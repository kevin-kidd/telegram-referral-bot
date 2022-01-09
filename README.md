# Telegram Referral Bot

A simple Telegram referral bot for tracking invites to your channel/group.

------------
#### Instructions:
- Replace <token> with your HTTP API Token from [BotFather](https://t.me/BotFather "BotFather").
- Create a table in your database called **referrals** with the following columns: **username**, **unique_code** and **count**.
- Create a table in your database called **used_referrals** with a column caled **user_id**.
- Fill in **psycopg2.connect()** with your database connection details.
- Edit the reply messages for each of the 3 commands.

------------
#### Usage:
- **/create** - Create a unique referral link
- **/check** - Check the amount of referrals you have
- **/start** - Accepts 1 argument with the referral code
------------
#### Credits:
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI "pyTelegramBotAPI")
