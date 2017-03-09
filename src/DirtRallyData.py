#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
import urllib
import urllib2
import json
from decimal import Decimal
import csv
import sys
import cookielib

reload(sys)
sys.setdefaultencoding('latin-1')

#read login file
f = open('login.txt', 'r')
email = f.readline()
password = f.readline()

#read names file
f = open('names.txt', 'r')
names = json.loads(f.read())

#convert time in seconds to HH:MM:SS.ddd format
def secondsToPrintable(seconds):

   mi = (Decimal(seconds) - int(seconds))*1000
   m, s = divmod(seconds, 60)
   h, m = divmod(m, 60)
   return "%02d:%02d:%02d.%03d" % (h, m, s, mi)

#convert time in HH:MM:SS.ddd format to seconds
def timeToSeconds(timeString):

   seconds = Decimal(timeString[-3:])/1000
   if len(timeString) > 4:
      seconds += Decimal(timeString[-6:-4])
   if len(timeString) > 7:
      seconds += Decimal(timeString[-9:-7])*60
   if len(timeString) > 11:
      seconds += Decimal(timeString[-12:-10])*3600
   return seconds

   
# Store the cookies and create an opener that will hold them
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# Add  headers
opener.addheaders = [('User-agent', 'dirt')]

# Install opener 
urllib2.install_opener(opener)

# login page
authentication_url = 'https://accounts.codemasters.com/auth/login?client_id=o8g45jNHt393&redirect_uri=https%3A%2F%2Fwww.dirtgame.com%2FOAuthCallback&skin=Clean&state=uri%3D%252fus%252fhome&reauthenticate=0&grant_type=code&auth_hash=JjkFhCBu4Nnfkz1x9boPdinAlWE%3D'

# Input parameters we are going to send
payload = {
   'ContinueToLinkStaging':'False',
   'DisableLinks':'False',
   'Email':email,
   'Password':password,
   'RememberMe':'False',
  }

# Use urllib to encode the payload
data = urllib.urlencode(payload)

# log in (POST)
req = urllib2.Request(authentication_url, data)
   
debug = False


#todo: Find how to get this automatically
#racenet event id
#pcEventID = '204698'
pcEventID = '205167'
xboxEventID = '205169'
psEventID = '205168'
pcEnabled   = True
xboxEnabled = True
psEnabled   = True
totalEntries = 0


#get the number of stages
html = urllib2.urlopen( "https://www.dirtgame.com/us/api/event?eventId="+pcEventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=0").read()
event=json.loads(html)
numStages = event.get('TotalStages')
stages=[dict() for x in range(numStages)]

#get the number of entries for each platform
if pcEnabled:
   html = urllib2.urlopen( "https://www.dirtgame.com/us/api/event?eventId="+pcEventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=1" ).read()
   event=json.loads(html)
   totalPCEntries = len(event.get('Entries'))
else:
   totalPCEntries = 0
   
if xboxEnabled:
   html = urllib2.urlopen("https://www.dirtgame.com/us/changeplatform?platform=microsoftlive")
   html = urllib2.urlopen( "https://www.dirtgame.com/us/api/event?eventId="+xboxEventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=1" ).read()
   event=json.loads(html)
   totalXboxEntries = len(event.get('Entries'))
else:
   totalXboxEntries = 0
   
if psEnabled:
   html = urllib2.urlopen("https://www.dirtgame.com/us/changeplatform?platform=playstationnetwork")
   html = urllib2.urlopen( "https://www.dirtgame.com/us/api/event?eventId="+psEventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=1" ).read()
   event=json.loads(html)
   totalPsEntries = len(event.get('Entries'))
else:
   totalPsEntries = 0

totalEntries = totalPCEntries + totalXboxEntries + totalPsEntries
entries = [dict() for x in range(totalEntries)]
#get the results for each stage
for x in range(0, numStages):

   stageNum = x + 1
   enabled = False
   device = ''
   #Get results for PC, Xbox, and PS
   for y in range(0, 3):
      if y == 0: 
         enabled = pcEnabled
         eventID = pcEventID
         device  = 'PC'
         html = urllib2.urlopen("https://www.dirtgame.com/us/changeplatform?platform=steam")
      elif y == 1: 
         enabled = xboxEnabled
         eventID = xboxEventID
         device  = 'Xbox'
         html = urllib2.urlopen("https://www.dirtgame.com/us/changeplatform?platform=microsoftlive")
      elif y == 2: 
         enabled = psEnabled
         eventID = psEventID
         device  = 'PS4'
         html = urllib2.urlopen("https://www.dirtgame.com/us/changeplatform?platform=playstationnetwork")
         
      if enabled:
         html = urllib2.urlopen( "https://www.dirtgame.com/us/api/event?eventId="+eventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=" + str(stageNum) ).read()
         event=json.loads(html)
         stages[x]['name'] = (event.get('StageName'))
         stages[x]['time'] = (event.get('TimeOfDay'))
         #print event
         if debug:
            print event
            
         #get the total number of entries
         if stageNum == 1:
            
            #build a list of dictionaries 
            if y == 0:
               for i in range (0, totalPCEntries):
                  #save the name and vehicle of player
                  entries[i]['name'] = event.get('Entries')[i].get('Name')
                  entries[i]['car']  = event.get('Entries')[i].get('VehicleName')
                  entries[i]['device'] = device
                  entries[i]['sortingTime'] = 0
            elif y == 1:
               for i in range (0, totalXboxEntries):
                  
                  #save the name and vehicle of player
                  entries[i+totalPCEntries]['name'] = event.get('Entries')[i].get('Name')
                  entries[i+totalPCEntries]['car']  = event.get('Entries')[i].get('VehicleName')
                  entries[i+totalPCEntries]['device'] = device
                  entries[i]['sortingTime'] = 0
            elif y == 2:
               for i in range (0, totalPsEntries):
                  
                  #save the name and vehicle of player
                  entries[i+totalPCEntries+totalXboxEntries]['name'] = event.get('Entries')[i].get('Name')
                  entries[i+totalPCEntries+totalXboxEntries]['car']  = event.get('Entries')[i].get('VehicleName')
                  entries[i+totalPCEntries+totalXboxEntries]['device'] = device
                  entries[i]['sortingTime'] = 0
            
            #print the entry list
            if debug:
               print entries
            
         #get the number of entries for this stage
         stageEntries = len(event.get('Entries'))
         
         #loops through all entries for this stage
         for i in range (0, stageEntries):
            
            #retrieves the name
            name = event.get('Entries')[i].get('Name')
            
            #todo: This could probably be made better
            #iterates though the player list to find
            #which player matches the name retrieved
            for j in range (0, totalEntries):
               if 'name' in entries[j]:
                  #if the name matches this entry save the time
                  if name == entries[j]['name']:
                     entries[j][str(stageNum)] = event.get('Entries')[i].get('Time')
                     
                     #penalize players who have not completed the rally
                     entries[j]['sortingTime'] = (numStages-stageNum)*600+timeToSeconds(event.get('Entries')[i].get('Time'))
                     
                     #compute diff times
                     if stageNum == 1:
                        entries[j][str(stageNum)+"RawTime"] = timeToSeconds(event.get('Entries')[i].get('Time'))
                     else:
                        entries[j][str(stageNum)+"RawTime"] = timeToSeconds(event.get('Entries')[i].get('Time')) -  timeToSeconds(entries[j][str(stageNum-1)])

                        
f = open('data.csv', 'w')
#sort by times
sortedEntries = sorted(entries, key=lambda k: k['sortingTime']) 
#write names to file
f.write(', , , ')
for j in range (0, totalEntries):
   found = False
   for k in range (0, len(names.get('names'))):
      if names.get('names')[k].get('id') == sortedEntries[j]['name']:
         f.write(names.get('names')[k].get('name')+", " +str(j+1)+", ")
         found = True
   if found != True:
      f.write(sortedEntries[j]['name']+", " +str(j+1)+", ")
f.write('\n')

#write car name to file
f.write(', , Fastest, ')
for j in range (0, totalEntries):
  f.write(sortedEntries[j]['car'] +", "+sortedEntries[j]['device']+", ")
f.write('\n')

#write stage names and the result of each stage
for x in range(0, numStages):
   
   #find fastest time
   fastestTime = 999999999
   fastestPlayer = 99999999
   for j in range (0, totalEntries):
      if str(x+1) in sortedEntries[j]:
         if timeToSeconds(sortedEntries[j][str(x+1)]) < fastestTime:
            fastestTime = timeToSeconds(sortedEntries[j][str(x+1)])
            fastestPlayer = j

   #write stage name
   f.write(stages[x]['name']+', ' + stages[x]['time'] +', ' + secondsToPrintable(fastestTime) +', ')
   for j in range (0, totalEntries):
      if str(x+1) in sortedEntries[j]:
         
         #compute difference from fastest time
         diff = timeToSeconds(sortedEntries[j][str(x+1)]) - fastestTime
         #write the players result if they have one
         f.write(sortedEntries[j][str(x+1)]+", " + secondsToPrintable(diff)+", ")

         
      else:

         #write a blank space if there is no time for this player
         f.write(", , ")
   f.write('\n')
f.write('\n')


#write stage names and the split times of each stage
f.write(', , Fastest\n')
for x in range(0, numStages):
   
   #find fastest time
   fastestTime = 999999999
   fastestPlayer = 99999999
   for j in range (0, totalEntries):
      if str(x+1) in sortedEntries[j]:
         if sortedEntries[j][str(x+1) +"RawTime"] < fastestTime:
            fastestTime = sortedEntries[j][str(x+1) +"RawTime"]
            fastestPlayer = j

   #write stage name
   f.write(stages[x]['name']+', ' + stages[x]['time'] +', ' + secondsToPrintable(fastestTime) +', ')
   for j in range (0, totalEntries):
      if str(x+1) in sortedEntries[j]:
         #compute difference from fastest time
         diff = sortedEntries[j][str(x+1) +"RawTime"] - fastestTime
         #write the players result if they have one
         f.write(secondsToPrintable(sortedEntries[j][str(x+1) +"RawTime"]) +', ' + secondsToPrintable(diff) +', ')
      else:

         #write a blank space if there is no time for this player
         f.write(", , ")
   f.write('\n')
f.write('\n')

