# 🤖 Berzerk Outlet Monitor Bot

I wanted to ensure I never missed a deal at the [Berzerk Outlet](https://berzerk.com.br/collections/outlet), so I built this bot. It monitors the outlet page and sends me a Telegram notification whenever a new product is added, a price changes, or an item is removed.

## ✨ Key Features

- **Instant Notifications:** Get Telegram alerts as soon as a promotion drops.
- **New Product Detection:** Be the first to know when a new item enters the outlet.
- **Price Change Alerts:** The bot tracks if a price has increased or decreased.
- **Removal Detection:** Know immediately when a product is sold out or removed from the page.
- **Persistent Memory:** The bot remembers seen products (using a `json` file) to prevent duplicate notifications.
- **Flexible Scheduling:** Runs automatically at defined intervals.
- **Resilience:** The script is designed to handle connection errors without losing its database.

## 🛠️ Built With

- [Python](https://www.python.org/)
- [Requests](https://docs.python-requests.org/en/latest/) - For HTTP requests and fetching page content.
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - For parsing HTML and web scraping.
- [python-telegram-bot](https://python-telegram-bot.org/) - For sending notifications to Telegram.
- [Schedule](https://schedule.readthedocs.io/en/stable/) - For scheduling the monitoring jobs.

## ⚙️ Setup and Installation

Follow these steps to get the bot running.

### 1. Prerequisites

- Python 3.6 or higher.
- A Telegram Bot and its credentials:
    1.  Talk to [@BotFather](https://t.me/BotFather) on Telegram.
    2.  Create a new bot with `/newbot`.
    3.  Save the **API Token**.
- Your Telegram Chat ID:
    1.  Talk to [@userinfobot](https://t.me/userinfobot).
    2.  It will provide your **Chat ID**.

### 2. Clone the Repository

```bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
```

### 3\. Install Dependencies

It is highly recommended to use a virtual environment (venv).

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install libraries
pip install -r requirements.txt
```

### 4\. Configure Credentials

Open the `main.py` file and update the following lines with your credentials:

```python
# YOUR BOT_TOKEN AND CHAT_ID
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" 
CHAT_ID = "YOUR_CHAT_ID_HERE"
```

## 🚀 How to Run

Once configured, simply start the script from your terminal:

```bash
python main.py
```

You will see a message indicating the first check has run and the schedule is set. The bot will now check automatically every 2 to 5 minutes.

## 📂 Project Structure

  - **`main.py`**: The core logic for scraping, comparison, and notifications.
  - **`monitored_products.json`**: Automatically created on the first run. Acts as the bot's "memory," storing found products and prices. **Do not delete this** unless you want to reset the monitoring history.

## 🤝 Contributions

Contributions are welcome\! Feel free to open an *issue* or submit a *pull request*.

-----