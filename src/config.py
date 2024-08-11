"""
Configuration module for the Telegram Referral Bot.

This module loads and validates environment variables, setting up the configuration
for both the bot and the database connection. It handles different configurations
for testing and production environments.
"""

import os
from dotenv import load_dotenv
import sys

# Check if we're in a testing environment
IS_TESTING = os.getenv("TESTING", "False").lower() in ("true", "1", "t")

# Load environment variables from .env file only if not testing
if not IS_TESTING:
    try:
        load_dotenv()
    except IOError:
        print(
            "Error: Unable to load .env file. Please ensure it exists and is readable."
        )
        sys.exit(1)

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

# Database configuration
if IS_TESTING:
    DB_HOST = os.getenv("DB_HOST", "localhost")  # Use localhost for local testing
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME", "test_db")
    DB_USER = os.getenv("DB_USER", "test_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "test_password")
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

# Debug mode
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t", "yes", "y")

# Validate required environment variables only if not in testing mode
if not IS_TESTING:
    required_vars = ["BOT_TOKEN", "CHANNEL_LINK", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing_vars = [var for var in required_vars if not globals()[var]]

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

"""
Configuration variables:

BOT_TOKEN: The Telegram Bot API token.
CHANNEL_LINK: The link to the Telegram channel associated with the bot.
DB_HOST: The hostname of the database server.
DB_PORT: The port number for the database connection.
DB_NAME: The name of the database.
DB_USER: The username for database authentication.
DB_PASSWORD: The password for database authentication.
DEBUG: A boolean flag to enable or disable debug mode.
IS_TESTING: A boolean flag indicating whether the application is running in a testing environment.

Environment variable handling:
- Variables are loaded from a .env file using dotenv.
- If the .env file can't be loaded, an error message is printed and the script exits.
- For production, all required variables must be set in the environment or .env file.
- In testing mode, some database variables have default values (not for production use).

Validation:
- Required variables are checked only when not in testing mode.
- A ValueError is raised if any required variables are missing in production.

Usage:
Import configuration variables in other modules like this:
from config import BOT_TOKEN, DB_NAME, DEBUG, etc.

Security note:
Keep the .env file and environment variables with sensitive information (like DB_PASSWORD and BOT_TOKEN)
 secure and unexposed in version control systems.
"""
