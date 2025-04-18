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
        "text": message
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Telegram notification sent.")
    else:
        print("Failed to send Telegram notification.")

# Function to get job postings from Woolworths careers page with pagination
def get_job_postings(url):
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to retrieve the page.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract job postings
    job_posts = soup.find_all('article', class_='article article--w--full article--result')
    job_list = []

    for job in job_posts:
        # Extract the job title from <h3> tag
        job_title = job.find('h3', class_='article__header__text__title').get_text(strip=True)

        # Extract the posted date from <span> tag
        job_date = job.find('span', class_='list-item-posted').get_text(strip=True)

        # Extract the REQ ID from <span> tag
        req_id = job.find('span', class_='list-item-ref').get_text(strip=True).replace('REQ ID', '').strip()

        # Extract the location from <span> tag
        job_location = job.find('span', class_='list-item-location').get_text(strip=True)

        job_list.append((job_title, job_date, req_id, job_location))

    return job_list

# Function to load previously seen REQ IDs from a file (if exists)
def load_seen_req_ids(file_name="seen_req_ids.json"):
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)
            return set(data['seen_req_ids'])  # Return as a set for fast lookup
    except (FileNotFoundError, json.JSONDecodeError):
        return set()  # If no REQ IDs saved, return an empty set

# Function to save the REQ IDs of the current job postings
def save_seen_req_ids(req_ids, file_name="seen_req_ids.json"):
    with open(file_name, 'w') as f:
        json.dump({'seen_req_ids': list(req_ids)}, f)

# Function to check for new job postings and send Telegram notifications
def check_new_job_postings_periodically():
    base_url = "https://careers.woolworthsgroup.com.au/en_GB/apply/search-jobs/?13321_location_place=Melbourne,%20City%20of%20Melbourne,%20Victoria,%20Australia&13321_location_radius=50&13321_location_coordinates=[-37.81,144.97]&listFilterMode=1&jobSort=schemaField_3_78_3&jobSortDirection=DESC&jobRecordsPerPage=6&"

    # Replace these with your Telegram bot token and chat ID
    bot_token = "7837144647:AAEpyx-Z5h7Fs0Xf0yNmfHc9dUWh9fEfO9c"
    chat_id = ["649377103","7021757983"]  # Example: chat_id = "123456789"

    while True:
        current_jobs = []

        # Loop through 5 pages (adjusting the starting point for pagination)
        for page in range(1, 6):
            url = base_url + f"&page={page}"
            current_jobs.extend(get_job_postings(url))

        # Load the previously seen REQ IDs
        seen_req_ids = load_seen_req_ids()

        # Find new job postings (those with REQ IDs not already seen)
        new_jobs = [job for job in current_jobs if job[2] not in seen_req_ids]

        if new_jobs:
            subject = "New Job Postings Alert!"
            body = "The following new jobs have been posted:\n\n"
            # Format each job posting
            for job in new_jobs:
                body += f"Title: {job[0]}\n"
                body += f"Date Posted: {job[1]}\n"
                body += f"Location: {job[3]}\n"
                body += f"REQ ID: {job[2]}\n"
                body += "---------\n"

            for ids in chat_id:
                # Send Telegram notification
                send_telegram_notification(body, ids, bot_token)

            # Update the seen REQ IDs with the new ones
            seen_req_ids.update([job[2] for job in new_jobs])
            save_seen_req_ids(seen_req_ids)
        else:
            print("No new job postings.")

        # Wait for 15 minutes before checking again
        time.sleep(900)  # 900 seconds = 15 minutes

# Start the periodic check
check_new_job_postings_periodically()
