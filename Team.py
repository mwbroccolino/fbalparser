###########
# Imports #
###########
import Sorter

#####################
# Class Definintion #
#####################
class Team:
    def __init__(self, teamName, playerList):
        #-------------------------------------
        # Save the variables and define others
        #-------------------------------------

        # IDs
        self.name           = teamName
        self.players        = playerList
        self.remaining      = 300
        self.numPlayers     = 0
        self.numHitters     = 0
        self.numPitchers    = 0

        # Set the acronym
        self.acro = ""
        if self.name.strip() == "Blazing Brits": self.acro = "UK"
        elif self.name.strip() == "Crumpton Roches": self.acro = "CR" 
        elif self.name.strip() == "Fredneck Flyers": self.acro = "FF" 
        elif self.name.strip() == "Deep in the Hole": self.acro = "DH" 
        elif self.name.strip() == "B&#39;More Balding Bruisers": self.acro = "BBB" 
        elif self.name.strip() == "Phuket Beach-bums": self.acro = "PBB" 
        elif self.name.strip() == "Murderer&#39;s Row": self.acro = "MR" 
        elif self.name.strip() == "Reading Wheelmen": self.acro = "RW" 
        elif self.name.strip() == "Mayan Shamans": self.acro = "MS" 
        elif self.name.strip() == "Lil Emperors": self.acro = "LE" 
        elif self.name.strip() == "Atlanta Cowards": self.acro = "AC" 
        elif self.name.strip() == "Barroom Brawlers": self.acro = "BB" 
        elif self.name.strip() == "Pass Miggy the scotch": self.acro = "PM" 
        elif self.name.strip() == "Go Blue": self.acro = "GB" 
        elif self.name.strip() == "Oriole85": self.acro = "OS" 
        elif self.name.strip() == "Deflated Ballz": self.acro = "DB" 
        elif self.name.strip() == "Williamsville Wombats": self.acro = "WW" 
        elif self.name.strip() == "The DyNasty": self.acro = "TD" 
        elif self.name.strip() == "surf_fish": self.acro = "SF" 
        elif self.name.strip() == "A2 Swagger": self.acro = "A2"    
        
        # Finances
        self.spent          = 0
        self.surplus        = 0
        self.penalty        = 0

        # Stats
        self.stats         = {}
        self.stats["H"]    = 0
        self.stats["HR"]   = 0
        self.stats["SB"]   = 0
        self.stats["R"]    = 0
        self.stats["RBI"]  = 0
        self.stats["AVG"]  = 0.0
        self.stats["OBP"]  = 0.0
        self.stats["SLG"]  = 0.0
        self.stats["W"]    = 0
        self.stats["L"]    = 0
        self.stats["K"]    = 0
        self.stats["QS"]   = 0
        self.stats["SV"]   = 0
        self.stats["HLD"]  = 0
        self.stats["ERA"]  = 0.0
        self.stats["WHIP"] = 0.0
        self.stats["AB"]   = 0
        self.stats["IP"]   = 0.0
        self.stats["BB"]   = 0
        self.stats["TB"]   = 0
        self.stats["ER"]   = 0
        self.stats["BBPH"] = 0

        # Scores
        self.ranks         = {}
        self.ranks["H"]    = 0
        self.ranks["HR"]   = 0
        self.ranks["SB"]   = 0
        self.ranks["R"]    = 0
        self.ranks["RBI"]  = 0
        self.ranks["AVG"]  = 0
        self.ranks["OBP"]  = 0
        self.ranks["SLG"]  = 0
        self.ranks["W"]    = 0
        self.ranks["L"]    = 0
        self.ranks["K"]    = 0
        self.ranks["QS"]   = 0
        self.ranks["SV"]   = 0
        self.ranks["HLD"]  = 0
        self.ranks["ERA"]  = 0
        self.ranks["WHIP"] = 0
        self.ranks["REM"]  = 0
        self.ranks["SU+"]  = 0

        self.powerRank     = 0.0
    
        #---------------------------------------
        # Compute financial info and team totals
        #---------------------------------------
        for player in self.players:
            if player.cost == -1:
                print "Removing Player: %s %s %s %s %d %s" % (player.firstName, player.lastName, player.bestPos, player.mlbTeam, player.cost, player.fbalTeam)
                self.players.remove(player)
            else:
                self.spent     += player.cost
                self.remaining -= player.cost
                self.surplus   += (player.bestValue - player.cost)

                if player.pos[0] == "PEN":
                    self.penalty = player.cost

        #--------------------------------------------------------
        # Set the number of players variable removing the penalty
        #--------------------------------------------------------
        if self.penalty > 0:
            self.numPlayers = len(self.players) - 1
        else:
            self.numPlayers = len(self.players)

        #----------------------------
        # Tally the teams total stats
        #----------------------------
        """
        for player in playerList:
            if   player.pos[0].strip() in ["BB", "PEN"]: continue
            elif player.pos[0].strip() in ["SP", "RP"]:
                try:
                    self.numPitchers     += 1
                    self.stats["W"]      += player.w
                    self.stats["L"]      += player.l
                    self.stats["K"]      += player.k
                    self.stats["QS"]     += player.qs
                    self.stats["SV"]     += player.sv
                    self.stats["HLD"]    += player.hld
                    self.stats["ERA"]    += player.era
                    self.stats["WHIP"]   += player.whip
            self.stats["IP"]     += player.ip
                except AttributeError:
                    print "Error in team sorter with..."
                    player.printPlayer()
            else:
                try:
                    self.numHitters     += 1
                    self.stats["H"]     += player.h
                    self.stats["HR"]    += player.hr
                    self.stats["SB"]    += player.sb
                    self.stats["R"]     += player.r
                    self.stats["RBI"]   += player.rbi
                    self.stats["AVG"]   += player.avg
                    self.stats["OBP"]   += player.obp
                    self.stats["SLG"]   += player.slg
                    self.stats["AB"]    += player.ab
        except AttributeError:
                    print "Error in team sorter with..."
                    player.printPlayer()
        """
        #----------------------------------------------------
        # Figure out who the starters for this team should be
        #----------------------------------------------------
        self.starters       = {}
        self.starters["C"]  = []
        self.starters["1B"] = []
        self.starters["2B"] = []
        self.starters["3B"] = []
        self.starters["SS"] = []
        self.starters["DH"] = []
        self.starters["OF"] = []
        self.starters["SP"] = []
        self.starters["RP"] = []

        self.numStarters       = {}
        self.numStarters["C"]  = 1
        self.numStarters["1B"] = 1
        self.numStarters["2B"] = 1
        self.numStarters["3B"] = 1
        self.numStarters["SS"] = 1
        self.numStarters["OF"] = 3
        self.numStarters["DH"] = 1
        self.numStarters["SP"] = 10
        self.numStarters["RP"] = 4
    
        # sort the players into their positional lists
        posList = {}

        for player in playerList:
            if player.lastName == "Gattis":
                player.bestPos = "C"

            if player.pos[0].strip() not in self.starters.keys(): continue
            
            if player.bestPos in posList.keys(): 
                posList[player.bestPos].append(player)
            else: 
                posList[player.bestPos] = []
                posList[player.bestPos].append(player)
 
        # sort the positional lists based on their best value
        for pos in posList.keys(): 
            posList[pos] = sorted(posList[pos], Sorter.sortPlayersByValue)
    
        # finally, fill in the starters
        for pos in posList.keys():
            num = self.numStarters[pos]
    
            for player in posList[pos]:
                if len(self.starters[pos]) < num: 
                    self.starters[pos].append(player)
                elif pos not in ("SP", "RP"):
                    # set the DH
                    if len(self.starters["DH"]) == 0: 
                        self.starters["DH"].append(player)
                    else: 
                        if player.bestValue > self.starters["DH"][0].bestValue: 
                            self.starters["DH"][0] = player 
        if self.name == "Blazing Brits": 
            self.printStarters() 
        
        #------------------------------------------
        # Recompute the stats based on the starters
        #------------------------------------------
        for pos in self.starters.keys(): 
            for player in self.starters[pos]: 
                if pos in ["SP", "RP"]:
                    try:
                        self.stats["W"]      += player.w
                        self.stats["L"]      += player.l
                        self.stats["K"]      += player.k
                        self.stats["QS"]     += player.qs
                        self.stats["SV"]     += player.sv
                        self.stats["HLD"]    += player.hld
                        self.stats["ERA"]    += player.era
                        self.stats["WHIP"]   += player.whip
                        self.stats["IP"]     += player.ip
                        self.stats["ER"]     += (float(player.ip*player.era)/float(9.0)) 
                        self.stats["BBPH"]   += (player.whip * float(player.ip))
                    except AttributeError:
                        print "Error in team sorter with..."
                        player.printPlayer()
                else: 
                    try:
                        self.stats["H"]     += player.h
                        self.stats["HR"]    += player.hr
                        self.stats["SB"]    += player.sb
                        self.stats["R"]     += player.r
                        self.stats["RBI"]   += player.rbi
                        self.stats["AVG"]   += player.avg
                        self.stats["OBP"]   += player.obp
                        self.stats["SLG"]   += player.slg
                        self.stats["AB"]    += player.ab
                        self.stats["BB"]    += ((float(player.obp)*float(player.ab) - float(player.h))/(1-player.obp))
                        self.stats["TB"]    += (player.slg * float(player.ab))
                    except AttributeError:
                        print "Error in team sorter with..."
                        player.printPlayer()

        #---------------------------------------
        # Compute the stats that can be computed
        #---------------------------------------
        if self.stats["AB"]:
            self.stats["AVG"]  = float(self.stats["H"]) / float(self.stats["AB"])
            self.stats["SLG"]  = float(self.stats["TB"]) / float(self.stats["AB"])
        
        if self.stats["AB"] or self.stats["BB"]:
            self.stats["OBP"]  = (float(self.stats["H"]) + self.stats["BB"]) / (float(self.stats["AB"]) + self.stats["BB"])
        
        if self.stats["IP"]:
            self.stats["ERA"]  = float(9)*(float(self.stats["ER"])/float(self.stats["IP"]))
            self.stats["WHIP"] = float(self.stats["BBPH"]) / float(self.stats["IP"])

        #-------------------------------------------------------  
        # Average the countable stats over the number of periods
        #-------------------------------------------------------  
        num = 13

        self.stats["H"]   /= num
        self.stats["HR"]  /= num
        self.stats["SB"]  /= num
        self.stats["R"]   /= num
        self.stats["RBI"] /= num
        self.stats["W"]   /= num
        self.stats["L"]   /= num
        self.stats["K"]   /= num
        self.stats["QS"]  /= num
        self.stats["SV"]  /= num
        self.stats["HLD"] /= num

        #-------------------
        # Average the  stats
        #-------------------
        """
    if self.numHitters > 0:
            self.stats["H"]    /= float(self.numHitters)
            self.stats["HR"]   /= float(self.numHitters)
            self.stats["SB"]   /= float(self.numHitters)
            self.stats["R"]    /= float(self.numHitters)
            self.stats["RBI"]  /= float(self.numHitters)
            self.stats["AVG"]  /= float(self.numHitters)
            self.stats["OBP"]  /= float(self.numHitters)
            self.stats["SLG"]  /= float(self.numHitters)
        if self.numPitchers > 0:
            self.stats["W"]    /= float(self.numPitchers)
            self.stats["L"]    /= float(self.numPitchers)
            self.stats["K"]    /= float(self.numPitchers)
            self.stats["QS"]   /= float(self.numPitchers)
            self.stats["SV"]   /= float(self.numPitchers)
            self.stats["HLD"]  /= float(self.numPitchers)
            self.stats["ERA"]  /= float(self.numPitchers)
            self.stats["WHIP"] /= float(self.numPitchers)
        """
    def printTeam(self):
        print "\nName:  " + self.name
        print "Surplus: " + str(self.surplus)
        print "Spent:   " + str(self.spent)
        print "Penalty  " + str(self.penalty)
        print "Rem:     " + str(self.remaining) + "\n"
        print "Players: "
        for pos in ["C","1B", "2B","SS", "3B","OF","SP","RP", "DH"]:
            self.printPos(pos)

    def printStarters(self): 
        names = {}
        for key in self.starters.keys(): 
            names[key] = [] 
            for player in self.starters[key]:
                names[key].append("%s %s %s $%s" % (player.firstName, player.lastName, player.mlbTeam, str(int(player.bestValue))))

        for key in ("C", "1B", "2B", "3B", "SS", "OF", "DH", "SP", "RP"): 
            print key, names[key]

    def printPos(self, pos):
        print pos
        for player in self.players:
            if player.pos[0] == pos:
                print "%s %s %s $%s $%d" % (player.firstName, player.lastName, player.mlbTeam, player.cost, int(player.surplus))
        print "\n"
