import os
import subprocess
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

last_input_time = time.time()

# Function to handle user input
def handle_user_input(update: Update, context: CallbackContext) -> None:
    global last_input_time
    user_input = update.message.text
    user = update.message.from_user
    logger.info(f"User {user.first_name} sent: {user_input}")
    last_input_time = time.time()  # Update last input time

    # Check if the input is a Spotify URL
    if user_input.startswith("https://open.spotify.com/"):
        # If it's a Spotify link, proceed with downloading
        download_spotify_link(update, user_input)
    else:
        # If it's not a Spotify link, treat it as a search query
        search_spotify(update, user_input)

# Function to search for songs on Spotify
def search_spotify(update: Update, query: str) -> None:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv('SPOTIFY_CLIENT_ID'), client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')))
    results = sp.search(q=query, limit=10, type='track')
    if results['tracks']['items']:
        keyboard = []
        for i, track in enumerate(results['tracks']['items']):
            keyboard.append([InlineKeyboardButton(f"{track['name']} - {', '.join([artist['name'] for artist in track['artists']])}", callback_data=f"track_{i}_{track['external_urls']['spotify']}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose a song:', reply_markup=reply_markup)
    else:
        update.message.reply_text('No results found.')

# Function to handle callback queries from inline keyboards
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    choice, spotify_link = query.data.split('_')[1:]
    if spotify_link.startswith("https://open.spotify.com/"):
        # If it's a Spotify link, proceed with downloading from Spotify
        download_spotify_link(update, spotify_link)
    else:
        # If it's not a Spotify link, try searching for the song on YouTube
        search_youtube(update, choice)

# Function to search for the song on YouTube and download it
def search_youtube(update: Update, query: str) -> None:
    results = YoutubeSearch(query, max_results=1).to_dict()
    if results:
        youtube_link = f"https://www.youtube.com/watch?v={results[0]['id']}"
        download_youtube_video(update, youtube_link)
    else:
        update.message.reply_text("Couldn't find the song on YouTube.")

# Function to download the song(s) from a YouTube link
def download_youtube_video(update: Update, youtube_link: str) -> None:
    update.message.reply_text('Downloading your song from YouTube...')

    # Download the video as audio
    result = subprocess.run(['youtube-dl', '-x', '--audio-format', 'mp3', '-o', '%(title)s.%(ext)s', youtube_link], capture_output=True, text=True)
    logger.info(f"youtube-dl command output: {result.stdout}")
    if result.returncode == 0:
        # Find the downloaded audio file
        audio_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
        if audio_files:
            # Send the downloaded audio file back to the user
            update.message.reply_audio(audio=open(audio_files[0], 'rb'))
        else:
            update.message.reply_text('Could not find the downloaded audio file.')
    else:
        logger.error(f"Error downloading video from YouTube: {result.stderr}")
        update.message.reply_text('Failed to download the song from YouTube. Please try again later.')

# Function to download the song(s) from a Spotify link
def download_spotify_link(update: Update, spotify_link: str) -> None:
    message = update.message or update.callback_query.message
    if not message:
        logger.error("Cannot determine message to reply to.")
        return

    # Clear the directory of previously downloaded files
    for file in os.listdir('.'):
        if file.endswith('.mp3'):
            os.remove(file)

    message.reply_text('Downloading your song or songs...')

    # Download the song(s)
    result = subprocess.run(['spotdl', spotify_link], capture_output=True, text=True)
    logger.info(f"spotdl command output: {result.stdout}")
    if result.returncode != 0:
        logger.error(f"Error downloading song/album/playlist: {result.stderr}")
        # If there's an error, try searching for the song on YouTube
        search_youtube(update, spotify_link)
        return

    # Find the downloaded file/files
    song_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
    if song_files:
        # Send the downloaded song(s) back to the user
        for song_file in song_files:
            message.reply_audio(audio=open(song_file, 'rb'))
    else:
        message.reply_text('Could not find the downloaded song/album/playlist.')

# Function to stop the bot after a certain time of idle user input
# def check_idle_timeout(context: CallbackContext):
#     global last_input_time
#     current_time = time.time()
#     idle_duration = current_time - last_input_time
#     if idle_duration > 600:  # Check every 600 secondes
#         logger.info("Bot idle timeout reached")
#         updater.stop()  # Stop the updater when idle timeout is reached

# Main function to start the bot
def main() -> None:
    # Create the Updater and pass it your bot's token
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_input))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Schedule the check_idle_timeout function to run every 600 seconds
    # updater.job_queue.run_repeating(check_idle_timeout, interval=600, first=0)
    
    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM, or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
