#The program gets data from the blue alliance api which has a list of all the
#frc robotics events including matches, participants, scores, and other basic data
#With this data it allow the user to enter a team number and the year to get the data from
#and it outputs Average score and win loss ratio. With each iteration it adds the data
#to the chart and sorts by average score allowing the user to see the best teams

import requests
import time
App_ID='Aria:GOA:1'

class Team:
    #Calls team API to extract and save data from their libraries
    def __init__ (self, teamNum):
        url = 'http://www.thebluealliance.com/api/v2/team/frc'+str(teamNum)
        param = { 'X-TBA-App-Id': App_ID }
        try:
            r = requests.get(url, params=param)
            #print(r.content)
            self.data=r.json()
        except:
            print("Error getting data for team or team does not exist")
            self.data=None

    def getName(self):
        return self.data['name']

    def getKey(self):
        return self.data['key']
        
    def isValid(self):
        return self.data is not None

class Matches:
    #Calls event API to get all matches for an event
    def __init__ (self, eventKey):
        url = 'http://www.thebluealliance.com/api/v2/event/'+str(eventKey)+'/matches'
        param = { 'X-TBA-App-Id': App_ID }
        try:
            r = requests.get(url, params=param)
            #print(r.content)
            self.data=r.json()
        except:
            print("Error getting data for event or team does not exist")
            self.data=None
        if self.numOfMatches()==0:
            print("Team participated in no matches that year")
            self.data=None
                           
    def numOfMatches(self):
        return len(self.data)

    def getMatchNumber(self,matchNum):
        return self.data[matchNum]['match_number']

    #returns score if team is in the match or -1 if team isnt
    #Precondition: team is a valid Team object
    def getScoreInMatch(self,matchNum,team):
        match=self.data[matchNum]
        if team.getKey() in match['alliances']['blue']['teams']:
            return match['alliances']['blue']['score']
        elif team.getKey() in match['alliances']['red']['teams']:
            return match['alliances']['red']['score']
        else:
            return -1

    #In FRC ties count as losses
    def didTeamWin(self,matchNum,team):
        match=self.data[matchNum]
        allyScore=self.getScoreInMatch(matchNum,team)
        oppScore=0
        oppColor='blue'
        if team.getKey() in match['alliances']['blue']['teams']:
            oppColor='red'
        oppScore=match['alliances'][oppColor]['score']
        return oppScore<allyScore

    def isValid(self):
        return self.data is not None

class Events:
    #Calls event API to get all events the team participated in the given year
    def __init__ (self, teamNum, year):
        url = 'http://www.thebluealliance.com/api/v2/team/frc'+str(teamNum)+'/'+str(year)+'/events'
        param = { 'X-TBA-App-Id': App_ID }
        try:
            r = requests.get(url, params=param)
            self.data=r.json()
            if self.numOfEvents()==0: 
                print("Team participated in no events that year")
                self.data=None
            elif type(self.data) is not list: #for example team 2138 gets a 404 error in a dictionary
                print("Error getting data for event or team does not exist")
                self.data=None
            else:
                #for each event load the matches for it and store them as a list in the event dictionary
                for event in self.data:
                    matches = Matches(event['key'])  
                    if matches.isValid():
                        event['matches']=matches
        except: #for some reason there are two different ways of getting an error if a team is not found (an exception or a 404 error)
            print("Error getting data for event or team does not exist")
            self.data=None

    def numOfEvents(self):
        return len(self.data)

    def getName(self, eventNum):
        return self.data[eventNum]['name']

    def getMatches(self, eventNum):
        return self.data[eventNum]['matches']

    def isValid(self):
        return self.data is not None

#Makes sure user inputs a number
def getNumberFromUser(prompt):
    valid=False
    while not valid:
        try:
            number=int(input(prompt))
            valid=True
        except ValueError:
            print("That's not a number")
    return number

#Basically does everything... calls all helper methods to calculate statistics displayed later
def doEverything(teamNumber,year):
    #Loads data
    team = Team(teamNumber)
    if not team.isValid():
        return None
    #print("Name: " + team.getName()) uncomment if you want to see
    events = Events(teamNumber,year)
    if not events.isValid():
        return None

    #Calculates stats
    totalMatches=0
    totalPoints=0
    wins=0
    losses=0
    for i in range(0,events.numOfEvents()): #Gets all events team attended
        matches=events.getMatches(i)
        for j in range(0,matches.numOfMatches()): #Gets all matches in given event
            score=matches.getScoreInMatch(j,team)
            if score!=-1: #Increments total matches and total points if they played in said match
                totalMatches+=1
                totalPoints+=score
                if matches.didTeamWin(j,team):
                    wins+=1
                else:
                    losses+=1

    #Creates stats dictionary to return
    average = totalPoints/totalMatches if totalMatches>0 else 0
    winLossRatio = str(wins)+':'+str(losses)
    matchStats = {'team':teamNumber,'year':year,'avg_score':average,'w_l_ratio':winLossRatio}
    return matchStats

def printStats(stats):
    print('%-5s %-5s %-10s %-7s' %('TEAM','YEAR','AVG SCORE','WIN:LOSS RATIO'))
    for stat in stats:
        print('%-5d %-5d %-10.2f %-7s' %(stat['team'],stat['year'],stat['avg_score'],stat['w_l_ratio']))
    

#Main processing loop
#Keeps a tally of all the main stats after recieving user input for the year and team number
#and prints it out in a readable format
repeat=True
stats=[] #Creates a list to be filled with dictonaries of each teams' stats
allInputs=[]
while (repeat):
    teamNumber=getNumberFromUser("Enter a valid team number: ")
    year=getNumberFromUser("Enter the year you want to get the data from: ")
    #(The challenges change each year which is why the points will vary so dramatically across years)
    
    x = (teamNumber, year)
    if x in allInputs:
        print("You've already seen the stats for "+str(teamNumber)+" in "+str(year))
    else:
        allInputs.append(x) #Keep track of all inputs
        stat=doEverything(teamNumber,year)
        if stat is not None:
            stats.append(stat)
            printStats(sorted(stats, key = lambda x: x['avg_score'], reverse=True)) #prints list after being sorted by avg score descending
            
    #user input to repeat
    answer=input("Again? [Y/N]: ")
    if answer!='Y' and answer!='y':
        repeat=False
 




