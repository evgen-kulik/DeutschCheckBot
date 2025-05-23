---

````markdown
# 🇩🇪 DeutschCheckBot

**DeutschCheckBot** is a Telegram bot that checks whether a German language exam certificate (telc) has been issued based on provided credentials. It runs headlessly using [Playwright](https://playwright.dev/python/) and can be triggered manually via Telegram.

---

## 🚀 Features

- 🔍 Checks telc certificate availability at [results.telc.net](https://results.telc.net/)
- 🤖 Telegram bot integration with the `/check` command
- 🔐 Uses environment variables for secure data input
- ☁️ Ready to deploy on free platforms like [Render](https://render.com)

---

## 📦 Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management
- Playwright
- Telegram Bot token from [@BotFather](https://t.me/BotFather)

---

## 🛠️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/evgen-kulik/DeutschCheckBot.git
cd DeutschCheckBot
````

### 2. Install dependencies

```bash
poetry install
poetry run playwright install
```

### 3. Create a `.env` file

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
PARTICIPANT_NUMBER=your_telc_participant_number
DATE_OF_BIRTH=dd.mm.yyyy
DATE_OF_ISSUE=dd.mm.yyyy
RENDER_EXTERNAL_URL=your-app-name.onrender.com
```

### 4. Run the bot locally

```bash
poetry run python telegram_bot.py
```

---

## 🤖 Usage

Open Telegram, go to your bot, and send the command:

```
/check
```

The bot will respond with one of the following:

* ✅ Certificate found!
* ❌ Certificate not found.
* ⚠️ Parsing error (if the site structure has changed)

---

## ☁️ Deployment (Render example)

1. Push your project to a GitHub repository
2. Create a new **Web Service** on [Render](https://render.com/)
3. Connect your GitHub repo and configure:

   * Runtime: Python
   * Start command: `python telegram_bot.py`
   * Environment variables: use values from your `.env`
4. Deploy and watch the logs

---

## 📁 Project Structure

```
DeutschCheckBot/
├── check_cert.py         # Core scraping logic (no browser window)
├── telegram_bot.py       # Telegram bot entrypoint
├── .env                  # Environment variables (not committed to git)
├── requirements.txt      # Dependencies for Render
├── pyproject.toml        # Poetry configuration
└── README.md             # Project description
```
