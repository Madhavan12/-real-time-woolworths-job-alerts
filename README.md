# Real-Time Woolworths Job Alerts

This Python script scrapes job postings from Woolworths' careers page and sends real-time job alerts to your Telegram account.

## Requirements
- Python 3.x
- requests
- BeautifulSoup
- python-telegram-bot

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/real-time-woolworths-job-alerts.git
    ```

2. Navigate to the project directory:
    ```bash
    cd real-time-woolworths-job-alerts
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

1. Set up a Telegram Bot using BotFather and get the `BOT_API_KEY` and `CHAT_ID`.
2. Add your credentials to the `job_alerts.py` script.
3. Run the script:
    ```bash
    python job_alerts.py
    ```
