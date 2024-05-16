import os
import subprocess
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me a Spotify song URL to download. Developed by @Surfboardv2ray')

# Define message handler
def download_song(update: Update, context: CallbackContext) -> None:
    song_url = update.message.text
    user = update.message.from_user
    logger.info(f"User {user.first_name} sent URL: {song_url}")

    if not song_url.startswith("https://open.spotify.com/track/"):
        update.message.reply_text('Please send a valid Spotify track URL.')
        return

    update.message.reply_text('Downloading your song...')

    # Download the song
    result = subprocess.run(['spotdl', song_url], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Error downloading song: {result.stderr}")
        update.message.reply_text('Failed to download the song. Please try again later.')
        return

    # Find the downloaded file
    song_file = next((f for f in os.listdir('.') if f.endswith('.mp3')), None)
    if song_file:
        # Send the downloaded song back to the user
        update.message.reply_audio(audio=open(song_file, 'rb'))
        os.remove(song_file)
    else:
        update.message.reply_text('Could not find the downloaded song.')

# Main function to start the bot
def main() -> None:
    # Create the Updater and pass it your bot's token
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_song))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
