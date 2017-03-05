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

import urllib2
import json
from decimal import Decimal
import csv
import sys

reload(sys)
sys.setdefaultencoding('latin-1')

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


f = open('data.csv', 'w')
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
html = urllib2.urlopen( "https://www.dirtgame.com/uk/api/event?eventId="+pcEventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=0").read()
event=json.loads(html)
numStages = event.get('TotalStages')
stages=[dict() for x in range(numStages)]

#get the number of entries for each platform
if pcEnabled:
   html = urllib2.urlopen( "https://www.dirtgame.com/uk/api/event?eventId="+pcEventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=1" ).read()
   event=json.loads(html)
   totalPCEntries = len(event.get('Entries'))
else:
   totalPCEntries = 0
   
if xboxEnabled:
   html = urllib2.urlopen( "https://www.dirtgame.com/uk/api/event?eventId="+xboxEventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=1" ).read()
   event=json.loads(html)
   totalXboxEntries = len(event.get('Entries'))
else:
   totalXboxEntries = 0
   
if psEnabled:
   html = urllib2.urlopen( "https://www.dirtgame.com/uk/api/event?eventId="+psEventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=1" ).read()
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
      elif y == 1: 
         enabled = xboxEnabled
         eventID = xboxEventID
         device  = 'Xbox'
      elif y == 2: 
         enabled = psEnabled
         eventID = psEventID
         device  = 'PS4'
         
      if enabled:
         html = urllib2.urlopen( "https://www.dirtgame.com/uk/api/event?eventId="+eventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=" + str(stageNum) ).read()
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
            elif y == 1:
               for i in range (0, totalXboxEntries):
                  
                  #save the name and vehicle of player
                  entries[i+totalPCEntries]['name'] = event.get('Entries')[i].get('Name')
                  entries[i+totalPCEntries]['car']  = event.get('Entries')[i].get('VehicleName')
                  entries[i+totalPCEntries]['device'] = device
            elif y == 2:
               for i in range (0, totalPsEntries):
                  
                  #save the name and vehicle of player
                  entries[i+totalPCEntries+totalXboxEntries]['name'] = event.get('Entries')[i].get('Name')
                  entries[i+totalPCEntries+totalXboxEntries]['car']  = event.get('Entries')[i].get('VehicleName')
                  entries[i+totalPCEntries+totalXboxEntries]['device'] = device
            
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
               
               #if the name matches this entry save the time
               if name == entries[j]['name']:
                  entries[j][str(stageNum)] = event.get('Entries')[i].get('Time')
                  
                  #compute diff times
                  if stageNum == 1:
                     entries[j][str(stageNum)+"RawTime"] = timeToSeconds(event.get('Entries')[i].get('Time'))
                  else:
                     entries[j][str(stageNum)+"RawTime"] = timeToSeconds(event.get('Entries')[i].get('Time')) -  timeToSeconds(entries[j][str(stageNum-1)])

#write names to file
f.write(', , ')
for j in range (0, totalEntries):
  f.write(entries[j]['name']+", " + entries[j]['device'] +", ")
f.write('\n')

#write car name to file
f.write(', , ')
for j in range (0, totalEntries):
  f.write(entries[j]['car']+", , ")
f.write('\n')

#write stage names and the result of each stage
for x in range(0, numStages):
   
   #write stage name
   f.write(stages[x]['name']+', ' + stages[x]['time'] +', ')
   for j in range (0, totalEntries):
      if str(x+1) in entries[j]:
         
         #write the players result if they have one
         f.write(entries[j][str(x+1)]+", , ")
      else:

         #write a blank space if there is no time for this player
         f.write(", , ")
   f.write('\n')
f.write('\n')


#write stage names and the split times of each stage
for x in range(0, numStages):
   
   #write stage name
   f.write(stages[x]['name']+', ' + stages[x]['time'] +', ')
   for j in range (0, totalEntries):
      if str(x+1) in entries[j]:
         
         #write the players result if they have one
         f.write(secondsToPrintable(entries[j][str(x+1) +"RawTime"]) + ", , ")
      else:

         #write a blank space if there is no time for this player
         f.write(", , ")
   f.write('\n')
f.write('\n')

