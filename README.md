# Introduction
A simple bot to get Spotify's features in Telegram.

# Disclaimer
This code is developed for educational purposes only and no abuse of any services, either Github, Spotify, or Telegram is instended.

# How to
* Create a telegram bot using [@BotFather](https://t.me/BotFather) and get your bot API token.
* Create an Actions Secret called `TELEGRAM_BOT_TOKEN` and set the value as your bot API token.
* Make sure you've allowed `Read and Write Permission` to github actions before running the workflow.
* To avoid extended workflow run for free users and avoid abuse of services, `tg-bot.yml` is set out to cancel the workflow after a limited time. Adjust it under `timeout-minutes`, capped at 6 hours due to Github policies (360 minutes).
* Run the workflow and `/start` your Telegram bot.

# Running Locally
* Resources to run locally are available under [Releases](https://github.com/Surfboardv2ray/telegram-spotbot/releases).
* Install dependencies via `requirements.txt`.
* Edit `tg-bot.py` and replace `YOUR_BOT_TOKEN` with your bot API Token.
* Run the script and `/start` your Telegram bot.
