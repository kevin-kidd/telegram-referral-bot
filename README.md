# Telegram Referral Bot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/kevin-kidd/telegram-referral-bot/actions/workflows/main.yml/badge.svg)](https://github.com/kevin-kidd/telegram-referral-bot/actions/workflows/main.yml)

Boost your Telegram channel's growth with this powerful, user-friendly referral bot. It generates unique referral links and accurately tracks invites while preventing self-referrals. Built using Python and PostgreSQL, this bot is easy to set up and scales effortlessly for communities of any size.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Available Commands](#available-commands)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- Create unique referral links
- Track referral counts
- Prevent self-referrals
- Easy setup and configuration

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kevin-kidd/telegram-referral-bot.git
   cd telegram-referral-bot
   ```

2. Set up the configuration as described in the [Configuration](#configuration) section.

3. Install the required packages:

   ```bash
   make install
   ```

4. Set up the database:

   ```bash
   make setup-db
   ```

5. Run the bot:

   ```bash
   make run
   ```

### Available Commands

- `/create` - Create a unique referral link
- `/check` - Check the number of referrals you have
- `/start <referral_code>` - Use a referral code to join the channel/group

## Configuration

This project uses environment variables for configuration. To set up your environment:

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file and replace the placeholder values with your actual configuration:

   - `BOT_TOKEN`: Your Telegram Bot Token
   - `CHANNEL_LINK`: The link to your Telegram channel or group
   - `DB_HOST`: PostgreSQL database host (default: localhost)
   - `DB_PORT`: PostgreSQL database port (default: 5432)
   - `DB_NAME`: PostgreSQL database name
   - `DB_USER`: PostgreSQL database user
   - `DB_PASSWORD`: PostgreSQL database password
   - `DEBUG`: Set to True for debug mode (default: False)

Make sure to keep your `.env` file secure and never commit it to version control.

## Development

To set up the development environment:

1. Install Docker and Docker Compose
2. Run `docker-compose up --build`

To run tests:

```bash
make test
```

To run the linter:

```bash
make lint
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
