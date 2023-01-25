import os
import requests
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from pyarr import RadarrAPI
from discordwebhook import Discord


class TMDB_API:
    def __init__(self, host, token) -> None:
        self.host = host
        self.token = token

    def get_watch_providers(self, movie_id: int) -> requests.Response:
        return requests.get(
            self.host
            + "/movie/"
            + str(movie_id)
            + "/watch/providers?api_key="
            + self.token
            + "&language=en-US"
        )


def post_to_discord(data: dict, webhook: str, microbin_url: str) -> None:
    discord: Discord = Discord(url=webhook)

    # Setup Footer
    full_results: str = ""
    if microbin_url != "":
        # Place microbin data
        full_results = f"Full data available [here]({microbin_url})."

    # Fields
    subs_we_care_about = (
        "Stan",
        "Netflix",
        "BINGE",
        "Foxtel Now",
        "Amazon Prime Video",
        "Disney Plus",
        "Paramount Plus",
    )
    fields: list = []
    for sub_name in data.keys():
        if sub_name not in subs_we_care_about:
            continue
        fields.append(
            {
                "name": sub_name,
                "value": str(
                    f"{data[sub_name]['count']} movies found! ({round(data[sub_name]['GB'], 2)}GB)"
                ),
            }
        )

    # Post!
    discord.post(
        embeds=[
            {
                "title": "Streaming Check",
                "description": str(
                    f"Checking the TMDB, you contain media that overlap streaming platforms. {full_results}"
                ),
                "fields": fields,
            }
        ]
    )


def post_to_microbin(data: dict, url: str) -> str:
    params_payload: dict = {
        "expiration": "1week",
        "syntax-highlight": "json",
    }
    files: dict = {
        "content": ("files.json", json.dumps(data, sort_keys=True, indent=4))
    }
    response: requests.Response = requests.post(
        url=url, data=params_payload, files=files, allow_redirects=False
    )
    return response.headers["location"]


def main():
    load_dotenv()

    # Get Env
    RADARR_TOKEN = os.getenv("RADARR_API_KEY", "")
    TMDB_TOKEN = os.getenv("TMDB_API_KEY", "")
    RADARR_URL = os.getenv("RADARR_HOST_URL", "")
    TMDB_URL = os.getenv("TMDB_HOST_URL", "")
    STREAM_REGION = os.getenv("STREAM_REGION", "AU")
    DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")
    DISCORD_ENABLED = os.getenv("DISCORD_ENABLED", "TRUE") == "TRUE"
    SAVE_ENABLED = os.getenv("SAVE_ENABLE", "TRUE") == "TRUE"
    MICROBIN_ENABLED = os.getenv("MICROBIN_ENABLED", "TRUE") == "TRUE"
    MICROBIN_URL = os.getenv("MICROBIN_URL", "")

    # Setup APIs
    radarr = RadarrAPI(RADARR_URL, RADARR_TOKEN)
    tmdb = TMDB_API(TMDB_URL, TMDB_TOKEN)

    # Query all movies
    movies: list = radarr.get_movie()
    movies_size = len(movies)
    print(f"Movies found: {movies_size}")

    # Get data
    data = {}
    count = 0
    for movie in movies:
        count += 1
        # Search Movies
        id = movie["tmdbId"]
        response = tmdb.get_watch_providers(id)
        response_json = json.loads(response.text)["results"]

        print(f"({count}/{movies_size}) {movie['title']}")

        if "AU" not in response_json:
            continue
        au_providers = json.loads(response.text)["results"][STREAM_REGION]

        if "flatrate" in au_providers:
            # Add all providers to master list
            for provider in au_providers["flatrate"]:
                if provider["provider_name"] in data:
                    data[provider["provider_name"]]["count"] += 1
                else:
                    data[provider["provider_name"]] = {}
                    data[provider["provider_name"]]["GB"] = 0
                    data[provider["provider_name"]]["count"] = 1

                # Add to provider file data size (Convert bytes to gigabytes)
                data[provider["provider_name"]]["GB"] += round(
                    (int(movie["sizeOnDisk"]) / (1 << 30)), 2
                )

    # Save Data
    if SAVE_ENABLED:
        with open(
            f"streaming_providers_report_{datetime.now(timezone.utc).astimezone().strftime('%Y_%m_%d_%H_%M_%S')}.json",
            "w",
        ) as file:
            file.write(json.dumps(data, sort_keys=True, indent=4))

    posted_url = ""
    if MICROBIN_ENABLED:
        posted_url = post_to_microbin(data=data, url=MICROBIN_URL)

    # Discord Webhook
    if DISCORD_ENABLED:
        post_to_discord(data=data, webhook=DISCORD_WEBHOOK, microbin_url=posted_url)


if __name__ == "__main__":
    main()
