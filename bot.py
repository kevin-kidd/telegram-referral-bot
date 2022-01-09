import telebot
import psycopg2
import random
import string

bot = telebot.TeleBot('<token>', threaded=False)

conn = psycopg2.connect(
    host="<host-address>",
    database="<db-name>",
    user="<db-user>",
    password="<db-password>")

cur = conn.cursor()


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None


def get_username_from_storage(unique_code):
    cur.execute(
        """
        SELECT username
        FROM referrals
        WHERE unique_code = %s;
        """,
        [unique_code]
    )
    result = cur.fetchone()
    return result


def grab_referral_code(sender_username):
    cur.execute(
        """
        SELECT unique_code
        FROM referrals
        WHERE username = %s;
        """,
        [sender_username]
    )
    result = cur.fetchone()
    return result


def create_unique_code():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(15))


def create_referral_code(sender_username):
    unique_code = create_unique_code()
    cur.execute(
        """
        INSERT INTO referrals
        (username, unique_code)
        VALUES(%s, %s)
        """,
        [sender_username, unique_code]
    )
    conn.commit()
    return unique_code


def add_user(sender_user_id):
    cur.execute(
        """
        INSERT INTO used_referrals
        (user_id)
        VALUES(%s)
        """,
        [sender_user_id]
    )
    conn.commit()
    pass


def increment_counter(username):
    cur.execute("UPDATE referrals set count = count + 1 WHERE username = %s", [username])
    conn.commit()
    pass


def check_new_user(sender_user_id):
    cur.execute(
        """
        SELECT *
        FROM used_referrals
        WHERE user_id = %s;
        """,
        [sender_user_id]
    )
    result = cur.fetchone()
    if result is None:
        return True
    return False


def check_user_exists(sender_username):
    cur.execute(
        """
        SELECT *
        FROM referrals
        WHERE username = %s;
        """,
        [sender_username]
    )
    result = cur.fetchone()
    if result is None:
        return False
    return True


def check_referrals(sender_username):
    cur.execute(
        """
        SELECT count
        FROM referrals
        WHERE username = %s;
        """,
        [sender_username]
    )
    result = cur.fetchone()
    return result[0]


@bot.message_handler(commands=['start'])
def send_welcome(message):
    unique_code = extract_unique_code(message.text)
    if unique_code:  # if the '/start' command contains a unique_code
        sender_user_id = str(message.from_user.id)
        username = get_username_from_storage(unique_code)
        if username[0] == message.from_user.username:
            bot.reply_to(message, "You can not use your own referral link!")
            return
        if username:  # if the username exists in the database
            if check_new_user(sender_user_id):
                increment_counter(username[0])
                add_user(sender_user_id)
                reply = "Hello, you have been referred by: " + username[0] + "\nPlease join the Telegram group by " \
                                                                             "clicking this link: <channel-link>"
            else:
                reply = "Hello, you have already been referred by someone else! \nPlease join the Telegram group by " \
                        "clicking this link: <channel-link>"
        else:
            reply = "Your referral code is invalid. \nPlease join the Telegram group by clicking this link: " \
                    "<channel-link> "
    else:
        reply = "You did not input a referral code!\nPlease join the Telegram group by clicking this link: " \
                    "<channel-link>"
    bot.reply_to(message, reply)


@bot.message_handler(commands=['create'])
def create_code(message):
    sender_username = message.from_user.username
    if not sender_username:
        bot.reply_to(message, "You do not have a Telegram username! Please create one in the Telegram settings.")
        return
    check_user = check_user_exists(sender_username)
    if check_user:  # if the username exists in the database
        referral_code = grab_referral_code(sender_username)
        reply = "You have already created a referral link! Your referral link is:\n<channel-link>?start=" + referral_code[0]
    else:
        referral_code = create_referral_code(sender_username)
        reply = "Your referral link is:\n<channel-link>?start=" + referral_code
    bot.reply_to(message, reply)


@bot.message_handler(commands=['check'])
def check_ref(message):
    sender_username = message.chat.username
    check_user = check_user_exists(sender_username)
    if check_user:  # if the username exists in the database
        referral_amount = check_referrals(sender_username)
        reply = "Referral amount: " + str(referral_amount)
    else:
        reply = "You do not have a referral code! Please create one using /create"
    bot.reply_to(message, reply)

bot.infinity_polling()
