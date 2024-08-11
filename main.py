# main.py

from src import bot
from src.db_setup import close_db_pool
import atexit

if __name__ == "__main__":
    print("Starting the bot...")
    atexit.register(close_db_pool)
    try:
        bot.infinity_polling()
    finally:
        close_db_pool()
