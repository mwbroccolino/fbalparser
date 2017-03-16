###########
# Imports #
###########

#####################
# Class Definintion #
#####################
class Player:
    
    def __init__(self, playerDict=None, posFlag="hitter", bid=None, firstName=None, lastName=None, pos=None, mlbTeam=None, fbalTeam=None, cost=None):
        #----------------------------------------------------------------
        # If this is coming from the value file, we will enter this block
        #----------------------------------------------------------------
	self.prevValue = 0.0
	self.risk      = 0.0
	self.delta     = 0.0
        
	if playerDict != None:
            #------------------------------------------------- 
            # Save the elements of the dictionary to the class
            #-------------------------------------------------
            self.firstName = playerDict["First"]
            self.lastName  = playerDict["Last"]
            self.mlbTeam   = playerDict["Team"]
            self.bid       = None
            self.fbalTeam  = None
            self.cost      = -1
            self.surplus   = None
            self.bestPos   = ""
            self.currentValue = 0
            
            self.pos       = []
            self.cbs       = []
            self.zips      = []
            self.fans      = []
            self.steamer   = []
            self.oliver    = []
            self.rotoChamp = []
            self.avgValue  = []
            self.infValue  = []
            self.bestValue = 0.0
	    self.prevValue = playerDict["Prev"]
	    self.risk      = playerDict["Risk"]
	    self.delta     = playerDict["Delta"]
            
            self.pos.append(playerDict["Pos"])
            #self.cbs.append(float(playerDict["CBS"]))
            #self.zips.append(float(playerDict["ZIPS"]))
            #self.fans.append(float(playerDict["Fans"]))
            #self.steamer.append(float(playerDict["Steamer"]))
            #self.oliver.append(float(playerDict["Oliver"]))
            #self.rotoChamp.append(float(playerDict["RotoChamp"]))
            self.avgValue.append(float(playerDict["Average"]))
            self.infValue.append(0.0)
            
            if posFlag == "hitter":
                self.h         = int(playerDict["H"])
                self.hr        = int(playerDict["HR"])
                self.sb        = int(playerDict["SB"])
                self.r         = int(playerDict["R"])
                self.rbi       = int(playerDict["RBI"])
                self.avg       = float(playerDict["AVG"])
                self.obp       = float(playerDict["OBP"])
                self.slg       = float(playerDict["SLG"])
		self.ab        = int(playerDict["AB"])
                self.ops       = float(self.obp + self.slg)
            else:
                self.w         = int(playerDict["W"])
                self.l         = int(playerDict["L"])
                self.k         = int(playerDict["K"])
                self.qs        = int(playerDict["QS"])
                self.sv        = int(playerDict["SV"])
                self.hld       = int(playerDict["HLD"])
                self.era       = float(playerDict["ERA"])
                self.whip      = float(playerDict["WHIP"])
		self.ip        = float(playerDict["IP"])

        #----------------------------------------------------------
        # If a player was bid on but wasn't projected to have value
        # he will end up here
        #----------------------------------------------------------
        elif bid != None: 
            #------------------------------------------------- 
            # Save the elements of the dictionary to the class
            #-------------------------------------------------
            self.firstName = bid.firstName
            self.lastName  = bid.lastName
            self.mlbTeam   = bid.mlbTeam
            self.bid       = bid
            self.fbalTeam  = bid.fbalTeam
            self.cost      = bid.value
            self.surplus   = float(0.0 - bid.value)
            
            self.pos       = [bid.pos]
            self.bestPos   = bid.pos
            #self.cbs       = [0.0]
            #self.zips      = [0.0]
            #self.fans      = [0.0]
            #self.steamer   = [0.0]
            #self.oliver    = [0.0]
            #self.rotoChamp = [0.0]
            self.avgValue  = [0.0]
            self.infValue  = [0.0]
            self.bestValue = 0.0
                    
            if posFlag == "hitter":
                self.h         = int(0)
                self.hr        = int(0)
                self.sb        = int(0)
                self.r         = int(0)
                self.rbi       = int(0)
                self.avg       = float(0.0)
                self.obp       = float(0.0)
                self.slg       = float(0.0)
                self.ops       = float(0.0)
		self.ab        = int(0)
            else:
                self.w         = int(0)
                self.l         = int(0)
                self.k         = int(0)
                self.qs        = int(0)
                self.sv        = int(0)
                self.hld       = int(0)
                self.era       = float(0.0)
                self.whip      = float(0.0)
		self.ip        = float(0.0)
                    
        #-----------------------------------------------------------------
        # If this is coming from the keeper file, we will enter this block
        #-----------------------------------------------------------------
        else: 
            #------------------------------------------------- 
            # Save the elements of the dictionary to the class
            #-------------------------------------------------
            self.firstName = firstName
            self.lastName  = lastName
            self.mlbTeam   = mlbTeam
            self.bid       = None
            self.fbalTeam  = fbalTeam
            self.cost      = cost
            self.surplus   = float(0.0 - cost)
            self.bestPos   = pos
                        
            self.pos       = [pos]
            #self.cbs       = [0.0]
            #self.zips      = [0.0]
            #self.fans      = [0.0]
            #self.steamer   = [0.0]
            #self.oliver    = [0.0]
            #self.rotoChamp = [0.0]
            self.avgValue  = [0.0]
            self.infValue  = [0.0]
            self.bestValue = 0.0
                    
            if posFlag == "hitter":
                self.h         = int(0)
                self.hr        = int(0)
                self.sb        = int(0)
                self.r         = int(0)
                self.rbi       = int(0)
                self.avg       = float(0.0)
                self.obp       = float(0.0)
                self.slg       = float(0.0)
                self.ops       = float(0.0)
		self.ab        = int(0)
            else:
                self.w         = int(0)
                self.l         = int(0)
                self.k         = int(0)
                self.qs        = int(0)
                self.sv        = int(0)
                self.hld       = int(0)
                self.era       = float(0.0)
                self.whip      = float(0.0)
		self.ip        = float(0.0) 

        #------------------------------------------------ 
        # Add the pos dictionary for the analysis portion
        #------------------------------------------------     
        self.posDict = {}
        
        cnt = 0
        
        for pos in self.pos:
            self.posDict[pos] = self.avgValue[cnt]
            
            cnt += 1 
            
    def exists(self, playerList):
        #---------------------------------------------------
        # See if the player already exists in the input list
        #---------------------------------------------------
        index = None
        cnt   = 0
        
        for player in playerList:
            if self.firstName.strip() == player.firstName.strip():
                if self.lastName.strip() == player.lastName.strip():
                    if self.mlbTeam.strip() == player.mlbTeam.strip():
                        index = cnt
                        break
            cnt += 1
            
        return index
        
    def printPlayer(self):
        print "Tag:  %s %s %s %s" % (self.firstName, self.lastName, self.mlbTeam, str(self.pos))
        print "FBAL: %s" % (self.fbalTeam)
        print "AVG:  %s" % (str(self.avgValue))
        print "Dict: %s" % (str(self.posDict))
        print "INF:  %s" % (str(self.infValue))
        print "Best: %s" % (str(self.bestValue))
        print "Pos:  %s" % (str(self.bestPos))
        print "Cost: %s" % (str(self.cost))
        print "Sur+: %s\n" % (str(self.surplus))
        
#################
# Main Function #
#################
if __name__ == "__main__":
    pass
