from django.db import models

class RSLeaderboardEntry(models.Model):
    id = models.AutoField(primary_key=True)
    rsn = models.CharField(max_length=20)
    weeklybosskillsstart = models.IntegerField()
    weeklybosskillscurrent = models.IntegerField()
    totalxpstart = models.IntegerField()
    totalxpcurrent = models.IntegerField()
    weeklyskillxpstart = models.IntegerField()
    weeklyskillxpcurrent = models.IntegerField()
    event = models.CharField(max_length=20)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.rsn
    
class Weeklys(models.Model):
    id = models.AutoField(primary_key=True)
    skill = models.CharField(max_length=45)
    boss = models.CharField(max_length=45)

class GainsLeaderboard(models.Model):
    rsn = models.CharField(max_length=20,primary_key=True)
    firstplaces = models.IntegerField(default=0)
    secondplaces = models.IntegerField(default=0)
    thirdplaces = models.IntegerField(default=0)
    @property
    def points(self):
        points = self.firstplaces*3 + self.secondplaces*2 + self.thirdplaces *1
        return points

    date_modified = models.DateTimeField(auto_now=True)

class RaidsLeaderboard(models.Model):
    rsn = models.CharField(max_length=20,primary_key=True)
    coxkcstart = models.IntegerField()
    coxkccurrent = models.IntegerField()

    toakcstart = models.IntegerField()
    toakccurrent = models.IntegerField()

    tobkcstart = models.IntegerField()
    tobkccurrent = models.IntegerField()


    date_modified = models.DateTimeField(auto_now=True)
    # @property
    # def sum(self):
    #     self.sum = (self.coxkccurrent - self.coxkcstart) + (self.toakccurrent - self.toakcstart) + (self.tobkccurrent - self.tobkcstart)
    #     return super(RaidsLeaderboard, self).save()

