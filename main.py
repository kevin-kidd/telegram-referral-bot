"""
Main entry point for the Telegram Referral Bot.

This script initializes the bot and starts the polling process.
It also ensures proper cleanup of database connections on exit.
"""

from src import bot
from src.db_setup import close_db_pool, init_db_pool
import atexit

if __name__ == "__main__":
    print("Connecting to database...")
    init_db_pool()
    print("Starting the bot...")
    # Register the database cleanup function to be called on exit
    atexit.register(close_db_pool)
    try:
        # Start the bot's polling process
        bot.infinity_polling()
    finally:
        # Ensure database connections are closed even if an exception occurs
        close_db_pool()
