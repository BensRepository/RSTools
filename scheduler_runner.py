import os

# Set the environment variable *before* any Django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WebApp.settings")

import django
django.setup()

# Now you can import Django-dependent modules safely
from apscheduler.schedulers.blocking import BlockingScheduler
from playground.views import WebAppViewset

def main():
    scheduler = BlockingScheduler()
    weekly = WebAppViewset()
    scheduler.add_job(weekly.periodically_update,"interval",minutes=0.1,id="leaderboardupdated_001",replace_existing=True)
    scheduler.add_job(weekly.change_weekly, trigger='cron', day_of_week='sun', hour=22, minute=59, second=56, replace_existing=True)
    scheduler.add_job(weekly.addPoints, trigger='cron', day_of_week='sun', hour=22, minute=59, second=57, replace_existing=True)
    scheduler.add_job(weekly.set_previous, trigger='cron', day_of_week='sun', hour=22, minute=59, second=58, replace_existing=True)
    scheduler.add_job(weekly.set_new_values, trigger='cron', day_of_week='sun', hour=22, minute=59, second=59, replace_existing=True)

    print("Scheduler started...")
    scheduler.start()

if __name__ == "__main__":
    main()