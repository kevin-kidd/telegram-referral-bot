"""
Telegram Referral Bot

This module contains the main functionality for the Telegram Referral Bot,
including database operations, message handling, and bot commands.
"""

import telebot
import random
import string
import logging
from typing import Optional
from .config import (
    BOT_TOKEN,
    CHANNEL_LINK,
    DEBUG,
)
from .db_setup import get_db_connection

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize the Telegram bot
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)


def extract_unique_code(text: str) -> Optional[str]:
    """
    Extract the unique code from the /start command message.

    Args:
        text (str): The message text.

    Returns:
        Optional[str]: The extracted unique code, or None if not found.
    """
    parts = text.split()
    if len(parts) > 1 and parts[0].lower() == "/start":
        return parts[1]
    return None


def get_username_from_storage(unique_code: str) -> Optional[str]:
    """
    Retrieve the username associated with a given unique code from the database.

    Args:
        unique_code (str): The unique referral code.

    Returns:
        Optional[str]: The associated username, or None if not found.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT username FROM referrals WHERE unique_code = %s",
                    (unique_code,),
                )
                result = cur.fetchone()
                logger.debug(f"get_username_from_storage result: {result}")
                return result[0] if result else None
    except Exception as e:
        logger.error(f"Error in get_username_from_storage: {e}")
        return None


def grab_referral_code(username: str) -> Optional[str]:
    """
    Retrieve the referral code for a given username from the database.

    Args:
        username (str): The username to look up.

    Returns:
        Optional[str]: The referral code, or None if not found.
    """
    logger.debug(f"Attempting to grab referral code for user: {username}")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT unique_code FROM referrals WHERE username = %s", (username,)
                )
                result = cur.fetchone()
                if result:
                    return result[0]
                else:
                    logger.debug(f"No referral code found for user: {username}")
                    return None
    except Exception as e:
        logger.error(f"Error in grab_referral_code: {e}")
        return None


def create_unique_code() -> str:
    """
    Generate a new unique referral code.

    Returns:
        str: A 15-character lowercase string.
    """
    return "".join(random.choice(string.ascii_lowercase) for _ in range(15))


def create_referral_code(sender_username: str) -> Optional[str]:
    """
    Create a new referral code for a user or retrieve an existing one.

    Args:
        sender_username (str): The username of the user requesting a code.

    Returns:
        Optional[str]: The new or existing referral code, or None if an error occurred.
    """
    logger.debug(f"Creating new referral code for {sender_username}")
    try:
        unique_code = create_unique_code()
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO referrals (username, unique_code, count) VALUES (%s, %s, 0) ON CONFLICT (username) DO NOTHING RETURNING unique_code",
                    (sender_username, unique_code),
                )
                result = cur.fetchone()
                if result:
                    logger.debug(
                        f"Successfully inserted code {unique_code} for user {sender_username}"
                    )
                    return unique_code
                else:
                    logger.debug(f"Code already exists for user {sender_username}")
                    return grab_referral_code(sender_username)
    except Exception as e:
        logger.error(f"Error in create_referral_code: {e}")
        return None


def add_user(sender_user_id: int) -> bool:
    """
    Add a user to the used_referrals table.

    Args:
        sender_user_id (int): The user ID to add.

    Returns:
        bool: True if the user was added successfully, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO used_referrals (user_id)
                    VALUES (%s)
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    (sender_user_id,),
                )
        return True
    except Exception as e:
        logger.error(f"Error in add_user: {e}")
        return False


def increment_counter(username: str) -> bool:
    """
    Increment the referral count for a given username.

    Args:
        username (str): The username whose referral count should be incremented.

    Returns:
        bool: True if the count was successfully incremented, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE referrals SET count = count + 1 WHERE username = %s",
                    (username,),
                )
                return cur.rowcount > 0
    except Exception as e:
        logger.error(f"Error incrementing counter: {e}")
        return False


def check_new_user(sender_user_id: int) -> bool:
    """
    Check if the user is new (not in the used_referrals table).

    Args:
        sender_user_id (int): The user ID to check.

    Returns:
        bool: True if the user is new, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT user_id
                    FROM used_referrals
                    WHERE user_id = %s;
                    """,
                    (sender_user_id,),
                )
                result = cur.fetchone()
                logger.debug(
                    f"check_new_user result for user_id {sender_user_id}: {result}"
                )
                return result is None
    except Exception as e:
        logger.error(f"Error in check_new_user: {e}")
        return False


def check_user_exists(sender_username: str) -> Optional[bool]:
    """
    Check if a user exists in the referrals table.

    Args:
        sender_username (str): The username to check.

    Returns:
        Optional[bool]: True if the user exists, False if not, None if an error occurred.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM referrals WHERE username = %s;", (sender_username,)
                )
                return cur.fetchone() is not None
    except Exception as e:
        logger.error(f"Error in check_user_exists: {e}")
        return None


def get_referral_amount(username: str) -> int:
    """
    Get the referral count for a given username.

    Args:
        username (str): The username to look up.

    Returns:
        int: The referral count for the user, or 0 if not found or an error occurred.
    """
    logger.debug(f"Getting referral count for user: {username}")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT count FROM referrals WHERE username = %s", (username,)
                )
                result = cur.fetchone()
                if result:
                    return result[0]
                else:
                    logger.debug(f"No referral count found for user: {username}")
                    return 0
    except Exception as e:
        logger.error(f"Error in get_referral_amount: {e}")
        return 0


@bot.message_handler(commands=["start"])
def send_welcome(message):
    """
    Handle the /start command, process referral links, and send a welcome message.

    This function extracts the unique code from the message, checks if it's a valid
    referral, and updates the database accordingly.

    Args:
        message (telebot.types.Message): The incoming Telegram message.
    """
    unique_code = extract_unique_code(message.text)
    user_id = message.from_user.id
    username = message.from_user.username

    logger.debug(
        f"Received welcome message. User ID: {user_id}, Username: {username}, Unique code: {unique_code}"
    )

    if unique_code:
        referrer_username = get_username_from_storage(unique_code)
        logger.debug(f"Referrer username: {referrer_username}")

        if referrer_username == username:
            bot.reply_to(message, "You can not use your own referral link!")
            return

        if referrer_username and check_new_user(user_id):
            logger.debug(
                f"New user detected. Incrementing counter for {referrer_username}"
            )
            increment_result = increment_counter(referrer_username)
            logger.debug(f"Increment result: {increment_result}")
            add_user_result = add_user(user_id)
            logger.debug(f"Add user result: {add_user_result}")
            bot.reply_to(
                message,
                f"Hello, you have been referred by: {referrer_username}\nPlease join the Telegram group by clicking this link: {CHANNEL_LINK}",
            )
        elif referrer_username:
            bot.reply_to(
                message,
                f"Hello, you have already been referred by someone else!\nPlease join the Telegram group by clicking this link: {CHANNEL_LINK}",
            )
        else:
            bot.reply_to(
                message,
                f"Your referral code is invalid.\nPlease join the Telegram group by clicking this link: {CHANNEL_LINK}",
            )
    else:
        bot.reply_to(
            message,
            f"You did not input a referral code!\nPlease join the Telegram group by clicking this link: {CHANNEL_LINK}",
        )


@bot.message_handler(commands=["create"])
def create_code(message):
    """
    Handle the /create command to generate a new referral code or retrieve an existing one.

    Args:
        message (telebot.types.Message): The incoming Telegram message.
    """
    sender_username = message.from_user.username
    logger.debug(f"Creating code for user: {sender_username}")

    if not sender_username:
        bot.reply_to(
            message,
            "You do not have a Telegram username! Please create one in the Telegram settings.",
        )
        return

    # First, try to get an existing code
    existing_code = grab_referral_code(sender_username)
    if existing_code:
        reply = f"You have already created a referral link! Your referral link is:\n{CHANNEL_LINK}?start={existing_code}"
        bot.reply_to(message, reply)
        return

    # If no existing code, create a new one
    unique_code = create_referral_code(sender_username)
    if unique_code:
        reply = f"Your referral link is:\n{CHANNEL_LINK}?start={unique_code}"
    else:
        reply = "An error occurred. Please try again later."

    bot.reply_to(message, reply)


@bot.message_handler(commands=["check"])
def check_ref(message):
    """
    Handle the /check command to retrieve and display the user's referral count.

    Args:
        message (telebot.types.Message): The incoming Telegram message.
    """
    username = message.from_user.username
    logger.debug(f"Checking referral for user: {username}")

    user_exists = check_user_exists(username)
    if user_exists is None:
        bot.reply_to(message, "An error occurred. Please try again later.")
        return
    if not user_exists:
        bot.reply_to(
            message, "You do not have a referral code! Please create one using /create"
        )
        return

    referral_amount = get_referral_amount(username)
    logger.debug(f"Retrieved referral amount: {referral_amount}")
    reply = f"Referral amount: {referral_amount}"
    bot.reply_to(message, reply)


if __name__ == "__main__":
    bot.infinity_polling()
