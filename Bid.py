###########
# Imports #
###########
import time
import datetime

#####################
# Class Definintion #
#####################
class Bid:

    def __init__(self, team, pos="", url="", value=None):
        #-------------------
        # Save the arguments
        #-------------------
        self.fbalTeam = team.strip()
        self.url      = url

        #---------------------------
        # Define the class variables
        #---------------------------
        self.firstName   = ""
        self.lastName    = ""
        self.pos         = pos
        self.mlbTeam     = ""
        self.time        = None
        self.active      = None
        self.value       = -1
        self.matched     = False
        self.tag         = None
        self.valueString = ""

        #---------------------------------------------------
        # See if the bid is being created by the keeper file
        #---------------------------------------------------
        if value != None:
            if value == -2:
                self.value = 0
            else:
                self.value = value

    def parseTag(self, tag):
        #-------------
        # Save the tag
        #-------------
        self.tag = tag

        #------------------------------------------
        # See if the guy is really only DH eligible
        #------------------------------------------
        if self.tag.count("DH") > 0:
            print "Changing pos to DH for %s" % (self.tag)
            self.pos = "DH"

        #-----------------------
        # Save the stuff we want
        #-----------------------
        if tag.count(","):
            splitOnCommas = tag.split(",")
            if len(splitOnCommas) == 4: # first, last, pos, team
                self.firstName = splitOnCommas[0].strip()
                self.lastName  = splitOnCommas[1].strip()
                self.pos       = splitOnCommas[2].strip().upper()
                self.mlbTeam   = splitOnCommas[3].strip().upper()
            elif len(splitOnCommas) == 3: # first last, pos, team
                splitOnSpaces = splitOnCommas[0].split(" ")
                self.firstName = splitOnSpaces[0].strip()
                self.lastName  = splitOnSpaces[1].strip()
                self.pos       = splitOnCommas[1].strip().upper()
                self.mlbTeam   = splitOnCommas[2].strip().upper()
            elif len(splitOnCommas) == 2: # first last, pos team OR first last pos, team
                splitOnSpaces  = splitOnCommas[0].split(" ")
                self.firstName = splitOnSpaces[0]
                self.lastName  = splitOnSpaces[1]
                if len(splitOnSpaces) > 2:
                    self.pos = splitOnSpaces[2]
                    self.mlbTeam = splitOnCommas[1].strip()
                else:
                    splitOnSpaces  = splitOnCommas[1].strip().split(" ")
                    self.pos       = splitOnSpaces[0]
                    self.mlbTeam   = splitOnSpaces[1]
        else:
            splitOnSpaces = tag.split(" ")

            self.firstName = splitOnSpaces[0].strip()
            self.lastName  = splitOnSpaces[1].strip()
            self.pos       = splitOnSpaces[2].strip().upper()
            self.mlbTeam   = splitOnSpaces[3].strip().upper()

    def findBidTime(self, timeLines):
        #--------------------------------------------------
        # Get the string containing the value from the post
        #--------------------------------------------------
        if len(timeLines) > 0:
            timeString = timeLines[-1]
        else:
            print "No time lines in bid.findBidTime for %s" % self.tag
            timeString = ""

        #------------------------------
        # Parse the line for the string
        #------------------------------
        if timeString != "":
            timeStamp = timeString.split(">")[-2].strip().split("<")[0]
        
        #-----------------------------------------------
        # Get the struct_time object from the time stamp
        #-----------------------------------------------
        #self.time = time.strptime(timeStamp, "%b %d %Y, %I:%M %p")
        self.time = time.strptime(timeStamp, "%Y-%m-%dT%H:%M")

        #--------------------------------------------
        # Convert the bid time to the datetime object
        #--------------------------------------------
        self.time = datetime.datetime.fromtimestamp(time.mktime(self.time))

        #----------------------------
        # Adjust for daylight savings
        #----------------------------
        #self.time = self.time + datetime.timedelta(hours=1)

        #----------------------------------------
        # Convert the bid time to the correct time
        #----------------------------------------
        #self.time = self.time + datetime.timedelta(hours=5)
        #self.time = self.time + datetime.timedelta(hours=-4)

    def isActive(self):
        #---------------------
        # Get the current time
        #---------------------
        now = datetime.datetime.now()

        #--------------------------------------------------------
        # Compute the expiration time and convert to England time
        #--------------------------------------------------------
        expireTime = self.time + datetime.timedelta(days=1)

        #-------------------------
        # See if the bid is active
        #-------------------------
        if expireTime > now:
            self.active = True
        else:
            if self.value > 0:
                self.active = False
            else:
                self.active = True

    def getValue(self, bidLines):
        """
        #TODO: pass in the time lines here and search for any invalid bids.
        """
        #--------------------------------------------------
        # Get the string containing the value from the post
        #--------------------------------------------------
        if len(bidLines) >= 1:
            valueString      = bidLines[-1]
            self.valueString = valueString
        else:
            self.value = 0
            return

        #------------------------------
        # Try to parse the value string
        #------------------------------
        self.parseValueString(valueString)

        #------------------------------------------------------------
        # As a last ditch effort, try the preceding post if available
        #------------------------------------------------------------
        if self.value < 0:
            print "Add to keeper file: %s %s %s" % (self.firstName, self.lastName, self.pos)
#            if len(bidLines) > 2:
#                newValueString = bidLines[-3]
#
#            self.parseValueString(newValueString)

    def parseValueString(self, valueString):
        #--------------------------------------------------
        # See if post was placed by CR about a mistaken bid
        #--------------------------------------------------
        splitOnSpaces = valueString.split(" ")

        if len(splitOnSpaces) >= 20 and self.fbalTeam.strip() == "Crumpton Roches":
            return

        #------------------------
        # Try to parse the string
        #------------------------
        splitValueString = valueString.split(">")
        splitValueString = splitValueString[1].split("<")[0]

        #-----------------------
        # Does it have a $ sign?
        #-----------------------
        if self.value < 0:
            for token in splitValueString.split(" "):
                if token.count("&amp;#036;") > 0:
                    newSplit = token.split("&amp;#036;")
                    for t in newSplit:
                        if len(t) > 0:
                            #------------------------------------
                            # Check for any lingering punctuation
                            #------------------------------------
                            if t.count(".") > 0:
                                t = t.split(".")[0]

                            if self.__isNumber(t):
                                self.value = int(t)

        #------------------------------------------
        # See if there is an actual $ sign in there
        #------------------------------------------
        if self.value < 0:
            for token in splitValueString.split(" "):
                if token.count("$") > 0:
                    newSplit = token.split("$")
                    for t in newSplit:
                        if len(t) > 0:
                            #------------------------------------
                            # Check for any lingering punctuation
                            #------------------------------------
                            if t.count(".") > 0:
                                t = t.split(".")[0]

                            if self.__isNumber(t):
                                self.value = int(t)
        
        #----------------------------
        # If it doesn't have a $ sign
        #----------------------------
        if self.value < 0:
            for token in splitValueString.split(" "):
                if self.__isNumber(token):
                    #------------------------------------
                    # Check for any lingering punctuation
                    #------------------------------------
                    if token.count(".") > 0:
                        token = token.split(".")[0]

                    self.value = int(token)

        #--------------------------------------------
        # See if the string has the <br /> char in it
        #--------------------------------------------
        if self.value < 0:
            splitValueString = valueString.split("<br />")

            if len(splitValueString) >= 2:
                token = splitValueString[1]
            else:
                token = ""

            splitToken = token.split("<")

            if len(splitToken) >= 1:
                value = splitToken[0].strip()
            else:
                value = ""

            if self.__isNumber(value):
                self.value = int(value)

        #--------------------------------------
        # See if the bid was placed with a word
        #--------------------------------------
        if self.value < 0:
            splitValueString = valueString.split(">")

            if len(splitValueString) > 0:
                token = splitValueString[1].split("<")[0].strip()

                if token == "one":     self.value = 1
                if token == "uno":     self.value = 1
                if token == "two":     self.value = 2
                if token == "three":   self.value = 3
                if token == "four":    self.value = 4
                if token == "five":    self.value = 5
                if token == "six":     self.value = 6
                if token == "seven":   self.value = 7
                if token == "eight":   self.value = 8
                if token == "nine":    self.value = 9
                if token == "ten":     self.value = 10
                if token == "eleven": self.value = 11

        #-------------------------------------------------
        # See if the string had some extra new lines in it
        #-------------------------------------------------
        if self.value < 0:
            splitValueString = valueString.split(" ")
            for token in splitValueString:
                for subtoken in token.split(">"):
                    #----------------------------------------------
                    # Do we have extra new lines AND a dollar sign?
                    #----------------------------------------------
                    if subtoken.count("&#036;") > 0:
                        subtoken = subtoken.split("&#036;")[1]

                    #--------------------------------------------
                    # Finally, see if we have the number and save
                    #--------------------------------------------
                    if self.__isNumber(subtoken):
                        self.value = int(subtoken)

        #------------------------------------------
        # See if the string had a ` character in it
        #------------------------------------------
        if self.value < 0:
            splitValueString = valueString.split("`")
            if len(splitValueString) >= 2: 
                tmp = splitValueString[1]
                self.value = int(splitValueString[1].split(" ")[0].split("<")[0])

    def printBid(self):
        print "First:  "  + str(self.firstName)
        print "Last:   "  + str(self.lastName)
        print "Pos:    "  + str(self.pos)
        print "Team:   "  + str(self.fbalTeam)
        print "Value:  $" + str(self.value)
        print "Time:   "  + str(self.time)
        print "Active: "  + str(self.active)
        print "URL:    "  + str(self.url) + "\n"

    def __isNumber(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

#--------------
# Main Function
#--------------
if __name__ == "__main__":
    bids = ["$26- Final Bid... you want to pay more, take him!",
            "IFIFYO bids $55",
            "$15",
            "15",
            "15$"
            ]
