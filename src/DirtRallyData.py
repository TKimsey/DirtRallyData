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

import csv
f = open('data.csv', 'w')
debug = False

#todo: Find how to get this automatically
#racenet event id
eventID = '204698'
totalEntries = 0

#get the number of stages
html = urllib2.urlopen( "https://www.dirtgame.com/uk/api/event?eventId="+eventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=0").read()
event=json.loads(html)
numStages = event.get('TotalStages')

stages=[]

#get the results for each stage
for x in range(0, numStages):

   stageNum = x + 1
   html = urllib2.urlopen( "https://www.dirtgame.com/uk/api/event?eventId="+eventID+"&group=all&leaderboard=true&nameSearch=&noCache=1&page=1&stageId=" + str(stageNum) ).read()
   event=json.loads(html)
   stages.append(event.get('StageName') )
   
   #print event
   if debug:
      print event
      
   #get the total number of entries
   if stageNum == 1:
      totalEntries = len(event.get('Entries'))
      entries = [dict() for x in range(totalEntries)]
      
      #build a list of dictionaries 
      for i in range (0, totalEntries):
         
         #save the name and vehicle of player
         entries[i]['name'] = event.get('Entries')[i].get('Name')
         entries[i]['car']  = event.get('Entries')[i].get('VehicleName')
      
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

#write names to file
f.write(', , ')
for j in range (0, totalEntries):
  f.write(entries[j]['name']+", ")
f.write('\n')

#write car name to file
f.write(', , ')
for j in range (0, totalEntries):
  f.write(entries[j]['car']+", ")
f.write('\n')

#write stage names and the result of each stage
for x in range(0, numStages):
   
   #write stage name
   f.write(stages[x]+', , ')
   for j in range (0, totalEntries):
      if str(x+1) in entries[j]:
         
         #write the players result if they have one
         f.write(entries[j][str(x+1)]+", ")
   f.write('\n')
f.write('\n')

