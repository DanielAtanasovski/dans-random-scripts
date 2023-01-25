## Dans Random Scripts

Various little scripts for the random services that I've run or encountered.

### get_streaming_services_radarr

If you got a Radarr instance and want to know how much of your media exists on streaming platforms in your region? look no further!

You can output the results to a json file and / or send a webhook to discord and / or post the results to a local instance of [microbin](https://github.com/szabodanika/microbin).

To use this script, it depends on a couple of environment variables:

| Env variable    | Description                                            | Default Value |
| --------------- | ------------------------------------------------------ | ------------- |
| RADARR_API_KEY  | RADARR API auth token                                  | ""            |
| RADARR_HOST_URL | RADARR host url                                        | ""            |
| TMDB_API_KEY    | TMDB API auth Token                                    | ""            |
| TMDB_HOST_URL   | TMDB host URL                                          | ""            |
| DISCORD_WEBHOOK | Discord webhook URL                                    | ""            |
| DISCORD_ENABLE  | Enable sending results to discord                      | "TRUE"        |
| MICROBIN_URL    | Microbin service URL                                   | ""            |
| MICROBIN_ENABLE | Enable posting results to microbin                     | "TRUE"        |
| SAVE_ENABLE     | Enable saving results to a file                        | "TRUE"        |
| STREAM_REGION   | Region for streaming subscriptions (according to TMDB) | "AU"          |
