"""
Integration tests for the Telegram Referral Bot.

This module contains integration tests that verify the interaction between
different components of the bot, including database operations and bot commands.

These tests use a real PostgreSQL database (in a Docker container) to ensure
that database operations work as expected in a production-like environment.

Each test function is decorated with @pytest.mark.integration to categorize
them as integration tests and allow selective test execution.
"""

import pytest
from unittest.mock import patch
from src import (
    send_welcome,
    create_code,
    CHANNEL_LINK,
    create_referral_code,
    grab_referral_code,
    check_ref,
    get_referral_amount,
    check_new_user,
)
from src.db_setup import (
    create_database,
    setup_database,
    close_db_pool,
    get_db_cursor,
    create_tables,
    init_db_pool,
)
import logging
import os

os.environ["TESTING"] = "True"

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def db_pool():
    """
    Create and manage a database connection pool for the entire test session.

    This fixture:
    1. Creates the test database
    2. Initializes the connection pool
    3. Yields control to the tests
    4. Closes the connection pool after all tests are complete

    Yields:
        None
    """
    create_database()
    init_db_pool()
    yield
    close_db_pool()


@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Set up a clean test database before each test and tear it down after.

    This fixture runs automatically for each test, ensuring a clean slate by:
    1. Dropping existing tables
    2. Creating new tables
    3. Cleaning up after the test

    Yields:
        None
    """
    logger.info("Setting up test database...")
    with get_db_cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS referrals, used_referrals")
    create_tables()
    yield
    logger.info("Tearing down test database...")
    with get_db_cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS referrals, used_referrals")


@pytest.fixture
def db_cursor():
    """
    Provide a database cursor for test operations.

    Yields:
        cursor: A database cursor for executing SQL commands.
    """
    with get_db_cursor() as cur:
        yield cur


class MockMessage:
    """
    A mock class to simulate Telegram message objects in tests.

    This class provides a simplified structure of a Telegram message,
    including nested classes for FromUser and Chat attributes.

    Attributes:
        text (str): The message text.
        message_id (int): A dummy message ID.
        from_user (FromUser): A mock user object.
        chat (Chat): A mock chat object.
    """

    def __init__(self, text, user_id, username):
        self.text = text
        self.message_id = 1
        self.from_user = self.FromUser(user_id, username)
        self.chat = self.Chat()

    class FromUser:
        """A mock class to simulate the 'from_user' attribute of a Telegram message."""

        def __init__(self, user_id, username):
            self.id = user_id
            self.username = username

    class Chat:
        """A mock class to simulate the 'chat' attribute of a Telegram message."""

        id = 456


@pytest.mark.integration
def test_create_tables_success(db_pool, caplog):
    caplog.set_level(logging.INFO)
    create_tables()
    assert "Tables created successfully." in caplog.text


@pytest.mark.integration
def test_create_tables_error(db_pool, caplog):
    caplog.set_level(logging.ERROR)
    with patch("src.db_setup.get_db_cursor") as mock_get_db_cursor:
        mock_get_db_cursor.side_effect = Exception("Test exception")
        create_tables()
    assert "Error creating tables: Test exception" in caplog.text


@pytest.mark.integration
def test_setup_database(db_pool, caplog):
    caplog.set_level(logging.INFO)
    with patch("src.db_setup.create_database") as mock_create_database, patch(
        "src.db_setup.init_db_pool"
    ) as mock_init_db_pool, patch("src.db_setup.create_tables") as mock_create_tables:
        setup_database()
        mock_create_database.assert_called_once()
        mock_init_db_pool.assert_called_once()
        mock_create_tables.assert_called_once()


@pytest.mark.integration
def test_close_db_pool_with_pool(db_pool, caplog):
    caplog.set_level(logging.INFO)
    close_db_pool()
    assert "Database connection pool closed." in caplog.text


@pytest.mark.integration
def test_close_db_pool_without_pool(caplog):
    caplog.set_level(logging.INFO)
    with patch("src.db_setup.db_pool", None):
        close_db_pool()
    assert "Database connection pool is already closed." in caplog.text


@pytest.mark.integration
def test_send_welcome_integration(db_cursor, caplog):
    """
    Test the integration of the send_welcome function.

    This test verifies:
    1. Creation of a referral code
    2. Proper handling of a new user using the referral link
    3. Correct increment of referral count
    4. Proper update of user status from new to existing

    Args:
        db_cursor: Pytest fixture providing a database cursor
        caplog: Pytest fixture for capturing log output
    """
    caplog.set_level(logging.DEBUG)

    # Clean up any existing data for this test
    db_cursor.execute("DELETE FROM referrals WHERE username = %s", ("referrer",))
    db_cursor.execute("DELETE FROM used_referrals WHERE user_id = %s", (123,))

    # Create a referral code for the referrer
    referrer_code = create_referral_code("referrer")
    assert referrer_code is not None, "Failed to create referral code for referrer"
    logger.debug(f"Created referral code for referrer: {referrer_code}")

    # Verify that the user is new before the welcome message
    assert check_new_user(123), "User should be new before welcome message"

    # Simulate a new user using the referral link
    message = MockMessage(f"/start {referrer_code}", 123, "newuser")

    with patch("src.bot.reply_to") as mock_reply_to:
        send_welcome(message)
        mock_reply_to.assert_called_once_with(
            message,
            f"Hello, you have been referred by: referrer\nPlease join the Telegram group by clicking this link: {CHANNEL_LINK}",
        )

    # Check that the referral count has been incremented
    referral_amount = get_referral_amount("referrer")
    assert (
        referral_amount == 1
    ), f"Expected referral count to be 1, but got {referral_amount}"

    # Verify that the user is no longer considered new after the welcome message
    assert not check_new_user(123), "User should not be new after welcome message"

    # Clean up test data
    db_cursor.execute("DELETE FROM referrals WHERE username = %s", ("referrer",))
    db_cursor.execute("DELETE FROM used_referrals WHERE user_id = %s", (123,))


@pytest.mark.integration
def test_create_code_integration(db_cursor, caplog):
    """
    Test the integration of the create_code function.

    This test verifies:
    1. A new referral code can be created for a user
    2. The same code is returned if the user already has one
    3. The correct responses are sent to the user in both cases

    Args:
        db_cursor: Pytest fixture providing a database cursor
        caplog: Pytest fixture for capturing log output
    """
    caplog.set_level(logging.DEBUG)
    message = MockMessage("", 1, "testuser")

    db_cursor.execute("DELETE FROM referrals WHERE username = %s", ("testuser",))
    logger.debug("Deleted existing user (if any)")

    with patch("src.bot.reply_to") as mock_reply_to:
        create_code(message)

    unique_code = grab_referral_code("testuser")
    logger.debug(f"Retrieved unique_code: {unique_code}")

    assert unique_code is not None, "No referral code was created in the database"
    assert (
        len(unique_code) == 15
    ), f"Expected unique code length to be 15, but got {len(unique_code)}"

    expected_reply = f"Your referral link is:\n{CHANNEL_LINK}?start={unique_code}"
    mock_reply_to.assert_called_once_with(message, expected_reply)

    mock_reply_to.reset_mock()

    with patch("src.bot.reply_to") as mock_reply_to:
        create_code(message)

    expected_reply = f"You have already created a referral link! Your referral link is:\n{CHANNEL_LINK}?start={unique_code}"
    mock_reply_to.assert_called_once_with(message, expected_reply)

    db_cursor.execute("DELETE FROM referrals WHERE username = %s", ("testuser",))
    logger.debug("Cleaned up test data")


@pytest.mark.integration
def test_check_ref_integration(db_cursor, caplog):
    """
    Test the integration of the check_ref function.

    This test verifies that:
    1. A referral code can be created for a user.
    2. The check_ref function correctly retrieves and reports the referral amount.
    """
    caplog.set_level(logging.DEBUG)

    # Clean up any existing data for this test
    db_cursor.execute("DELETE FROM referrals WHERE username = %s", ("testuser",))

    message = MockMessage("", 123, "testuser")

    created_code = create_referral_code("testuser")
    logger.debug(f"Created referral code: {created_code}")

    grabbed_code = grab_referral_code("testuser")
    logger.debug(f"Grabbed referral code: {grabbed_code}")

    with patch("src.bot.reply_to") as mock_reply_to:
        check_ref(message)

    mock_reply_to.assert_called_once_with(message, "Referral amount: 0")

    # Clean up test data
    db_cursor.execute("DELETE FROM referrals WHERE username = %s", ("testuser",))


@pytest.mark.integration
def test_send_welcome_self_referral(db_cursor, caplog):
    """
    Test the integration of the send_welcome function with self-referral.

    This test verifies that:
    1. A referral code can be created for a user.
    2. The user cannot use their own referral code.
    """
    caplog.set_level(logging.DEBUG)

    # Create a referral code for the user
    referrer_code = create_referral_code("testuser")
    assert referrer_code is not None, "Failed to create referral code for testuser"
    logger.debug(f"Created referral code for testuser: {referrer_code}")

    # Simulate the user trying to use their own referral link
    message = MockMessage(f"/start {referrer_code}", 123, "testuser")

    with patch("src.bot.reply_to") as mock_reply_to:
        send_welcome(message)
        mock_reply_to.assert_called_once_with(
            message, "You can not use your own referral link!"
        )

    # Clean up test data
    db_cursor.execute("DELETE FROM referrals WHERE username = %s", ("testuser",))
    db_cursor.execute("DELETE FROM referrals WHERE username = %s", ("testuser",))
