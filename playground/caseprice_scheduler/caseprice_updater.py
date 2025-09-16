from apscheduler.schedulers.background import BackgroundScheduler 
from apscheduler.triggers.cron import CronTrigger
from playground.views import WebAppViewset



def start():
    scheduler = BackgroundScheduler()
    weekly = WebAppViewset()
    scheduler.add_job(weekly.periodically_update,"interval",minutes=21,id="leaderboardupdated_001",replace_existing=True)
    scheduler.add_job(weekly.change_weekly, trigger='cron', day_of_week='tue',hour=22,minute=36, second=1)
    scheduler.add_job(weekly.addPoints, trigger='cron', day_of_week='tue',hour=22,minute=36, second=2)
    scheduler.add_job(weekly.set_previous, trigger='cron', day_of_week='tue',hour=22,minute=36, second=3)
    scheduler.add_job(weekly.set_new_values, trigger='cron', day_of_week='tue',hour=22,minute=36, second=4)
    scheduler.start()

