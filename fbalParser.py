#! /usr/bin/env python

###########
# Imports #
###########

# Python
import urllib2
import smtplib
import time
import datetime
import sys 
import os 
import subprocess

#from matplotlib import pyplot

# Classes
import Bid
import Player
import Team
import Sorter

#############
# Functions #
#############
def readValueList(fileName, posFlag):
    #---------------
    # Open the file
    #---------------
    f = open(fileName)

    #---------------
    # Read the lines
    #---------------
    valueLines = f.readlines()

    #---------------------------
    # Create the list of players
    #---------------------------
    firstLine  = True
    playerList = []
    dictKeys   = []

    for line in valueLines:

        tokens = line.split(",")

        #--------------------------------------
        # Get the headers if its the first line
        #--------------------------------------
        if firstLine:
            for t in tokens:
                dictKeys.append(t.split("\n")[0])
            firstLine = False
        else:
            #-----------------------------------------
            # Otherwise, create a new dictionary for
            # the player and add it to the player list
            #-----------------------------------------
            index   = 0
            newDict = {}

            for key in dictKeys:
                newDict[key] = tokens[index].split("\n")[0]
                index += 1

            #----------------------
            # Create the new player
            #----------------------
            newPlayer = Player.Player(playerDict=newDict, posFlag=posFlag)

            #-------------------------------
            # Add the new player to the list
            #-------------------------------
            idx = newPlayer.exists(playerList)

            if idx != None:
                playerList[idx].pos.append(newPlayer.pos[0])
                playerList[idx].avgValue.append(newPlayer.avgValue[0])
                playerList[idx].infValue.append(newPlayer.infValue[0])

                playerList[idx].posDict[newPlayer.pos[0]] = newPlayer.avgValue[0]
            else:
                playerList.append(newPlayer)

    #-----------------------------------------
    # Determine the best value for each player
    #-----------------------------------------
    for player in playerList:
        # Find the max value for the surplus calcution
        maxVal = -1
        for val in player.avgValue:
            if val > maxVal:
                maxVal = val

        # Save the relevant attributes
        player.bestValue = maxVal

    #--------------------------------------------
    # Determine the best position for each player
    #--------------------------------------------
    for player in playerList:
        for pos in player.pos:
            if int(player.bestValue) == int(player.posDict[pos]):
                player.bestPos = pos

    return playerList

def readKeeperFile(fileName, hitterList, pitcherList):
    #---------------
    # Open the file
    #---------------
    f = open(fileName)

    #---------------
    # Read the lines
    #---------------
    keepers = f.readlines()

    #-----------------------------------
    # Read the file and create the teams
    #-----------------------------------
    for keeper in keepers:
        #-------------------------------------------------------------
        # Split on the commas then split the second part on the spaces
        #-------------------------------------------------------------
        splitComma  = keeper.split(",")
        splitSpaces = splitComma[1].strip().split(" ")
        
        #-------------------
        # Get the attributes
        #-------------------
        fbalTeam  = splitComma[0].strip()
        firstName = splitSpaces[0].strip()
        lastName  = splitSpaces[1].strip()
        pos       = splitSpaces[2].strip()
        mlbTeam   = splitSpaces[3].strip()
        cost      = int(splitSpaces[4])

        #-----------------------------------
        # Create a bid object for the player
        #-----------------------------------
        bid = Bid.Bid(fbalTeam, pos, "", cost)

        #------------------------------------------------
        # If the player exists, save the cost. Otherwise,
        # create a new player object and save it
        #------------------------------------------------
        found = False

        if pos in ["SP", "RP"]:
            searchList = pitcherList
            posFlag    = "pitcher"
        elif pos in ["PEN"]:
            searchList = []
        else:
            searchList = hitterList
            posFlag    = "hitter"

        for player in searchList:
            if firstName.strip() == player.firstName.strip():
                if lastName.strip() == player.lastName.strip():
                    if pos.strip() in player.pos:
                        player.cost      = cost
                        player.surplus   = player.bestValue - player.cost
                        player.fbalTeam  = fbalTeam
                        player.mlbTeam   = mlbTeam
                        player.bestPos   = pos
                        player.bid       = bid

                        # Trigger the end of the loop
                        found           = True

        if not found:
            newPlayer = Player.Player(posFlag=posFlag, firstName=firstName, lastName=lastName, pos=pos, mlbTeam=mlbTeam, fbalTeam=fbalTeam, cost=cost)

            newPlayer.bid = bid

            if pos == "PEN":
                hitterList.append(newPlayer)
            else:
                searchList.append(newPlayer)

def parseBoard(rootUrl, year):
    #----------------------
    # Get the root URL page
    #----------------------
    rootUrlData = urllib2.urlopen(rootUrl).readlines()

    """
    Find the positional URLs
    """
    #-----------------------------------------------
    # first find the lines in the HTLML that we want
    #-----------------------------------------------
    linesWithPosUrl = []

    for line in rootUrlData:
        if line.count(year + " Catchers")          > 0: linesWithPosUrl.append(line)
        if line.count(year + " First Base")        > 0: linesWithPosUrl.append(line)
        if line.count(year + " Second Base")       > 0: linesWithPosUrl.append(line)
        if line.count(year + " Third Base")        > 0: linesWithPosUrl.append(line)
        if line.count(year + " Shortstops")        > 0: linesWithPosUrl.append(line)
        if line.count(year + " Outfielders")       > 0: linesWithPosUrl.append(line)
        if line.count(year + " Starting Pitchers") > 0: linesWithPosUrl.append(line)
        if line.count(year + " Relief Pitchers")   > 0: linesWithPosUrl.append(line)
        if line.count(year + " Bargain Bin")       > 0: linesWithPosUrl.append(line)

    #------------------------------------------------
    # Now Assemble the positional URLs from the lines
    #------------------------------------------------
    posUrls = []

    for line in linesWithPosUrl:
        #---------------------------------
        # Do the nescessary string parsing
        #---------------------------------
        splitOnQuotes     = line.split("\"")
        splitOnQMark      = splitOnQuotes[3].split("?")
        splitOnSemiColon  = splitOnQMark[-1].split(";")
        posUrl            = splitOnQMark[0] + "?" + splitOnSemiColon[-1]

        #-----------------
        # Save off the URL
        #-----------------
        #print posUrl
        posUrls.append(posUrl)

    """
    Parse the Player Pages
    """

    #-------------------------------------------------------------------
    # Loop over the main pages filling up the Bid structs where possible
    #-------------------------------------------------------------------
    print "+--------+"
    print "| Status |"
    print "+--------+"
    bidList = []
    cnt     = 0

    for posUrl in posUrls:
        #--------------------------------------
        # Set the pos variable and print status
        #--------------------------------------
        if cnt == 0: pos = "C"
        if cnt == 1: pos = "1B"
        if cnt == 2: pos = "2B"
        if cnt == 3: pos = "3B"
        if cnt == 4: pos = "SS"
        if cnt == 5: pos = "OF"
        if cnt == 6: pos = "SP"
        if cnt == 7: pos = "RP"
        if cnt == 8: pos = "BB"

        print "Parsing %s..." % (pos)

        cnt += 1

        #----------------------------
        # Get the positional URL data
        #----------------------------
        posUrlData = urllib2.urlopen(posUrl).readlines()

        #---------------------------------------------
        # Create a bid object and fill in what you can
        #---------------------------------------------
        for iii in range(len(posUrlData)):
            #-------------
            # Get the line
            #-------------
            line = posUrlData[iii]

            #-------------------------
            # See if the line is a bid
            #-------------------------
            if line.count("This topic was started:") > 0 and line.count("Pinned") == 0:
                #----------------------------------------
                # Pull out what you can from the bid line
                #----------------------------------------
                splitLine = line.split("\"")
                #url       = splitLine[1].split("?")[0] + "?" + splitLine[1].split(";")[-1] + "&st=15"
                url       = splitLine[1].split("?")[0] + "?" + splitLine[1].split(";")[-1] + "&st=0&#last"
                tag       = (splitLine[-1])[1:-7]

                #print url

                #------------------
                # Get the team name
                #------------------
                jjj  = iii + 5
                team = None

                if jjj < len(posUrlData):
                    #-----------------------
                    # Get the team name line
                    #-----------------------
                    teamNameLine = posUrlData[jjj]

                    #------------------
                    # Get the team name
                    #------------------
                    splitTeamNameLine = teamNameLine.split(">")
                    team              = splitTeamNameLine[-5][:-3]
                    #print team
                else:
                    print "Warning: No team name line for %s" % (tag)

                #------------------------
                # Create a new Bid object
                #------------------------
                bid = Bid.Bid(team, pos, url)

                #-=----------------------------------------
                # Parse the tag for name/pos info
                #
                # Note: This fills in first, last, and pos
                #-=----------------------------------------
                bid.parseTag(tag)

                #---------------------------------------------------------
                # Put the players that are handled in the keeper file here
                #---------------------------------------------------------
                """
                if bid.lastName == "" and bid.firstName == "": continue
                """
		if bid.lastName.count("Day"): 
		    print "Warning: Changing %s %s to Darren O\'Day" % (bid.firstName, bid.lastName)
		    bid.firstName = "Darren"
		    bid.lastName  = "O'Day"
		
		if bid.lastName == "Odor" and bid.firstName == "Rougned": continue
		if bid.lastName == "Gausman" and bid.firstName == "Kevin": continue
		if bid.lastName == "Leake" and bid.firstName == "Mike": continue
		if bid.lastName == "Zimmerman" and bid.firstName == "Jordan":
	            print "Fixing Jordan Zimmermann spelling" 
		    bid.lastName == "Zimmermann"
			

                #-----------------
                # Get the bid data
                #-----------------
                data = urllib2.urlopen(url).readlines()

                #---------------------
                # Gather the bid lines
                #---------------------
                bidLines = []

                for dataLine in data:
                    if dataLine.count("<div class='postcolor'>") > 0:
                        bidLines.append(dataLine)

                #print bid.lastName + ":" + str(len(bidLines))

                #--------------------------------------------------------
                # If there weren't any bid lines, this guy doesn't matter
                #--------------------------------------------------------
                #if len(bidLines) == 1:
                #    bid.value = 0
                #    bid.active = True
                #    continue

                #------------------
                # Find the bid time
                #------------------
                timeLines = []

                for dataLine in data:
                    if dataLine.count("Posted:") > 0:
                        timeLines.append(dataLine)

                bid.findBidTime(timeLines)

                #-------------------------
                # Get the value of the bid
                #-------------------------
                #if len(bidLines) > 0:
                bid.getValue(bidLines)

                #-------------------------
                # See if the bid is active
                #-------------------------
                bid.isActive()


                #------------------------
                # Add the bid to the list
                #------------------------
                bidList.append(bid)

    #------
    # Debug
    #------
    print "\n+------------+"
    print "| Tag Errors |"
    print "+------------+"
    for bid in bidList:
        if (bid.firstName == "" and bid.lastName == "" and bid.pos == ""):
            print bid.tag

    print "\n+--------------+"
    print "| Value Errors |"
    print "+--------------+"
    for bid in bidList:
        if bid.value < 0:
            print "%s %s %s: %s" % (bid.firstName, bid.lastName, bid.pos, bid.valueString)

    return bidList

def urlOpen(url):
    command = "curl %s >& tmp.txt" % url
    subprocess.call(command, shell=True)
    url_data = open("tmp.txt", "r").readlines()
    subprocess.call("rm tmp.txt", shell=True)
    return url_data
 
def parseBoard2(rootUrl):
    #-------------------------------------------------------------------
    # Loop over the main pages filling up the Bid structs where possible
    #-------------------------------------------------------------------
    done    = False
    inc      = 0
    bidList  = []
    tag_list = []

    print "+--------+"
    print "| Status |"
    print "+--------+"
    while not done:
        #----------------------
        # Assemble the next URL
        #----------------------
        nextUrl = rootUrl + "/index-s%d.html" % inc
        inc += 255

        #nextUrl = rootUrl
        #print "Parsing Bids: %3d to %3d" % (inc, (inc + 255)-1)

        #----------------------
        # Retrieve the next URL
        #----------------------
        try:
            nextUrlData = urlOpen(nextUrl)
        except urllib2.URLError:
            print "Error: No Internet Connection. Skipping bid parsing."
            return []

        #---------------------------------------------
        # Create a bid object and fill in what you can
        #---------------------------------------------
        numBids = 0

        for iii in range(len(nextUrlData)):
            #-------------
            # Get the line
            #-------------
            line = nextUrlData[iii]

            #-------------------------
            # See if the line is a bid
            #-------------------------
            if line.count("headline") > 0 and not line.count("Auction Rules") and not line.count("How To"):
                #----------------------------------------
                # Pull out what you can from the bid line
                #----------------------------------------
                splitLine = line.split("\"")
                url       = splitLine[3]
                tag       = splitLine[-1].split(">")[1].split("<")[0]
                
                if tag not in tag_list:
                    tag_list.append(tag)
                else:
                    done = True
                    break

                #timeStamp = splitLine[3].split(":")[1].strip() + ":" + splitLine[3].split(":")[-1]
                
                #------------------
                # Get the team name
                #------------------
                jjj = iii + 13

                if jjj < len(nextUrlData):
                    #-----------------------
                    # Get the team name line
                    #-----------------------
                    teamNameLine = nextUrlData[jjj]
                    team = teamNameLine.split(">")[1].split("<")[0]
                else:
                    print "Warning: No team name line for %s" % (tag)
                
                #------------------------
                # Create a new Bid object
                #------------------------
                bid = Bid.Bid(team)
                
                #---------------------------------------------------------------------------
                # Make some manual adjustments to the tags to make sure they parse correctly
                # if tag.count("") > 0: tag = ""
                #---------------------------------------------------------------------------
                if tag.count("Duda") > 0: tag = "Lucas Duda 1B NYM" 
                if tag.count("Senzatela") > 0: tag = "Antonio Senzatela SP COL" 
                if tag.count("Blackmon") > 0: tag = "Charlie Blackmon OF COL"
                if tag.count("Familia") > 0: tag = "Jeurys Familia RP NYM" 
                if tag.count("Scherzer") > 0: tag = "Max Scherzer SP WSH"
                if tag.count("Gyorko") > 0: tag = "Jedd Gyorko SS STL"
                if tag.count("Wacha") > 0: tag = "Michael Wacha SP STL" 
                if tag.count("AJ Ramos") > 0: tag = "A.J. Ramos RP MIA"
                if tag.count("Archer") > 0: tag = "Chris Archer SP TB"
                if tag.count("Ken Giles") > 0: tag = "Ken Giles RP HOU"
                if tag.split(" ")[0] == "PEDRO": tag = "Pedro Strop RP CHC"
                if tag.split(" ")[0] == "DAN": tag = "Daniel Straily SP OAK"
                if tag.count("Jarrod Dyson") > 0: tag = "Jarrod Dyson OF SEA"
                if tag.count("Matt Moore") > 0: tag = "Matt Moore SP SF" 
                if tag.count("Wade Davis") > 0: tag = "Wade Davis RP CHC"
                if tag.count("Tanaka") > 0: tag = "Masahiro Tanaka SP NYY" 
                if tag.count("Velasquez") > 0: tag = "Vincent Velasquez SP PHI"
                if tag.count("LeMahieu") > 0: tag = "DJ LeMahieu 2B COL"
                if tag.count("Schoop") > 0: tag = "Jonathan Schoop 2B BAL"
                if tag.count("Joe Kelly") > 0: tag = "Joe Kelly SP BOS"
                if tag.count("Wily Peralta") > 0: tag = "Wily Peralta SP MIL"
                if tag.count("K. Gibson") > 0: tag = "Kyle Gibson SP MIN"
                if tag.count("Jon Gray") > 0: tag = "Jonathan Gray SP COL"
                if tag.count("Colome") > 0: tag = "Alexander Colome RP TB"
                if tag.count("Jed Lowrie") > 0: tag = "Jed Lowrie 2B OAK"
                if tag.count("Colby") > 0: tag = "Colby Rasmus OF TB"

                #-----------------------------------------
                # Parse the tag for name/pos info
                #
                # Note: This fills in first, last, and pos
                #-=----------------------------------------
                print "Parsing %s" % tag
                bid.parseTag(tag)

                #-----------------
                # Get the bid data
                #-----------------
                data = urlOpen(url)

                #------------------
                # Find the bid time
                #------------------
                timeLines = []

                for dataLine in data:
                    if dataLine.count("datePublished") > 0 or dataLine.count("commentTime"):
                        timeLines.append(dataLine)

                bid.findBidTime(timeLines)
                
                #-------------------------
                # Get the value of the bid
                #-------------------------
                bidLines = []

                for dataLine in data:
                    if dataLine.count("articleBody") > 0 or dataLine.count("commentText"):
                        bidLines.append(dataLine)

                bid.getValue(bidLines)

                if bid.value < 0:
                    print "Value Error: %s" % bid.tag
                
                #-------------------------
                # See if the bid is active
                #-------------------------
                bid.isActive()

                #------------------------
                # Add the bid to the list
                #------------------------
                bidList.append(bid)
    
    #------
    # Debug
    #------
    print "\n+------------+"
    print "| Tag Errors |"
    print "+------------+"
    for bid in bidList:
        if (bid.firstName == "" and bid.lastName == "" and bid.pos == "") or (bid.pos not in ["C", "1B", "2B", "3B", "SS", "OF", "DH", "SP", "RP"]):
            print bid.tag, bid.firstName, bid.lastName, bid.pos, bid.tag.split(" ")

    print "\n+--------------+"
    print "| Value Errors |"
    print "+--------------+"
    for bid in bidList:
        if bid.value <= 0:
            print "%s %s %s" % (bid.firstName, bid.lastName, bid.pos)

    return bidList

def isValid(team):
    if   team.strip() == "Crumpton Roches":             return True
    elif team.strip() == "Balmer Bruisers":             return True
    elif team.strip() == "Bi-Racial Angels":            return True
    elif team.strip() == "Wishful Thinking":            return True
    elif team.strip() == "Crimson Coots":               return True
    elif team.strip() == "Unbereevable&#33;&#33;&#33;": return True
    elif team.strip() == "mike2bike527":                return True
    elif team.strip() == "True Romance":                return True
    elif team.strip() == "Blazing Brits":               return True
    elif team.strip() == "The Lil Emperors":            return True
    elif team.strip() == "Show Me Yo TDs":              return True
    elif team.strip() == "Baltimore Boh Diggity":       return True
    else:
        print "Invalid Team Name: %s" % (str(team))
        return False

####################
# Sorting Routines #
####################

def sortPlayers(a, b):
    if a.value < b.value:  return 1
    if a.value == b.value: return 0
    else: return -1

def sortToTeams(hitterList, pitcherList):
    #-------------------------
    # Create a team dictionary
    #-------------------------
    teamDict = {}

    # Hitters
    for player in hitterList:
        if player.fbalTeam == None: continue
        if player.cost     == 0:    continue
        if player.cost     == -2:   player.cost = 0

        #if isValid(player.fbalTeam.strip()):
        if player.fbalTeam.strip() in teamDict.keys():
            teamDict[player.fbalTeam.strip()].append(player)
        else:
            teamDict[player.fbalTeam.strip()] = []
            teamDict[player.fbalTeam.strip()].append(player)

    # Pitchers
    for player in pitcherList:
        if player.fbalTeam == None: continue
        if player.cost     == 0:    continue
        if player.cost     == -2:   player.cost = 0

        #if isValid(player.fbalTeam.strip()):
        if player.fbalTeam.strip() in teamDict.keys():
            teamDict[player.fbalTeam.strip()].append(player)
        else:
            teamDict[player.fbalTeam.strip()] = []
            teamDict[player.fbalTeam.strip()].append(player)

    #-------------------------------
    # Create the team structure list
    #-------------------------------
    teamList = []

    for key in teamDict.keys():
        teamList.append(Team.Team(key, teamDict[key]))

    return sorted(teamList, Sorter.sortTeamsBySurplus)

# def sortTeamsBySurplus(a,b):
#     if a.surplus < b.surplus:  return 1
#     if a.surplus == b.surplus: return 0
#     else: return -1
#
# def sortTeamsByRemaining(a,b):
#     if a.remaining < b.remaining:  return 1
#     if a.remaining == b.remaining: return 0
#     else: return -1
#
# def sortTeamsByRosterSize(a,b):
#     if a.numPlayers <  b.numPlayers:  return 1
#     if a.numPlayers == b.numPlayers: return 0
#     else: return -1
#
# def sortByPlayerValue(a,b):
#     if a.avgValue[0] <  b.avgValue[0]:  return 1
#     if a.avgValue[0] == b.avgValue[0]: return 0
#     else: return -1

def analyzeAuction(hitterList, pitcherList):
    #-----------
    # Initialize
    #-----------
    expectedSpending = {}
    actualSpending   = {}
    expectedTotal    = 0
    actualTotal      = 0

    #-----------------------------------------
    # Compute the expected and actual spending
    #-----------------------------------------
    playerList = hitterList + pitcherList

    totalHitters  = 0
    totalPitchers = 0

    for player in playerList:
        #------------------
        # Expected Spending
        #------------------
        for pos in player.posDict.keys():
            if pos.upper() in expectedSpending.keys():
                expectedSpending[pos.upper()] += player.posDict[pos]
                expectedTotal                 += player.posDict[pos]
            else:
                expectedSpending[pos.upper()]  = 0
                expectedSpending[pos.upper()] += player.posDict[pos]
                expectedTotal                 += player.posDict[pos]

	expectedSpending["PEN"] = 0

        #----------------
        # Actual Spending
        #----------------
        if player.cost > 0:
            if player.bestPos.upper() in actualSpending.keys():

                if   player.bestPos in ["BB","PEN"]: continue
                elif player.bestPos in ["SP","RP"]:  totalPitchers += player.cost
                else:                                totalHitters  += player.cost

                actualSpending[player.bestPos.upper()] += player.cost
                actualTotal                            += player.cost
            else:
                actualSpending[player.bestPos.upper()]  = 0
                actualSpending[player.bestPos.upper()] += player.cost
                actualTotal                            += player.cost

    #print "+------------------+"
    #print "\nAuction Analysis"
    #print "+------------------+"
    print "\nPos Exp  Act  Exp%  Act%"
    for key in ["C","1B","2B","3B","SS","OF","SP","RP","DH","PEN"]:
        if key in actualSpending.keys():
            print "%3s %4d %4d %.2f %.2f" % (key, int(expectedSpending[key]), int(actualSpending[key]), float(expectedSpending[key]) / expectedTotal, float(actualSpending[key]) / actualTotal)
        else:
            print "%3s %4d %4d %.2f %.2f" % (key, int(expectedSpending[key]), int(0), float(expectedSpending[key]) / expectedTotal, float(0) / actualTotal)
    print "%3s %4d %4d %2.2f %2.2f\n" % ("TOT", expectedTotal, actualTotal, float(totalHitters)/actualTotal, float(totalPitchers)/actualTotal)
    #print totalHitters
    #print totalPitchers

def printAuctionReport(fileName, playerList, inflationRate, hoursTilCheck=None):
    #--------------
    # Open the file
    #--------------
    ofile = open(fileName, "w")

    #-------------------
    # Set up the headers
    #-------------------
    ofile.write("##,")
    ofile.write("First,")
    ofile.write("Last,")
    ofile.write("Pos,")
    ofile.write("Team,")
    ofile.write("H.W,")
    ofile.write("HR.L,")
    ofile.write("SB.K,")
    ofile.write("R.QS,")
    ofile.write("RBI.SV,")
    ofile.write("BA.HD,")
    ofile.write("OBP.ERA,")
    ofile.write("SLG.WHIP,")
    ofile.write("OPS,")
    ofile.write("Last,")
    ofile.write("Orig,")
    ofile.write("Inf,")
    ofile.write("Bid,")
    ofile.write("S+,")
    ofile.write("Act,")
    ofile.write("Time,")
    ofile.write("Team\n")

    #----------------------------------------------------------
    # Print the bids set to expire before the next time i check
    #----------------------------------------------------------
    if hoursTilCheck: 
    	now       = datetime.datetime.now()
    	nextCheck = now + datetime.timedelta(hours=hoursTilCheck)

    	rank = 1
   	ofile.write("BNT\n")
    
    surplusList = sorted(playerList, Sorter.sortPlayersBySurplus)
            
    for player in surplusList:
	if not hoursTilCheck: break

        if player.bid != None:
            #-----------------------------------------------------
            # If the players bid is -1 at this point, he is active
            #-----------------------------------------------------
            if player.bid.value == -1:
                player.bid.active = True
        
	    if player.bid.time:         
            	expireTime = player.bid.time + datetime.timedelta(days=1)
	    else:
		continue

            if player.bid.active and (nextCheck > expireTime):
                # print the id info
                ofile.write(str(rank)                   + ",")
                ofile.write(player.firstName            + ",")
                ofile.write(player.lastName             + ",")
                ofile.write(player.bestPos              + ",")
                ofile.write(player.mlbTeam              + ",")
    
                # print the stats
                if player.bestPos in ["SP", "RP"]:
                    ofile.write(str(player.w)             + ",")
                    ofile.write(str(player.l)             + ",")
                    ofile.write(str(player.k)             + ",")
                    ofile.write(str(player.qs)            + ",")
                    ofile.write(str(player.sv)            + ",")
                    ofile.write(str(player.hld)           + ",")
                    ofile.write("%1.2f," % (player.era))
                    ofile.write("%1.2f," % (player.whip))
                    ofile.write(str(0)                    + ",")
                elif player.bestPos in ["BB"]:
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                else: #hitters
                    ofile.write(str(player.h)             + ",")
                    ofile.write(str(player.hr)            + ",")
                    ofile.write(str(player.sb)            + ",")
                    ofile.write(str(player.r)             + ",")
                    ofile.write(str(player.rbi)           + ",")
                    ofile.write("%.3f," % (player.avg))
                    ofile.write("%.3f," % (player.obp))
                    ofile.write("%.3f," % (player.slg))
                    ofile.write("%.3f," % (player.ops))

                # print the financial info
                ofile.write("$%d,"  % (int(float(player.prevValue))))
                ofile.write("$%d,"  % (int(player.bestValue)))
                ofile.write("$%d,"  % (int(player.bestValue * inflationRate)))

                # print the bid info
                if player.bid != None:
                    if int(player.bid.value) == -1:
                        ofile.write("$0,")
                    else:
                        ofile.write("$%d," % (int(player.bid.value)))
                    if player.surplus != None:
                        ofile.write("%d,"  % (player.surplus))
                    else:
                        ofile.write(",")
                    ofile.write("%d," % (int(player.bid.active)))
                    ofile.write(str(player.bid.time)     + ",")
                    ofile.write(str(player.bid.fbalTeam) + "\n")
                else:
                    ofile.write("\n")

                # increment the rank counter
                rank += 1

    ofile.write("\n") 

    #----------------------
    # Print the active bids
    #----------------------
    rank = 1
    ofile.write("ACT\n")

    surplusList = sorted(playerList, Sorter.sortPlayersBySurplus)

    for player in surplusList:
        if player.bid != None:
            #-----------------------------------------------------
            # If the players bid is -1 at this point, he is active
            #-----------------------------------------------------
            if player.bid.value == -1:
                player.bid.active = True

            if player.bid.active:
                # print the id info
                ofile.write(str(rank)                   + ",")
                ofile.write(player.firstName            + ",")
                ofile.write(player.lastName             + ",")
                ofile.write(player.bestPos              + ",")
                ofile.write(player.mlbTeam              + ",")

                # print the stats
                if player.bestPos in ["SP", "RP"]:
                    ofile.write(str(player.w)             + ",")
                    ofile.write(str(player.l)             + ",")
                    ofile.write(str(player.k)             + ",")
                    ofile.write(str(player.qs)            + ",")
                    ofile.write(str(player.sv)            + ",")
                    ofile.write(str(player.hld)           + ",")
                    ofile.write("%1.2f," % (player.era))
                    ofile.write("%1.2f," % (player.whip))
                    ofile.write(str(0)                    + ",")
                elif player.bestPos in ["BB"]:
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                    ofile.write(str(0)                    + ",")
                else: #hitters
                    ofile.write(str(player.h)             + ",")
                    ofile.write(str(player.hr)            + ",")
                    ofile.write(str(player.sb)            + ",")
                    ofile.write(str(player.r)             + ",")
                    ofile.write(str(player.rbi)           + ",")
                    ofile.write("%.3f," % (player.avg))
                    ofile.write("%.3f," % (player.obp))
                    ofile.write("%.3f," % (player.slg))
                    ofile.write("%.3f," % (player.ops))

                # print the financial info
		ofile.write("$%d,"  % (int(float(player.prevValue))))
                ofile.write("$%d,"  % (int(player.bestValue)))
                ofile.write("$%d,"  % (int(player.bestValue * inflationRate)))

                # print the bid info
                if player.bid != None:
                    if int(player.bid.value) == -1:
                        ofile.write("$0,")
                    else:
                        ofile.write("$%d," % (int(player.bid.value)))
                    if player.surplus != None:
                        ofile.write("%d,"  % (player.surplus))
                    else:
                        ofile.write(",")
                    ofile.write("%d," % (int(player.bid.active)))
                    ofile.write(str(player.bid.time)     + ",")
                    ofile.write(str(player.bid.fbalTeam) + "\n")
                else:
                    ofile.write("\n")

                # increment the rank counter
                rank += 1

    ofile.write("\n")

    #--------------------------------------------
    # Break the player list into positional lists
    #--------------------------------------------
    posDict = {}

    for player in playerList:
        for pos in player.pos:
            #if player.bestPos.upper() not in posDict.keys():
            if pos.upper() not in posDict.keys():
                posDict[pos.upper()] = []

            posDict[pos.upper()].append(player)

    #---------------------------
    # Print the positional lists
    #---------------------------
    for pos in ["C","1B","2B","3B","SS","OF", "DH", "SP","RP","BB"]:
        #---------------------------------------------------------
        # Set the current value of the players to the current pos
        #---------------------------------------------------------
        if posDict.has_key(pos):
            playerList = posDict[pos]
        else:
            continue

        for player in playerList:
            player.currentValue = player.posDict[pos]

        ofile.write("%s\n" % (pos))
        printRankings(sorted(posDict[pos], Sorter.sortByPlayerValue), pos, inflationRate, ofile)

    #----------------------
    # Close the output file
    #----------------------
    ofile.close()

def printRankings(playerList, pos, inflationRate, ofile):
    rank = 1
    for player in playerList:
        # print the id info
        ofile.write(str(rank)                   + ",")
        ofile.write(player.firstName            + ",")
        ofile.write(player.lastName             + ",")
        ofile.write(pos                         + ",")
        ofile.write(player.mlbTeam              + ",")

        # print the stats
        if pos in ["SP", "RP"]:
            ofile.write(str(player.w)             + ",")
            ofile.write(str(player.l)             + ",")
            ofile.write(str(player.k)             + ",")
            ofile.write(str(player.qs)            + ",")
            ofile.write(str(player.sv)            + ",")
            ofile.write(str(player.hld)           + ",")
            ofile.write("%1.2f," % (player.era))
            ofile.write("%1.2f," % (player.whip))
            ofile.write(str(0)                    + ",")
	elif pos in ["BB"]:
            ofile.write(str(0)                    + ",")
            ofile.write(str(0)                    + ",")
            ofile.write(str(0)                    + ",")
            ofile.write(str(0)                    + ",")
            ofile.write(str(0)                    + ",")
            ofile.write(str(0)                    + ",")
            ofile.write(str(0)                    + ",")
            ofile.write(str(0)                    + ",")
            ofile.write(str(0)                    + ",")
#         elif player.bestPos in ["PEN"]:
#             continue
        else: #hitters
            ofile.write(str(player.h)             + ",")
            ofile.write(str(player.hr)            + ",")
            ofile.write(str(player.sb)            + ",")
            ofile.write(str(player.r)             + ",")
            ofile.write(str(player.rbi)           + ",")
            ofile.write("%.3f," % (player.avg))
            ofile.write("%.3f," % (player.obp))
            ofile.write("%.3f," % (player.slg))
            ofile.write("%.3f," % (player.ops))

        # print the financial info
        ofile.write("$%d,"  % (int(float(player.prevValue))))
        ofile.write("$%d,"  % (int(player.posDict[pos])))
        ofile.write("$%d,"  % (int(player.posDict[pos] * inflationRate)))

        # print the bid info
        if player.bid != None:
            if int(player.bid.value) == -1:
                ofile.write("$0,")
            else:
                ofile.write("$%d," % (int(player.bid.value)))
            if player.surplus != None:
                ofile.write("%d,"  % (int(player.posDict[pos] - player.bid.value)))
            else:
                ofile.write(",")
            if player.bid.active != None:
                if player.bid.active == True:
                    ofile.write("1,")
                else:
                    ofile.write("-1,")
            else:
                ofile.write("-1,")

            if player.bid.active != None:
                ofile.write(str(player.bid.time)     + ",")
            else:
                ofile.write("-1,")
            ofile.write(str(player.bid.fbalTeam) + "\n")
        else:
            ofile.write("\n")

        rank += 1

    ofile.write("\n")

def saveBidsToPlayerList(hitterList, pitcherList, bidList):
    #-----------------------------------------------
    # Match each bid to its entry in the player list
    #-----------------------------------------------
    for bid in bidList:
        #--------------------
        # Initialize the flag
        #--------------------
        found = False

        #--------------------------------
        # Figure out which list to search
        #--------------------------------
        searchList = []

        if bid.pos in ["SP", "RP"]:
            searchList = pitcherList
        elif bid.pos in ["C", "1B", "2B", "3B", "SS", "OF"]:
            searchList = hitterList
        else:
            searchList = hitterList + pitcherList

        #-------------------------------------------------------------------
        # Scan the search list for the player and save the bid info if found
        #-------------------------------------------------------------------
        for player in searchList:
            if bid.firstName.lower().strip() == player.firstName.lower().strip():
                if bid.lastName.lower().strip() == player.lastName.lower().strip():
                    if bid.pos in player.pos:
                        player.cost     = bid.value
                        player.bid      = bid
                        player.fbalTeam = bid.fbalTeam
                        player.surplus  = player.bestValue - player.cost
                        #player.bestPos  = bid.pos
                        found           = True
                        break

        #-----------------------------------
        # Create a new player if we need too
        #-----------------------------------
        if not found:
            if bid.pos in ["SP", "RP"]:
                newPlayer = Player.Player(posFlag="pitcher", bid=bid)

                pitcherList.append(newPlayer)
            else:
                newPlayer = Player.Player(posFlag="hitter", bid=bid)

                hitterList.append(newPlayer)

def adjustForInflation(hitterList, pitcherList):
    #-------------------------------
    # Set the total amount available
    #-------------------------------
    totalValue = 300 * 20

    #-----------------------------------
    # Compute the total spent on keepers
    #-----------------------------------
    totalKeepers = 0.0

    for player in hitterList:
        if player.cost >= 0:
            totalKeepers += player.cost

    for player in pitcherList:
        if player.cost >= 0:
            totalKeepers += player.cost

    #-----------------------------------
    # Compute the total amount protected
    #-----------------------------------
    totalProtected  = 0

    for player in hitterList:
        if player.cost >= 0 and player.avgValue >= 0:
            totalProtected += player.bestValue

    for player in pitcherList:
        if player.cost >= 0 and player.avgValue >= 0:
            totalProtected += player.bestValue

    #---------------------------------
    # Compute the amount of value left
    #---------------------------------
    valueLeft = totalValue - totalProtected

    #-----------------------
    # Compute the money left
    #-----------------------
    dollarsLeft = totalValue - totalKeepers

    #---------------------------
    # Compute the inflation rate
    #---------------------------
    inflationRate = float(dollarsLeft/valueLeft)

    #-------------------------
    # Apply the inflation rate
    #-------------------------
    for player in hitterList:
        player.infValue[0] = player.bestValue * inflationRate

    for player in pitcherList:
        player.infValue[0] = player.bestValue * inflationRate

    return inflationRate

def printTeamRankings(teamList):
    #----------------------------
    # Print out the stat rankings
    #----------------------------
    #for stat in ["H","HR", "SB", "R", "RBI", "AVG", "OBP", "SLG", "W", "L", "K", "QS","SV","HLD","ERA", "WHIP", "Roster Size", "Remaining", "Surplus"]:
    for stat in ["Roster Size", "Remaining", "Surplus"]:
        #---------------------------------
        # Sort the teams based on the stat
        #---------------------------------
        if stat == "H":           teamList = sorted(teamList, Sorter.sortTeamsByH)
        if stat == "HR":          teamList = sorted(teamList, Sorter.sortTeamsByHR)
        if stat == "SB":          teamList = sorted(teamList, Sorter.sortTeamsBySB)
        if stat == "R":           teamList = sorted(teamList, Sorter.sortTeamsByR)
        if stat == "RBI":         teamList = sorted(teamList, Sorter.sortTeamsByRBI)
        if stat == "AVG":         teamList = sorted(teamList, Sorter.sortTeamsByAVG)
        if stat == "OBP":         teamList = sorted(teamList, Sorter.sortTeamsByOBP)
        if stat == "SLG":         teamList = sorted(teamList, Sorter.sortTeamsBySLG)
        if stat == "W":           teamList = sorted(teamList, Sorter.sortTeamsByW)
        if stat == "L":           teamList = sorted(teamList, Sorter.sortTeamsByL)
        if stat == "K":           teamList = sorted(teamList, Sorter.sortTeamsByK)
        if stat == "QS":          teamList = sorted(teamList, Sorter.sortTeamsByQS)
        if stat == "SV":          teamList = sorted(teamList, Sorter.sortTeamsBySV)
        if stat == "HLD":         teamList = sorted(teamList, Sorter.sortTeamsByHLD)
        if stat == "ERA":         teamList = sorted(teamList, Sorter.sortTeamsByERA)
        if stat == "WHIP":        teamList = sorted(teamList, Sorter.sortTeamsByWHIP)
        if stat == "Roster Size": teamList = sorted(teamList, Sorter.sortTeamsByRosterSize)
        if stat == "Remaining":   teamList = sorted(teamList, Sorter.sortTeamsByRemaining)
        if stat == "Surplus":     teamList = sorted(teamList, Sorter.sortTeamsBySurplus)

        #---------------------------
        # Prepare the message header
        #---------------------------
        title = "| %s Rankings |" % (stat)

        header = "+"
        for i in range(len(title)-2): header += "-"
        header += "+"

        #-----------------
        # Print the output
        #-----------------
        print header
        print title
        print header
        cnt = 1
        if stat == "Roster Size":
            for team in teamList:
                print "%2d: %s %d" % (cnt, team.name, team.numPlayers)
                cnt += 1
            print "\n"
        elif stat == "Remaining":
            for team in teamList:
                print "%2d: %s $%d" % (cnt, team.name, team.remaining)
                cnt   += 1
            print "\n"
        elif stat == "Surplus":
            for team in teamList:
                print "%2d: %s $%d" % (cnt, team.name, team.surplus)
                cnt   += 1
            print "\n"
        else:
            if stat in ["ERA","WHIP"]:
                for team in teamList:
                    print "%2d: %s %1.2f" % (cnt, team.name, float(team.stats[stat]))
                    cnt += 1
            elif stat in ["AVG", "OBP", "SLG"]:
                for team in teamList:
                    print "%2d: %s %.3f" % (cnt, team.name, float(team.stats[stat]))
                    cnt += 1
            else:
                for team in teamList:
                    print "%2d: %s %s" % (cnt, team.name, str(team.stats[stat]))
                    cnt += 1

            print "\n"

def emailResults(playerList, toaddr):
    #-------
    # Set up
    #-------
    fromaddr = "mwbroccolino@gmail.com"
    username = "mwbroccolino"
    password = "BALfootball05!"

    #----------------------------
    # Connect to the gmail server
    #----------------------------
    server = smtplib.SMTP("smtp.gmail.com:587")

    #----------------------
    # Create the time stamp
    #----------------------
    now        = time.time()
    conversion = (60 * 60 * 4)
    est        = now - conversion
    estStr     = datetime.datetime.fromtimestamp(int(est)).strftime('%Y-%m-%d %H:%M:%S')

    #--------------------
    # Prepare the message
    #--------------------
    msgList   = ["From: " + fromaddr, "To: " + toaddr, "Subject: Auction Report: " + estStr, ""]
    msgString = ""
    for pos in ["C","1B","2B","3B", "SS", "OF", "SP","RP","DH","BB"]:
        msgString += pos + "\n"
        for player in playerList:
            if player.bestPos == pos:
                if player.bid != None:
                    if player.bid.active:
                        #bidTimeStr = datetime.datetime.fromtimestamp(int(int(player.bid.time) - conversion)).strftime('%Y-%m-%d %H:%M:%S')
                        if player.cost == -1:
                            msgString += "%s %s %s %s $%d %s\n" % (player.firstName, player.lastName, player.mlbTeam, player.bestPos, 0, player.fbalTeam)
                        else:
                            msgString += "%s %s %s %s $%d %s\n" % (player.firstName, player.lastName, player.mlbTeam, player.bestPos, player.cost, player.fbalTeam)
        msgString += "\n"
    msgList.append(msgString)

    msg = "\r\n".join(msgList)

    #-----------------
    # Send the message
    #-----------------
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddr, msg)

    #-----------------------------------
    # Close the connection to the server
    #-----------------------------------
    server.quit()

def sortTeamsByH(a, b):
    if a.ranks["H"] < b.ranks["H"]:  return 1
    if a.ranks["H"] == b.ranks["H"]: return 0
    else: return -1

def printStatsMatrix(teamList):

    # Compute the rankings based on each stat
    for stat in teamList[0].ranks.keys():
        # first sort based on the stat 
	if stat == "H":           teamList = sorted(teamList, Sorter.sortTeamsByH)
        if stat == "HR":          teamList = sorted(teamList, Sorter.sortTeamsByHR)
        if stat == "SB":          teamList = sorted(teamList, Sorter.sortTeamsBySB)
        if stat == "R":           teamList = sorted(teamList, Sorter.sortTeamsByR)
        if stat == "RBI":         teamList = sorted(teamList, Sorter.sortTeamsByRBI)
        if stat == "AVG":         teamList = sorted(teamList, Sorter.sortTeamsByAVG)
        if stat == "OBP":         teamList = sorted(teamList, Sorter.sortTeamsByOBP)
        if stat == "SLG":         teamList = sorted(teamList, Sorter.sortTeamsBySLG)
        if stat == "W":           teamList = sorted(teamList, Sorter.sortTeamsByW)
        if stat == "L":           teamList = sorted(teamList, Sorter.sortTeamsByL)
        if stat == "K":           teamList = sorted(teamList, Sorter.sortTeamsByK)
        if stat == "QS":          teamList = sorted(teamList, Sorter.sortTeamsByQS)
        if stat == "SV":          teamList = sorted(teamList, Sorter.sortTeamsBySV)
        if stat == "HLD":         teamList = sorted(teamList, Sorter.sortTeamsByHLD)
        if stat == "ERA":         teamList = sorted(teamList, Sorter.sortTeamsByERA)
        if stat == "WHIP":        teamList = sorted(teamList, Sorter.sortTeamsByWHIP)
	if stat == "REM" :        teamList = sorted(teamList, Sorter.sortTeamsByRemaining)
	if stat == "SU+":         teamList = sorted(teamList, Sorter.sortTeamsBySurplus) 

	# now assign the ranking
	for iii in range(len(teamList)): 
	    teamList[iii].ranks[stat] = iii+1
	    teamList[iii].powerRank   = teamList[iii].powerRank + (iii+1)

    # Average out the powerRanking to get an average standing
    for team in teamList: 
	team.powerRank /= 16.0 # number of stats

    # Sort the teams by the power ranking 
    teamList = sorted(teamList, Sorter.sortTeamsByPowerRank)

    print "##     ID   SU+ REM rH rHR rSB rR rRBI rAVG rOBP rSLG rW rL rK rQS rSV rHLD rERA rWHIP |  SU+  REM   H   HR  SB   R   RBI  AVG   OBP   SLG    W   L   K   QS  SV  HD ERA  WHIP"
    cnt = 1
    for team in teamList: 
	print "%2d. %3s[%2d]: %2d %2d  %2d %3d %3d %2d %4d %4d %4d %4d %2d %2d %2d %3d %3d %4d %4d %5d | $%3d $%3d %4d %3d %3d %4d %4d %.3f %.3f %.3f %3d %3d %4d %3d %3d %3d %2.2f %2.2f" % \
		(cnt, \
		team.acro, \
		len(team.players),\
		team.ranks["SU+"],\
		team.ranks["REM"],\
		team.ranks["H"],\
		team.ranks["HR"],\
		team.ranks["SB"], \
		team.ranks["R"], \
		team.ranks["RBI"],\
		team.ranks["AVG"], \
		team.ranks["OBP"], \
		team.ranks["SLG"], \
		team.ranks["W"], \
		team.ranks["L"], \
		team.ranks["K"], \
		team.ranks["QS"], \
		team.ranks["SV"], \
		team.ranks["HLD"], \
		team.ranks["ERA"], \
		team.ranks["WHIP"], \
		team.surplus,\
		team.remaining,\
		team.stats["H"], \
		team.stats["HR"], \
		team.stats["SB"], \
		team.stats["R"], \
		team.stats["RBI"],\
		team.stats["AVG"], \
		team.stats["OBP"], \
		team.stats["SLG"], \
		team.stats["W"], \
		team.stats["L"], \
		team.stats["K"], \
		team.stats["QS"], \
		team.stats["SV"], \
		team.stats["HLD"], \
		team.stats["ERA"], \
		team.stats["WHIP"])
 	cnt = cnt + 1
		 
#################
# Main Function #
#################
if __name__ == "__main__":
    #----------
    # Variables
    #----------
    year             = "2017"
    hitterFile       = "/Users/michaelbroccolino/Desktop/hitters_test_new.csv"
    pitcherFile      = "/Users/michaelbroccolino/Desktop/pitchers_test_new.csv"
    keeperFile       = "/Users/michaelbroccolino/Desktop/baseball/" + year+ "/keepers.txt"
    auctionBoardRoot = "https://www.tapatalk.com/groups/fbauctionboard/2017-auction-f3"
    outputFile       = "/Users/michaelbroccolino/Desktop/auction_report.csv"

    ########################
    # Evaluate the Auction #
    ########################

    #---------------------
    # Read the value files
    #----------------------
    hitterList  = readValueList(hitterFile,  "hitter")
    pitcherList = readValueList(pitcherFile, "pitcher")

    #----------------------
    # Read the keeper file
    #----------------------
    readKeeperFile(keeperFile, hitterList, pitcherList)

    #---------------------
    # Adjust for inflation
    #---------------------
    #inflationRate = adjustForInflation(hitterList, pitcherList)
    inflationRate = 1.145

    print "+------------------------+"
    print "| Inflation Rate = %1.3f |" % (inflationRate)
    print "+------------------------+\n"

    #------------------------
    # Parse the auction board
    #------------------------
    bidList = parseBoard2(auctionBoardRoot)
    
    #------------------------------------------
    # Consolidate the info into the player list
    #------------------------------------------
    saveBidsToPlayerList(hitterList, pitcherList, bidList)

    #--------------------------------
    # Sort the player list into teams
    #--------------------------------
    teamList = sortToTeams(hitterList, pitcherList)

    #--------------------
    # Analyze the auction
    #--------------------
    analyzeAuction(hitterList, pitcherList)

    #-----------------
    # Print the report
    #-----------------
    if len(sys.argv) > 1:
     	printAuctionReport(outputFile, hitterList + pitcherList, inflationRate, hoursTilCheck=int(sys.argv[1]))
    else:
    	printAuctionReport(outputFile, hitterList + pitcherList, inflationRate)
	
    #--------------------------------
    # Print the team-by-team Rankings
    #--------------------------------
    #printTeamRankings(teamList)

    #---------------------------
    # Print out the stats matrix
    #---------------------------
    printStatsMatrix(teamList)
