from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import json
import random
import sys, os


from .models import RSLeaderboardEntry
from .models import Weeklys
from .models import RaidsLeaderboard
from .models import GainsLeaderboard
from rest_framework import viewsets
import glob
from WebApp.settings import STATIC_URL
# Create your views here.


minigameNames = [
 
    "Bounty Hunter - Hunter",
    "Bounty Hunter - Rogue",
    "Bounty Hunter (Legacy) - Hunter",
    "Bounty Hunter (Legacy) - Rogue",
    "Clue Scrolls (all)",
    "Clue Scrolls (beginner)",
    "Clue Scrolls (easy)",
    "Clue Scrolls (medium)",
    "Clue Scrolls (hard)",
    "Clue Scrolls (elite)",
    "Clue Scrolls (master)",
    "LMS - Rank",
    "PvP Arena - Rank",
    "Soul Wars Zeal",
    "Rifts closed",
    "Colosseum Glory",
    "Collections Logged",
    "Abyssal Sire",
    "Alchemical Hydra",
    "Amoxliatl",
    "Araxxor",
    "Artio",
    "Barrows Chests",
    "Bryophyta",
    "Callisto",
    "Calvar'ion",
    "Cerberus",
    "Chambers of Xeric",
    "Chambers of Xeric Challenge Mode",
    "Chaos Elemental",
    "Chaos Fanatic",
    "Commander Zilyana",
    "Corporeal Beast",
    "Crazy Archaeologist",
    "Dagannoth Prime",
    "Dagannoth Rex",
    "Dagannoth Supreme",
    "Deranged Archaeologist",
    "Doom of Mokhaiotl",
    "Duke Sucellus",
    "General Graardor",
    "Giant Mole",
    "Grotesque Guardians",
    "Hespori",
    "Kalphite Queen",
    "King Black Dragon",
    "Kraken",
    "Kree'Arra",
    "K'ril Tsutsaroth",
    "Lunar Chests",
    "Mimic",
    "Nex",
    "Nightmare",
    "Phosani's Nightmare",
    "Obor",
    "Phantom Muspah",
    "Sarachnis",
    "Scorpia",
    "Scurrius",
    "Skotizo",
    "Sol Heredit",
    "Spindel",
    "Tempoross",
    "The Gauntlet",
    "The Corrupted Gauntlet",
    "The Hueycoatl",
    "The Leviathan",
    "The Royal Titans",
    "The Whisperer",
    "Theatre of Blood",
    "Theatre of Blood Hard Mode",
    "Thermonuclear Smoke Devil",
    "Tombs of Amascut",
    "Tombs of Amascut Expert",
    "TzKal-Zuk",
    "TzTok-Jad",
    "Vardorvis",
    "Venenatis",
    "Vet'ion",
    "Vorkath",
    "Wintertodt",
    "Yama",
    "Zalcano",
    "Zulrah"

         ]
SkillNames = ["Overall",
            "Attack",
            "Defence",
            "Strength",
            "Hitpoints",
            "Ranged",
            "Prayer",
            "Magic",
            "Cooking",
            "Woodcutting",
            "Fletching",
            "Fishing",
            "Firemaking",
            "Crafting",
            "Smithing",
            "Mining",
            "Herblore",
            "Agility",
            "Thieving",
            "Slayer",
            "Farming",
            "Runecrafting",
            "Hunter",
            "Construction"]





class WebAppViewset(viewsets.ModelViewSet):
   
    
    def load_rstools(request):
        return render(request,'rstools.html')
    
    def load_raids(request):
        return render(request,'Raids/raids.html')
    def load_cox(request):
        return render(request,'Raids/cox.html')
    def load_tob(request):
        return render(request,'Raids/tob.html')
    def load_toa(request):
        return render(request,'Raids/toa.html')
    
    def load_lootsimulator(request):
        return render(request,'lootsimulator.html')
    

    def skill_wheel(request):
        return render(request,'skill_wheel.html')

    def load_leaderboard(request):
        rsn = request.POST.get('rsn')
        print(rsn)
        if(rsn != None):
            try:
                url = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" +rsn
                api_request = requests.get(url)
                api_request.raise_for_status() 
                api_request = api_request.content

                weeklyObjects = Weeklys.objects.all()
                weekly = weeklyObjects.get(id=1)
                data = str(api_request).split('\\')
                addDB = True
                for x in RSLeaderboardEntry.objects.all():
                    print(x.rsn.lower() +" "+str(rsn).lower())
                    if(x.rsn.lower() == str(rsn).lower() and x.event == "current"):
                        print("Do not add to DB")
                        addDB = False
                        DBObject = x
  
                if(addDB == True):
                    print("Add to DB Main Leaderboard")
                    newEntry = RSLeaderboardEntry()
                    newEntry.rsn = rsn 
                    if data[minigameNames.index(weekly.boss)+26] == "n-1,-1":
                        newEntry.weeklybosskillsstart = 0
                        newEntry.weeklybosskillscurrent = 0
                    else:
                        newEntry.weeklybosskillsstart = data[minigameNames.index(weekly.boss)+26].split(',')[1]
                        newEntry.weeklybosskillscurrent = data[minigameNames.index(weekly.boss)+26].split(',')[1]
    

                    newEntry.totalxpstart = data[0].split(',')[2]
                    newEntry.totalxpcurrent = data[0].split(',')[2]
            
                    newEntry.weeklyskillxpstart = data[SkillNames.index(weekly.skill)].split(',')[2]
                    newEntry.weeklyskillxpcurrent = data[SkillNames.index(weekly.skill)].split(',')[2]
               
                    newEntry.event="current"
                    newEntry.save()
                    print("created new entry main leaderboard")



                    newEntry = RaidsLeaderboard()
                    newEntry.rsn = rsn
                    cox = "Chambers of Xeric"
                    coxcm = "Chambers of Xeric Challenge Mode"
                    tob = "Theatre of Blood"
                    tobh = "Theatre of Blood Hard Mode"
                    toa = "Tombs of Amascut"
                    toae = "Tombs of Amascut Expert"

                    #Chambers of Xeric
                    coxStart = 0
                    coxCurrent = 0
                    print(data)
                    if data[minigameNames.index(cox)+26] == "n-1,-1":
                        coxStart = 0
                        coxCurrent = 0
                    else:
                        coxStart= int(data[minigameNames.index(cox)+26].split(',')[1])
                        coxCurrent= int(data[minigameNames.index(cox)+26].split(',')[1])

                    if data[minigameNames.index(coxcm)+26] == "n-1,-1":
                        print("No CMs")
                    else:
                        coxStart += int(data[minigameNames.index(coxcm)+26].split(',')[1])
                        coxCurrent += int(data[minigameNames.index(coxcm)+26].split(',')[1])


                    #Tombs of Amascut
                    toaStart = 0
                    toaCurrent = 0
                    if data[minigameNames.index(toa)+26] == "n-1,-1":
                        toaStart = 0
                        toaCurrent = 0
                    else:
                        toaStart = int(data[minigameNames.index(toa)+26].split(',')[1])
                        toaCurrent = int(data[minigameNames.index(toa)+26].split(',')[1])

                    if data[minigameNames.index(toae)+26] == "n-1,-1":
                        print("No Experts")
                    else:
               
                       toaStart += int(data[minigameNames.index(toae)+26].split(',')[1])
                       toaCurrent += int(data[minigameNames.index(toae)+26].split(',')[1])

                    newEntry.toakcstart = toaStart
                    newEntry.toakccurrent = toaCurrent

                    #Theatre of Blood
                    tobStart = 0
                    tobCurrent = 0
                    if data[minigameNames.index(tob)+26] == "n-1,-1":
                        tobStart = 0
                        tobCurrent = 0
                    else:
                        tobStart = int(data[minigameNames.index(tob)+26].split(',')[1])
                        tobCurrent = int(data[minigameNames.index(tob)+26].split(',')[1])

                    if data[minigameNames.index(tobh)+26] == "n-1,-1":
                        print("no hard kc")
                    else:
                        tobStart += int(data[minigameNames.index(tobh)+26].split(',')[1])
                        tobCurrent += int(data[minigameNames.index(tobh)+26].split(',')[1])

    
                    newEntry.toakcstart = toaStart
                    newEntry.toakccurrent = toaCurrent

                    newEntry.coxkcstart = coxStart
                    newEntry.coxkccurrent = coxCurrent

                    newEntry.tobkcstart = tobStart
                    newEntry.tobkccurrent = tobCurrent
                    
                    newEntry.save()
                    print("created new entry raid leaderboard")
                    try:
                        gainsLeaderboardEntry = GainsLeaderboard.objects.create(
                            rsn = rsn,
                            firstplaces = 0,
                            secondplaces = 0,
                            thirdplaces = 0
                        )
   
                        gainsLeaderboardEntry.save
                        print("Added "+rsn+" to Gains Leaderboard")
                    except:
                        print("Failed to add to Gains Leaderboard")

                else:
                    try:
                        url = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" +rsn
                        api_request = requests.get(url)
                        api_request.raise_for_status() 
                        api_request = api_request.content
                    
                        weeklyObjects = Weeklys.objects.all()
                        weekly = weeklyObjects.get(id=1)
                        data = str(api_request).split('\\')
                        if data[minigameNames.index(weekly.boss)+26] == "n-1,-1":
                            DBObject.weeklybosskillscurrent = 0
                        else:
                            print(data[minigameNames.index(weekly.boss)+26])
                            DBObject.weeklybosskillscurrent = data[minigameNames.index(weekly.boss)+26].split(',')[1]
                        DBObject.totalxpcurrent = data[0].split(',')[2]
                        if data[SkillNames.index(weekly.skill)] == "n-1,-1":
                            DBObject.weeklyskillxpcurrent = 0
                        else:
                            DBObject.weeklyskillxpcurrent = data[SkillNames.index(weekly.skill)].split(',')[2]

                        weeklySkillXpGained = int(data[0].split(',')[2]) - int(DBObject.totalxpstart)

                        DBObject.save()
                        print(DBObject.rsn + " was Updated. " + str(weeklySkillXpGained) + " Weekly XP Gained")


                        # Raids manual update

                        rsnRaidEntry = RaidsLeaderboard.objects.get(rsn__iexact = rsn)
                    
                        cox = "Chambers of Xeric"
                        coxcm = "Chambers of Xeric Challenge Mode"
                        tob = "Theatre of Blood"
                        tobh = "Theatre of Blood Hard Mode"
                        toa = "Tombs of Amascut"
                        toae = "Tombs of Amascut Expert"

                        #Chambers of Xeric
                        coxCurrent = 0
                        print(data)
                        if data[minigameNames.index(cox)+26] == "n-1,-1":
                            coxCurrent = 0
                        else:
                            coxCurrent= int(data[minigameNames.index(cox)+26].split(',')[1])

                        if data[minigameNames.index(coxcm)+26] == "n-1,-1":
                            print("No CMs")
                        else:
                            coxCurrent += int(data[minigameNames.index(coxcm)+26].split(',')[1])


                        #Tombs of Amascut
                        toaCurrent = 0
                        if data[minigameNames.index(toa)+26] == "n-1,-1":
                            toaCurrent = 0
                        else:
                            toaCurrent = int(data[minigameNames.index(toa)+26].split(',')[1])

                        if data[minigameNames.index(toae)+26] == "n-1,-1":
                            print("No Experts")
                        else:
                            toaCurrent += int(data[minigameNames.index(toae)+26].split(',')[1])

                        #Theatre of Blood
                        tobCurrent = 0
                        if data[minigameNames.index(tob)+26] == "n-1,-1":
                            tobCurrent = 0
                        else:
                            tobCurrent = int(data[minigameNames.index(tob)+26].split(',')[1])

                        if data[minigameNames.index(tobh)+26] == "n-1,-1":
                            print("no hard kc")
                        else:
                            tobCurrent += int(data[minigameNames.index(tobh)+26].split(',')[1])

                        rsnRaidEntry.toakccurrent = toaCurrent
                        rsnRaidEntry.coxkccurrent = coxCurrent
                        rsnRaidEntry.tobkccurrent = tobCurrent
                        
                        rsnRaidEntry.save()
                        print("Updated RaidEntry manually")

                        print(rsnRaidEntry)
                    except Exception as e:
                        # exc_type, exc_obj, exc_tb = sys.exc_info()
                        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(e)
                 

            except Exception as e:
                print(e)



        leaderboard_data=[]
        raids_leaderboard_data=[]
        context = {}
        weeklyObjects = Weeklys.objects.all()
        weekly = weeklyObjects.get(id=1)
        context['skill'] = weekly.skill
        context['boss'] = weekly.boss

        weeklyPrevious = weeklyObjects.get(id=2)
        context['previous_skill'] = weeklyPrevious.skill
        context['previous_boss'] = weeklyPrevious.boss

        print(weeklyPrevious.skill)

        for x in RSLeaderboardEntry.objects.all().values():
            leaderboard_data.append(x)
        
        context['leaderboard_data'] = leaderboard_data

        for x in RaidsLeaderboard.objects.all().values():
            raids_leaderboard_data.append(x)
        context['raids'] = raids_leaderboard_data
        
        gains_leaderboard = []
        for x in GainsLeaderboard.objects.all().values():
            gains_leaderboard.append(x)

        context['gains'] = gains_leaderboard



        return render(request,'leaderboard.html',context)
    
    def change_weekly(self):
        try:
            weeklyObjects = Weeklys.objects.all()
            current = weeklyObjects.get(id=1)
            previous = weeklyObjects.get(id=2)

            previous.skill = current.skill
            previous.boss = current.boss
            previous.save()
        except:
            print("failed to set previous boss in change weekly")
            pass

        weeklyObjects = Weeklys.objects.all()
        weekly = weeklyObjects.get(id=1)
        try:
            boss_index = random.randint(15,len(minigameNames))
            skill_index = random.randint(1,len(SkillNames))
            weekly.boss = minigameNames[boss_index]
            weekly.skill = SkillNames[skill_index]
            print(weekly.boss +" New Boss")
            print(weekly.skill+" New Skill")                        
            while((weekly.boss == current.boss) or (current.skill == weekly.skill) or (weekly.boss =="reroll")):
                print("Duplicate or Reroll")
                boss_index = random.randint(17,len(minigameNames))
                skill_index = random.randint(1,len(SkillNames))
                weekly.boss = minigameNames[boss_index]
                weekly.skill = SkillNames[skill_index]

            weekly.save(update_fields=['boss','skill'])
            print("saves model")
        except:
            print("change weekly failed")
            pass


    def set_previous(self):

        LeaderboardObjects = RSLeaderboardEntry.objects.all()
        try:
            for object in LeaderboardObjects:
                if object.event == "previous":
                    object.delete() 
                if object.event == "current":
                    object.pk = None
                    object.save()
                    
                    object.event = "previous"
                    object.save()
                    print("set_previous successful" + object.rsn)
        except:
            print("set_previous failed")

        seen = set()
        for obj in RSLeaderboardEntry.objects.order_by('id'):
            identifier = (obj.event, obj.rsn.lower())
            if identifier in seen:
                obj.delete()
            else:
                seen.add(identifier)
       

    def periodically_update(self):

        last_updated = RSLeaderboardEntry.objects.all().filter(event="current").order_by('date_modified').first()
        print(last_updated.rsn)
        try:
            url = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" +last_updated.rsn
            api_request = requests.get(url)
            api_request.raise_for_status() 
            api_request = api_request.content

         
            weeklyObjects = Weeklys.objects.all()
            weekly = weeklyObjects.get(id=1)
            data = str(api_request).split('\\')

            if data[minigameNames.index(weekly.boss)+26] == "n-1,-1":
                last_updated.weeklybosskillscurrent = 0
            else:
                last_updated.weeklybosskillscurrent = data[minigameNames.index(weekly.boss)+26].split(',')[1]
            last_updated.totalxpcurrent = data[0].split(',')[2]


            if data[SkillNames.index(weekly.skill)] == "n-1,-1":
                last_updated.weeklyskillxpcurrent = 0
            else:
                last_updated.weeklyskillxpcurrent = data[SkillNames.index(weekly.skill)].split(',')[2]

            weeklySkillXpGained = int(data[0].split(',')[2]) - int(last_updated.totalxpstart)
            last_updated.save()

            last_updated_raids = RaidsLeaderboard.objects.get(rsn=last_updated.rsn)

            #Raids updates
            #COX
            coxkc = 0
            if data[minigameNames.index("Chambers of Xeric")+26] == "n-1,-1":
                print("No cox kc")
            else:
                coxkc = int(data[minigameNames.index("Chambers of Xeric")+26].split(',')[1])
                print("COX KC " +data[minigameNames.index("Chambers of Xeric")+26].split(',')[1])

            if data[minigameNames.index("Chambers of Xeric Challenge Mode")+26] == "n-1,-1":
                print("No CMs")
            else:
                coxkc += int(data[minigameNames.index("Chambers of Xeric Challenge Mode")+26].split(',')[1])
                print("CM "+data[minigameNames.index("Chambers of Xeric Challenge Mode")+26].split(',')[1])
    
            last_updated_raids.coxkccurrent = coxkc
            
            #TOA
            
            toakc = 0
            if data[minigameNames.index("Tombs of Amascut")+26] == "n-1,-1":
                print("No TOA kc")
            else:
                toakc = int(data[minigameNames.index("Tombs of Amascut")+26].split(',')[1])
                print("TOA KC " +data[minigameNames.index("Tombs of Amascut")+26].split(',')[1])

            if data[minigameNames.index("Tombs of Amascut Expert")+26] == "n-1,-1":
                print("No TOA Expert")
            else:
                toakc += int(data[minigameNames.index("Tombs of Amascut Expert")+26].split(',')[1])
                print("TOA Experts "+data[minigameNames.index("Tombs of Amascut Expert")+26].split(',')[1])
            last_updated_raids.toakccurrent = toakc

            #TOB
            tobkc = 0
            if data[minigameNames.index("Theatre of Blood")+26] == "n-1,-1":
                print("No TOB")
            else:
                tobkc += int(data[minigameNames.index("Theatre of Blood")+26].split(',')[1])
                print("TOB : "+ data[minigameNames.index("Theatre of Blood")+26].split(',')[1])
            if data[minigameNames.index("Theatre of Blood Hard Mode")+26] == "n-1,-1":
                print("No TOB Hard Mode")
            else:
                tobkc += int(data[minigameNames.index("Theatre of Blood Hard Mode")+26].split(',')[1])
                print("TOB Hard: "+ data[minigameNames.index("Theatre of Blood Hard Mode")+26].split(',')[1])

            print("above")
            last_updated_raids.toakccurrent = toakc
        
            last_updated_raids.save()
        
           
            print(last_updated.rsn + " was Updated. " + str(weeklySkillXpGained) + " Weekly XP Gained")


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print("Unable to Update Leaderboard")


    def set_new_values(self):

        LeaderboardObjects = RSLeaderboardEntry.objects.all()
        try:
            for object in LeaderboardObjects:
                if object.event == "current":
                    try:
                        url = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" +object.rsn
                        api_request = requests.get(url)
                        api_request.raise_for_status() 
                        api_request = api_request.content
                 
                        weeklyObjects = Weeklys.objects.all()
                        weekly = weeklyObjects.get(id=1)
                        
                        data = str(api_request).split('\\')
                        if data[minigameNames.index(weekly.boss)+26] == "n-1,-1":
                            object.weeklybosskillsstart = 0
                            object.weeklybosskillscurrent = 0
                        else:
                            object.weeklybosskillsstart = data[minigameNames.index(weekly.boss)+26].split(',')[1]
                            object.weeklybosskillscurrent = data[minigameNames.index(weekly.boss)+26].split(',')[1]
                        

                        if data[SkillNames.index(weekly.skill)] == "n-1,-1":
                            object.weeklyskillxpstart = 0
                            object.weeklyskillxpcurrent = 0
                        else:
                            object.weeklyskillxpstart = data[SkillNames.index(weekly.skill)].split(',')[2]
                            object.weeklyskillxpcurrent = data[SkillNames.index(weekly.skill)].split(',')[2]
               
                        object.totalxpstart = data[0].split(',')[2]
                        object.totalxpcurrent = data[0].split(',')[2]

                        
 
                        object.save()
                        print("set_values successful")
                    except Exception as e:
                        print(e)
                        print("unsuccessful")
        
                      
        except:
            print("Didn't save model")
            pass


    def addPoints(self):
        results =  []
        LeaderboardObjects = RSLeaderboardEntry.objects.all().filter(event = "current")
        try:
            for object in LeaderboardObjects:
               results.append([object.rsn,(object.weeklybosskillscurrent - object.weeklybosskillsstart),(object.weeklyskillxpcurrent - object.weeklyskillxpstart),(object.totalxpcurrent - object.totalxpstart)])
            print("created results")
        except Exception as e:
                    print(e)
                    print("Failed to get leardboard data")
  
        sorted_data_boss = sorted(results, key=lambda x: x[1], reverse=True)
        sorted_data_skill = sorted(results, key=lambda x: x[2], reverse=True)
        sorted_data_total_xp = sorted(results, key=lambda x: x[3], reverse=True)

        #Boss Points
     
        pointsLeaderboardBossFirstPlace = GainsLeaderboard.objects.all().filter(rsn = sorted_data_boss[0][0]).first()
        print(sorted_data_boss)

        if(sorted_data_boss[0][1] ==0):
            print("no one got a KC for Bossing")
        
        else:
            pointsLeaderboardBossFirstPlace.firstplaces +=1
            pointsLeaderboardBossFirstPlace.save()
        


        pointsLeaderboardBossSecondPlace = GainsLeaderboard.objects.filter(rsn = sorted_data_boss[1][0]).first()
   
        if(sorted_data_boss[1][1] ==0):
            print("No one came second boss")
        else:
            pointsLeaderboardBossSecondPlace.secondplaces +=1
            pointsLeaderboardBossSecondPlace.save()

        pointsLeaderboardBossThirdPlace = GainsLeaderboard.objects.filter(rsn = sorted_data_boss[2][0]).first()
    
        if(sorted_data_boss[2][1] ==0):
            print("No one came third Boss")
        else:
            pointsLeaderboardBossThirdPlace.thirdplaces += 1
            pointsLeaderboardBossThirdPlace.save()

        #Skill Points

        pointsLeaderboardSkillFirstPlace = GainsLeaderboard.objects.filter(rsn = sorted_data_skill[0][0]).first()
        if(sorted_data_skill[0][2] ==0):
            print("no one got XP for Skilling")
        else:
            pointsLeaderboardSkillFirstPlace.firstplaces += 1
            pointsLeaderboardSkillFirstPlace.save()

        pointsLeaderboardSkillSecondPlace = GainsLeaderboard.objects.filter(rsn = sorted_data_skill[1][0]).first()
        if(sorted_data_skill[1][2] ==0):
            print("No one came 2nd Skill")
        else:
            pointsLeaderboardSkillSecondPlace.secondplaces += 1
            pointsLeaderboardSkillSecondPlace.save()

        pointsLeaderboardSkillThirdPlace = GainsLeaderboard.objects.filter(rsn = sorted_data_skill[2][0]).first()
        if(sorted_data_skill[2][2] ==0):
            print("No one came 3rd Skill")
        else:
            pointsLeaderboardSkillThirdPlace.thirdplaces += 1
            pointsLeaderboardSkillThirdPlace.save()
        #Total XP

        pointsLeaderboardTotalXPFirstPlace = GainsLeaderboard.objects.filter(rsn = sorted_data_total_xp[0][0]).first()
        if(sorted_data_total_xp[0][3] ==0):
            print("No one came 3rd Skill")
        else:
            pointsLeaderboardTotalXPFirstPlace.firstplaces += 1
            pointsLeaderboardTotalXPFirstPlace.save()

        pointsLeaderboardTotalXPSecondPlace = GainsLeaderboard.objects.filter(rsn = sorted_data_total_xp[1][0]).first()
        if(sorted_data_total_xp[1][3] ==0):
            print("No one got XP")
        else:
            pointsLeaderboardTotalXPSecondPlace.secondplaces += 1
            pointsLeaderboardTotalXPSecondPlace.save()

        pointsLeaderboardTotalXPThirdPlace = GainsLeaderboard.objects.filter(rsn = sorted_data_total_xp[2][0]).first()
        if(sorted_data_total_xp[2][3] ==0):
            print("No one came third total xp")
        else:
            pointsLeaderboardTotalXPThirdPlace.thirdplaces += 1
            pointsLeaderboardTotalXPThirdPlace.save()

    def load_statlookup(request):

            return render(request,'statlookup.html')

    def load_statlookupresult(request):
        name = request.POST.get('text')
        name2 = request.POST.get('text2')
        compare = request.POST.get('compare')
        type = request.POST.get('type')
        api_request2 = ""
        print(type)
        print(compare)
        if(type == "Hardcore Ironman"):
            try:
                url = "https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.ws?player=" +name
                api_request = requests.get(url)
                api_request.raise_for_status() 
           
  
            except:
                print("no data returned")
            if(compare == "True"):
                
                try:
                    url = "https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.ws?player=" +name2
                    api_request2 = requests.get(url)
                    api_request2.raise_for_status() 
                    api_request2 = api_request2.content
                except:
                    print("no data returned hc")

        elif(type == "Ultimate Ironman"):
            try:
                url = "https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.ws?player=" +name
                api_request = requests.get(url)
                api_request.raise_for_status() 
            except:
                print("no data returned")
            if(compare == "True"):
                try:
                    url = "https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.ws?player=" +name2
                    api_request2 = requests.get(url)
                    api_request2.raise_for_status() 
                    api_request2 = api_request2.content
                except:
                    print("no data returned")
        elif(type == "Ironman"):
            try:
                url = "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?player=" +name
                api_request = requests.get(url)
                api_request.raise_for_status() 
            except:
                print("no data returned IM")
            if(compare == "True"):
                try:
                    url = "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?player=" +name2
                    api_request2 = requests.get(url)
                    api_request2.raise_for_status() 
                    api_request2 = api_request2.content
                except:
                    print("no data returned IM2")
        else:
            try:
                url = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" +name
                api_request = requests.get(url)
                api_request.raise_for_status() 
                type = "All" 
            except:
                print("no data returned")
                type = "All"
                return render(request,'statlookup.html')
            if(compare == "True"):
                try:
                    url = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" +name2
                    api_request2 = requests.get(url)
                    api_request2.raise_for_status() 
                    api_request2 = api_request2.content
                    print(str(api_request2.content)) 
                except:
                    print("no data returned")
                    type = "All"

            

        context = {"player_data":str(api_request.content),"rsn":name,"type":type, "compare":compare,"player_data_compare":str(api_request2),"rsncompare":name2}
        return render(request,'statlookup_results.html',context=context)

    
    