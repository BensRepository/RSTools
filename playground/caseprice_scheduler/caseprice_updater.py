from apscheduler.schedulers.background import BackgroundScheduler 
from apscheduler.triggers.cron import CronTrigger
from playground.views import WebAppViewset



def start():
    scheduler = BackgroundScheduler()
    weekly = WebAppViewset()
    scheduler.add_job(weekly.periodically_update,"interval",minutes=5,id="leaderboardupdated_001",replace_existing=True)
    scheduler.add_job(weekly.change_weekly, trigger='cron', day_of_week='fri',hour=22,minute=10, second=56,replace_existing=True)
    scheduler.add_job(weekly.addPoints, trigger='cron', day_of_week='fri',hour=22,minute=10, second=57,replace_existing=True)
    scheduler.add_job(weekly.set_previous, trigger='cron', day_of_week='fri',hour=22,minute=10, second=58,replace_existing=True)
    scheduler.add_job(weekly.set_new_values, trigger='cron', day_of_week='fri',hour=22,minute=10, second=59,replace_existing=True)
    scheduler.start()

