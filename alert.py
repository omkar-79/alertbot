import os
import requests
from bs4 import BeautifulSoup
import telebot

# URL of the job portal
job_portal_url = "https://gwu-studentemployment.peopleadmin.com/postings/search"

# Replace 'TOKEN' with your Bot's API token
bot_token = '6818076787:AAHkdN4NQVMdVZFHVl_OWs-dHq-7XMFPFaM'

bot = telebot.TeleBot(bot_token)

# Keep track of job titles that have already been posted
posted_jobs = set()

def get_job_updates():
    try:
        response = requests.get(job_portal_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all job postings on the webpage
        job_postings = soup.find_all('div', class_='job-item job-item-posting')

        new_jobs = []

        for posting in job_postings:
            title = posting['data-posting-title']
            if "Non-FWS" in title or "Non FWS" in title:
                if title not in posted_jobs:
                    link = posting.find('a', href=True)['href']
                    full_link = f"https://gwu-studentemployment.peopleadmin.com{link}"
                    openings = posting.find('div', class_='col-md-2 col-xs-12 job-title job-title-text-wrap col-md-push-0').text.strip() if posting.find('div', class_='col-md-2 col-xs-12 job-title job-title-text-wrap col-md-push-0') else "N/A"
                    new_jobs.append((title, full_link, openings))
                    posted_jobs.add(title)

        return new_jobs
    except Exception as e:
        print(f"Failed to get job updates: {e}")
        return []

@bot.message_handler(commands=['jobs'])
def send_jobs(message):
    if posted_jobs:
        jobs_message = "\n\n".join([f"Title: {job[0]}\nLink: {job[1]}\nOpenings: {job[2]}" for job in posted_jobs])
    else:
        jobs_message = "No job postings available."
    bot.reply_to(message, f"Here are the jobs that have been posted:\n\n{jobs_message}")

if __name__ == "__main__":
    # Check for Non_FWS job updates
    new_jobs = get_job_updates()

    for job in new_jobs:
        try:
            # Send Telegram notification for each new job
            message = f"A new Non-FWS job has been posted:\n\nTitle: {job[0]}\nLink: {job[1]}\nNumber of Openings: {job[2]}"
            bot.send_message(chat_id='6964785347', text=message)
        except Exception as e:
            print(f"Failed to send notification: {e}")

    bot.polling()
