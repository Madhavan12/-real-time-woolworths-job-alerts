import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import time

# Function to send Telegram notification
def send_telegram_notification(message, chat_id, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"  # Allows bold, italic, etc
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"[{datetime.now()}] ✅ Telegram notification sent to {chat_id}.", flush=True)
    else:
        print(f"[{datetime.now()}] ❌ Failed to send Telegram to {chat_id}. Status: {response.status_code}", flush=True)

# Function to get job postings from Woolworths careers page
def get_job_postings(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[{datetime.now()}] ❌ Failed to retrieve page: {url}", flush=True)
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    job_posts = soup.find_all('article', class_='article article--w--full article--result')
    job_list = []

    for job in job_posts:
        try:
            job_title = job.find('h3', class_='article__header__text__title').get_text(strip=True)
            job_date = job.find('span', class_='list-item-posted').get_text(strip=True)
            req_id = job.find('span', class_='list-item-ref').get_text(strip=True).replace('REQ ID', '').strip()
            job_location = job.find('span', class_='list-item-location').get_text(strip=True)
            job_list.append((job_title, job_date, req_id, job_location))
        except Exception as e:
            print(f"[{datetime.now()}] ⚠️ Error parsing job: {e}", flush=True)

    return job_list

# Load previously seen REQ IDs
def load_seen_req_ids(file_name="seen_req_ids.json"):
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)
            return set(data['seen_req_ids'])
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

# Save seen REQ IDs
def save_seen_req_ids(req_ids, file_name="seen_req_ids.json"):
    with open(file_name, 'w') as f:
        json.dump({'seen_req_ids': list(req_ids)}, f)

# Main function
def check_new_job_postings_periodically():
    base_url = "https://careers.woolworthsgroup.com.au/en_GB/apply/search-jobs/?13316=6987&13316_format=18944&13321_location_place=Upper%20Mount%20Gravatt,%20Brisbane%20City,%20Queensland,%20Australia&13321_location_radius=20&13321_location_coordinates=[-27.56,153.08]&listFilterMode=1&jobSort=schemaField_3_78_3&jobSortDirection=DESC&jobRecordsPerPage=6&"

    bot_token = "7837144647:AAEpyx-Z5h7Fs0Xf0yNmfHc9dUWh9fEfO9c"
    chat_ids = ["649377103", "7021757983", "6441296270"]

    print("🟢 Job notifier started successfully.", flush=True)

    while True:
        print(f"[{datetime.now()}] 🔍 Checking for job postings...", flush=True)

        job_dict = {}

        for page in range(1, 6):
            url = base_url + f"&page={page}"
            page_jobs = get_job_postings(url)
            for job in page_jobs:
                req_id = job[2]
                if req_id not in job_dict:
                    job_dict[req_id] = job

        current_jobs = list(job_dict.values())

        seen_req_ids = load_seen_req_ids()
        new_jobs = [job for job in current_jobs if job[2] not in seen_req_ids]

        if new_jobs:
            message = "📢 *New Job Postings Alert!*\n\n"
            for job in new_jobs:
                safe_title = job[0].replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.').replace('!', '\\!')
                job_link = f"https://careers.woolworthsgroup.com.au/en_GB/apply/JobDetail/{job[2]}"
                message += f"📌 [{safe_title}]({job_link})\n"
                message += f"📅 *Date Posted:* {job[1]}\n"
                message += f"📍 *Location:* {job[3]}\n"
                message += f"🆔 *REQ ID:* {job[2]}\n"
                message += "-----------------------\n"



            for chat_id in chat_ids:
                send_telegram_notification(message, chat_id, bot_token)

            seen_req_ids.update([job[2] for job in new_jobs])
            save_seen_req_ids(seen_req_ids)
        else:
            print(f"[{datetime.now()}] No new job postings found.", flush=True)

        time.sleep(900)  # Sleep 15 minutes

# Run it
check_new_job_postings_periodically()
