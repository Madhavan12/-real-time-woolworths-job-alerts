# ✅ Unified Job Notifier for Both Woolworths and ALDI
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

# 🔐 Telegram bot token
bot_token = "7837144647:AAEpyx-Z5h7Fs0Xf0yNmfHc9dUWh9fEfO9c"

# 🧹 Markdown Escape for Telegram
def escape_markdown(text):
    return re.sub(r'([_\*\[\]\(\)~`>#+=|{}.!])', r'\\\1', text)

# 📩 Send Telegram Notification
def send_telegram_notification(message, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"[{datetime.now()}] ✅ Telegram sent to {chat_id}", flush=True)
    else:
        print(f"[{datetime.now()}] ❌ Failed to send Telegram to {chat_id}. Status: {response.status_code}", flush=True)

# 🔁 Load/Save Seen REQ IDs
def load_seen_req_ids(file_name):
    try:
        with open(file_name, 'r') as f:
            return set(json.load(f).get('seen_req_ids', []))
    except:
        return set()

def save_seen_req_ids(req_ids, file_name):
    with open(file_name, 'w') as f:
        json.dump({'seen_req_ids': list(req_ids)}, f)

# 🛒 ALDI Job Scraper
def get_aldi_job_postings(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[{datetime.now()}] ❌ ALDI page failed ({response.status_code}): {url}", flush=True)
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        job_posts = soup.find_all('div', class_='attrax-vacancy-tile')
        job_list = []
        for job in job_posts:
            try:
                title_tag = job.find('a', class_='attrax-vacancy-tile__title')
                job_title = title_tag.get_text(strip=True)
                job_link = "https://www.aldicareers.com.au" + title_tag['href']
                location = job.find('div', class_='attrax-vacancy-tile__location-freetext')
                job_location = location.find('p', class_='attrax-vacancy-tile__item-value').get_text(strip=True)
                ref_tag = job.find('p', class_='attrax-vacancy-tile__externalreference-value')
                req_id = ref_tag.get_text(strip=True) if ref_tag else title_tag['href'].split("-")[-1]
                job_list.append((job_title, job_link, req_id, job_location))
            except Exception as e:
                print(f"⚠️ Error parsing ALDI job: {e}", flush=True)
        return job_list
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] ❌ Request failed: {e}", flush=True)
        return []

# 🛒 Woolworths Job Scraper
def get_woolworths_job_postings(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"[{datetime.now()}] ❌ Woolies page failed ({response.status_code}): {url}", flush=True)
            return []
        soup = BeautifulSoup(response.content, 'html.parser')
        job_posts = soup.find_all('article', class_='article article--w--full article--result')
        job_list = []
        for job in job_posts:
            try:
                title = job.find('h3', class_='article__header__text__title').get_text(strip=True)
                date_posted = job.find('span', class_='list-item-posted').get_text(strip=True)
                req_id = job.find('span', class_='list-item-ref').get_text(strip=True).replace('REQ ID', '').strip()
                location = job.find('span', class_='list-item-location').get_text(strip=True)
                job_list.append((title, date_posted, req_id, location))
            except Exception as e:
                print(f"⚠️ Error parsing Woolworths job: {e}", flush=True)
        return job_list
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] ❌ Request failed: {e}", flush=True)
        return []

# 🗂 Configurations
aldi_configs = [
    {
        "url": "https://www.aldicareers.com.au/jobs?options=2229,45&page=1&ln=Essendon%20VIC%203040,%20Australia&la=-37.7527648&lo=144.9160333&lr=8&li=",
        "seen_file": "seen_aldi_Essendon.json",
        "chat_ids": [{
        "id": "7021757983",
        "name": "Madhavan",
        "location": "Essendon",
        "radius": "8km"
    },
    {
        "id": "649377103",
        "name": "Mahe",
        "location": "Essendon",
        "radius": "8km"
    }]

    },
    {
        "url": "https://www.aldicareers.com.au/jobs?options=2229,45&page=1&ln=Melbourne%20VIC,%20Australia&la=-37.8136276&lo=144.9630576&lr=20&li=",
        "seen_file": "seen_aldi_Melbourne.json",
        "chat_ids": [{
        "id": "7021757983",
        "name": "Madhavan",
        "location": "Melbourne",
        "radius": "20km"
    },
    {
        "id": "649377103",
        "name": "Mahe",
        "location": "Melbourne",
        "radius": "20km"
    }]
    }
]

woolworths_configs = [
    {
        "url": "https://careers.woolworthsgroup.com.au/en_GB/apply/search-jobs/?13316=6987&13321_location_place=Upper%20Mount%20Gravatt,%20Brisbane%20City,%20Queensland,%20Australia&13321_location_radius=20&13321_location_coordinates=[-27.56,153.08]&listFilterMode=1&jobSort=schemaField_3_78_3&jobSortDirection=DESC&jobRecordsPerPage=6&",
        "seen_file": "seen_woolies_Upper_Mount_Gravatt.json",
        "chat_ids": [
    {
        "id": "7021757983",
        "name": "Madhavan",
        "location": "Upper Mount Gravatt",
        "radius": "20km"
    },
    {
        "id": "649377103",
        "name": "Mahe",
        "location": "Upper Mount Gravatt",
        "radius": "20km"
    },
    {
        "id": "6441296270",
        "name": "Devika",
        "location": "Upper Mount Gravatt",
        "radius": "20km"
    }
]
    },
    {
        "url": "https://careers.woolworthsgroup.com.au/en_GB/apply/search-jobs/?13321_location_place=Melbourne,%20City%20of%20Melbourne,%20Victoria,%20Australia&13321_location_radius=20&13321_location_coordinates=[-37.81,144.97]&listFilterMode=1&jobSort=schemaField_3_78_3&jobSortDirection=DESC&jobRecordsPerPage=6&",
        "seen_file": "seen_woolies_Melbourne.json",
        "chat_ids": [{
        "id": "7021757983",
        "name": "Madhavan",
        "location": "Melbourne",
        "radius": "10km"
    },
    {
        "id": "7890180275",
        "name": "Pranav",
        "location": "Melbourne",
        "radius": "20km"
    },
    {
        "id": "789821759",
        "name": "Praveen",
        "location": "Melbourne",
        "radius": "20km"
    },
    {
        "id": "649377103",
        "name": "Mahe",
        "location": "Melbourne",
        "radius": "20km"
    }]
    }
]

# 🚀 Check ALDI Jobs
def check_aldi_jobs():
    for config in aldi_configs:
        job_dict = {}
        for page in range(1, 6):
            url = config["url"].replace("&page=1", f"&page={page}")
            for job in get_aldi_job_postings(url):
                job_dict[job[2]] = job
        seen_ids = load_seen_req_ids(config["seen_file"])
        new_jobs = [job for job in job_dict.values() if job[2] not in seen_ids]
        if new_jobs:
            msg = "📢 *New ALDI Job Postings!*\n\n"
            for job in new_jobs:
                msg += f"📌 [{escape_markdown(job[0])}]({job[1]})\n"
                msg += f"📍 *Location:* {escape_markdown(job[3])}\n"
                msg += f"🆔 *Ref:* {escape_markdown(job[2])}\n"
                msg += "-----------------------\n"
            for user in config["chat_ids"]:
              personalized_msg = (
    f"Hey {user.get('name', 'User')} 👋 – Jobs near *{escape_markdown(user.get('location', 'your area'))}* "
    f"({escape_markdown(user.get('radius', 'unknown range'))})\n\n"
    + msg
)

              send_telegram_notification(personalized_msg, user['id'])

            seen_ids.update([job[2] for job in new_jobs])
            save_seen_req_ids(seen_ids, config["seen_file"])

# 🚀 Check Woolworths Jobs
def check_woolworths_jobs():
    for config in woolworths_configs:
        job_dict = {}
        for page in range(1, 6):
            url = config["url"] + f"&page={page}"
            for job in get_woolworths_job_postings(url):
                job_dict[job[2]] = job
        seen_ids = load_seen_req_ids(config["seen_file"])
        new_jobs = [job for job in job_dict.values() if job[2] not in seen_ids]

        if new_jobs:
            msg = "📢 *New Woolworths Job Postings!*\n\n"
            for job in new_jobs:
                job_link = f"https://careers.woolworthsgroup.com.au/en_GB/apply/JobDetail/{job[2]}"
                msg += f"📌 [{escape_markdown(job[0])}]({job_link})\n"
                msg += f"📅 *Date Posted:* {escape_markdown(job[1])}\n"
                msg += f"📍 *Location:* {escape_markdown(job[3])}\n"
                msg += f"🆔 *REQ ID:* {escape_markdown(job[2])}\n"
                msg += "-----------------------\n"

            for user in config["chat_ids"]:
                personalized_msg = (
                    f"Hey {user.get('name', 'User')} 👋 – Jobs near *{escape_markdown(user.get('location', 'your area'))}* "
                    f"({escape_markdown(user.get('radius', 'unknown range'))})\n\n"
                    + msg
                )
                send_telegram_notification(personalized_msg, user['id'])

            seen_ids.update([job[2] for job in new_jobs])
            save_seen_req_ids(seen_ids, config["seen_file"])

# 🔁 Main Loop
def run_job_notifier():
    print("🟢 Unified ALDI & Woolworths job notifier started!", flush=True)
    while True:
        print(f"[{datetime.now()}] 🔍 Checking all job listings...", flush=True)
        check_aldi_jobs()
        check_woolworths_jobs()
        print(f"[{datetime.now()}] ✅ Done. Sleeping for 15 minutes...\n", flush=True)
        time.sleep(900)

# 🚀 Start
run_job_notifier()
