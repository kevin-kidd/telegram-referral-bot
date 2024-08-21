"""
Unit tests for the Telegram Referral Bot.

This module contains unit tests for individual functions and components of the bot.
It uses mocking to isolate the tested components from external dependencies.

Each test function is focused on a specific functionality and uses appropriate
fixtures and mocks to create a controlled testing environment.
"""

import pytest
from unittest.mock import patch, MagicMock
from src import (
    extract_unique_code,
    get_username_from_storage,
    grab_referral_code,
    create_referral_code,
    add_user,
    increment_counter,
    check_new_user,
    get_referral_amount,
    send_welcome,
    create_code,
    check_ref,
    CHANNEL_LINK,
)


@pytest.fixture
def mock_message():
    """
    Create a mock Telegram message for testing.

    Returns:
        MagicMock: A mock object simulating a Telegram message.
    """
    message = MagicMock()
    message.from_user.id = 123
    message.from_user.username = "testuser"
    return message


def test_extract_unique_code():
    """
    Test the extract_unique_code function with various inputs.

    This test verifies that the function correctly extracts the unique code
    from a valid /start command, and returns None for invalid inputs.
    """
    assert extract_unique_code("/start abc123") == "abc123"
    assert extract_unique_code("/start") is None
    assert extract_unique_code("hello world") is None


@patch("src.get_db_connection")
def test_get_username_from_storage(mock_get_db_connection):
    """
    Test the get_username_from_storage function with mocked database connection.

    This test verifies that the function correctly retrieves a username for a given
    unique code and returns None for non-existent codes.

    Args:
        mock_get_db_connection: A mocked database connection.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("testuser",)
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    assert get_username_from_storage("abc123") == "testuser"

    mock_cursor.fetchone.return_value = None
    assert get_username_from_storage("nonexistent") is None


@patch("src.get_db_connection")
def test_grab_referral_code(mock_get_db_connection):
    """
    Test the grab_referral_code function with mocked database connection.

    This test verifies that the function correctly retrieves a referral code for a given
    username and returns None for non-existent usernames.

    Args:
        mock_get_db_connection: A mocked database connection.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("abc123",)
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    assert grab_referral_code("testuser") == "abc123"

    mock_cursor.fetchone.return_value = None
    assert grab_referral_code("nonexistent") is None


@patch("src.get_db_connection")
@patch("src.create_unique_code")
def test_create_referral_code(mock_create_unique_code, mock_get_db_connection):
    """
    Test the create_referral_code function with mocked database connection and unique code generation.

    This test verifies that the function correctly creates and returns a new referral code.

    Args:
        mock_create_unique_code: A mocked function for creating unique codes.
        mock_get_db_connection: A mocked database connection.
    """
    mock_create_unique_code.return_value = "abc123"
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("abc123",)
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    assert create_referral_code("testuser") == "abc123"


@patch("src.get_db_connection")
def test_add_user(mock_get_db_connection):
    """
    Test the add_user function with mocked database connection.

    This test verifies that the function correctly adds a user and returns True.

    Args:
        mock_get_db_connection: A mocked database connection.
    """
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    assert add_user(123) is True


@patch("src.get_db_connection")
def test_increment_counter(mock_get_db_connection):
    """
    Test the increment_counter function with mocked database connection.

    This test verifies that the function correctly increments the counter and returns True.

    Args:
        mock_get_db_connection: A mocked database connection.
    """
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    assert increment_counter("testuser") is True


@patch("src.get_db_connection")
def test_check_new_user(mock_get_db_connection):
    """
    Test the check_new_user function with mocked database connection.

    This test verifies that the function correctly identifies new and existing users.

    Args:
        mock_get_db_connection: A mocked database connection.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    assert check_new_user(123) is True

    mock_cursor.fetchone.return_value = (123,)
    assert check_new_user(123) is False


@patch("src.get_db_connection")
def test_get_referral_amount(mock_get_db_connection):
    """
    Test the get_referral_amount function with mocked database connection.

    This test verifies that the function correctly retrieves referral amounts for
    existing users and returns 0 for non-existent users.

    Args:
        mock_get_db_connection: A mocked database connection.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (5,)
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    assert get_referral_amount("testuser") == 5

    mock_cursor.fetchone.return_value = None
    assert get_referral_amount("nonexistent") == 0


@patch("src.bot.reply_to")
@patch("src.get_username_from_storage")
@patch("src.check_new_user")
@patch("src.increment_counter")
@patch("src.add_user")
def test_send_welcome(
    mock_add_user,
    mock_increment_counter,
    mock_check_new_user,
    mock_get_username_from_storage,
    mock_reply_to,
    mock_message,
):
    """
    Test the send_welcome function for various scenarios.

    Verifies correct handling of valid referrals, self-referrals,
    and cases without referral codes.

    Args:
        mock_add_user, mock_increment_counter, mock_check_new_user,
        mock_get_username_from_storage, mock_reply_to: Mocked functions.
        mock_message: Fixture providing a mock message object.
    """
    # Test case: Valid referral
    mock_message.from_user.username = "testuser"  # Reset username
    mock_message.text = "/start abc123"
    mock_get_username_from_storage.return_value = "referrer"
    mock_check_new_user.return_value = True
    mock_increment_counter.return_value = True
    mock_add_user.return_value = True

    send_welcome(mock_message)

    mock_reply_to.assert_called_once_with(
        mock_message,
        f"Hello, you have been referred by: referrer\nPlease join the Telegram group by clicking this link: {CHANNEL_LINK}",
    )

    # Test case: Self-referral
    mock_message.from_user.username = "referrer"  # Set username for self-referral
    mock_message.text = "/start abc123"
    mock_get_username_from_storage.return_value = "referrer"

    send_welcome(mock_message)

    mock_reply_to.assert_called_with(
        mock_message, "You can not use your own referral link!"
    )

    # Test case: No referral code
    mock_message.from_user.username = "testuser"  # Reset username
    mock_message.text = "/start"
    send_welcome(mock_message)

    mock_reply_to.assert_called_with(
        mock_message,
        f"You did not input a referral code!\nPlease join the Telegram group by clicking this link: {CHANNEL_LINK}",
    )


@patch("src.bot.reply_to")
@patch("src.grab_referral_code")
@patch("src.create_referral_code")
def test_create_code(
    mock_create_referral_code, mock_grab_referral_code, mock_reply_to, mock_message
):
    """
    Test the create_code function for different user scenarios.

    Verifies behavior for new referral code creation, existing code retrieval,
    and users without a username.

    Args:
        mock_create_referral_code, mock_grab_referral_code, mock_reply_to: Mocked functions.
        mock_message: Fixture providing a mock message object.
    """
    # Test case: New referral code
    mock_message.from_user.username = "testuser"
    mock_grab_referral_code.return_value = None
    mock_create_referral_code.return_value = "abc123"

    create_code(mock_message)

    mock_reply_to.assert_called_once_with(
        mock_message, f"Your referral link is:\n{CHANNEL_LINK}?start=abc123"
    )

    # Test case: Existing referral code
    mock_grab_referral_code.return_value = "existing123"

    create_code(mock_message)

    mock_reply_to.assert_called_with(
        mock_message,
        f"You have already created a referral link! Your referral link is:\n{CHANNEL_LINK}?start=existing123",
    )

    # Test case: No username
    mock_message.from_user.username = None

    create_code(mock_message)

    mock_reply_to.assert_called_with(
        mock_message,
        "You do not have a Telegram username! Please create one in the Telegram settings.",
    )


@patch("src.bot.reply_to")
@patch("src.check_user_exists")
@patch("src.get_referral_amount")
def test_check_ref(
    mock_get_referral_amount, mock_check_user_exists, mock_reply_to, mock_message
):
    """
    Test the check_ref function for users with and without referral codes.

    Verifies correct referral amount reporting and prompting for code creation.

    Args:
        mock_get_referral_amount, mock_check_user_exists, mock_reply_to: Mocked functions.
        mock_message: Fixture providing a mock message object.
    """
    # Test case: User has a referral code
    mock_message.from_user.username = "testuser"
    mock_check_user_exists.return_value = True
    mock_get_referral_amount.return_value = 5

    check_ref(mock_message)

    mock_reply_to.assert_called_once_with(mock_message, "Referral amount: 5")

    # Test case: User does not have a referral code
    mock_check_user_exists.return_value = False

    check_ref(mock_message)

    mock_reply_to.assert_called_with(
        mock_message, "You do not have a referral code! Please create one using /create"
    )
