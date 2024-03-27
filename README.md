# Jackett-Indexers.dlm
Download Station search modules for Jackett (https://github.com/Jackett/Jackett) - individual module per Jackett indexer.

The goal is to have the results displaying a correct Site column. And getting the results faster - per indexer, not all the info at a time.

![Synology Download Station Search BT results](/screenshots/Download-Station.png?raw=true "Synology Download Station Search BT results")

The code for each module is a slight variation of the original code from [dimitrov-adrian/jackett.dlm](https://github.com/dimitrov-adrian/jackett.dlm)


## Installation

![Synology Download Station BT Search configuration](/screenshots/BT-Search-Settings.png?raw=true "Synology Download Station BT Search configuration")

1. Check - WORKING AND ACCESSIBLE JACKETT INSTANCE. Configure some Indexers there. For example: AniLibria

2. Download respective modules from [dlm folder](/dlm) for each indexer you'd like to use in Download Station. Example: [dlm/Anilibria-Jackett.dlm](/dlm/Anilibria-Jackett.dlm)

3. Install and enable to your Download Station -> Settings -> BT Search -> Add

4. Enable Jackett and edit settings.

5. Use your jackett instance **host as username**, and **api key as password**
> Example: If your Jackett instance is accessible via *http://192.168.0.1:9117/UI/Dashboard*,
> then the username is **192.168.0.1:9117**

6. It is a good idea to click "Verify" after setting up host and API key.

7. Click OK

![Synology Download Station Search BT results](/screenshots/Edit-AniLibria.png?raw=true "Synology Download Station Search BT results")


## Compatibility

Tested on Synology DSM 6.1-6.2 and 7.2.1


## Building

(optional) Download and replace `indexers.json` from your Jackett instance: http://your_jackett_server/api/v2.0/indexers

Call the `generate.py` - it will create/update the [dlm](/dlm) folder for you.

```bash
python3 generate.py
```
