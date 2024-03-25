# Mastodon Wiki Bot

Hosted at [@daily_wikipedia@tomkahe.com](https://tomkahe.com/@daily_wikipedia)

Provides a daily markdown formatted post with random events from this date in history on wikipedia along with a random wikipedia article.

![image](https://github.com/TomCasavant/wikibot/assets/7014115/3c371c26-5a0b-4c41-bf41-8ae2d5843995)


## Setup
1. Clone and cd into repository
2. (Optional, recommended) Setup a virtual environment (`python -m virtualenv .venv` and `source .venv/bin/activate`)
3. Install requirements.txt (`pip install -r requirements.txt`)
4. Copy config.toml.example to config.toml
5. Create mastodon credentials on your server (login to bot account -> settings -> Development -> Create New Application)
6. Copy server url and access token into config.toml
7. Configure wiki user agent and customize number of events/birts/deaths/holidays in config.toml
8. run the script with `python wiki.py`
9. (Optional) configure crontab, sample configuration: `0 18 * * * /home/tom/wiki-bot/.venv/bin/python /home/tom/wiki-bot/wiki.py` (runs every day at 6pm)

[![Follow @daily_wikipedia@tomkahe.com](https://fedi-badge.deno.dev/@daily_wikipedia@tomkahe.com/followers.svg?style=plastic)](https://tomkahe.com/@daily_wikipedia)
