# 🔔 Real-Time Job Alerts – Woolworths & ALDI via Telegram

This Python-based Telegram bot continuously monitors job listings from Woolworths and ALDI career portals, filters out duplicates using `.json` trackers, and sends real-time alerts to multiple users via Telegram.

---

## 🧰 Features

- ✅ Scrapes jobs from both Woolworths and ALDI
- ✅ Sends personalized Telegram alerts (name, location, radius)
- ✅ JSON-based job tracking to avoid duplicate alerts
- ✅ Runs continuously on EC2 using `systemd`
- ✅ Simple config with multiple users and locations

---

## ⚙️ Requirements

- Python 3.x
- `requests`
- `beautifulsoup4`
- Telegram bot token (via BotFather)

To install:

```bash
pip install --user requests beautifulsoup4
