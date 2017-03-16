###########
# Imports #
###########


#####################
# Class Definintion #
#####################
def sortTeamsBySurplus(a,b):
    if a.surplus < b.surplus:  return 1
    if a.surplus == b.surplus: return 0
    else: return -1
    
def sortPlayersBySurplus(a,b):
    if a.surplus < b.surplus:  return 1
    if a.surplus == b.surplus: return 0
    else: return -1

def sortPlayersByValue(a,b):
    if a.bestValue < b.bestValue:  return 1
    if a.bestValue == b.bestValue: return 0
    else: return -1

def sortTeamsByH(a,b):
    if a.stats["H"] < b.stats["H"]:  return 1
    if a.stats["H"] == b.stats["H"]: return 0
    else: return -1
    
def sortTeamsByHR(a,b):
    if a.stats["HR"] < b.stats["HR"]:  return 1
    if a.stats["HR"] == b.stats["HR"]: return 0
    else: return -1
    
def sortTeamsBySB(a,b):
    if a.stats["SB"] < b.stats["SB"]:  return 1
    if a.stats["SB"] == b.stats["SB"]: return 0
    else: return -1
    
def sortTeamsByR(a,b):
    if a.stats["R"] < b.stats["R"]:  return 1
    if a.stats["R"] == b.stats["R"]: return 0
    else: return -1
    
def sortTeamsByRBI(a,b):
    if a.stats["RBI"] < b.stats["RBI"]:  return 1
    if a.stats["RBI"] == b.stats["RBI"]: return 0
    else: return -1
    
def sortTeamsByAVG(a,b):
    if a.stats["AVG"] < b.stats["AVG"]:  return 1
    if a.stats["AVG"] == b.stats["AVG"]: return 0
    else: return -1
    
def sortTeamsByOBP(a,b):
    if a.stats["OBP"] < b.stats["OBP"]:  return 1
    if a.stats["OBP"] == b.stats["OBP"]: return 0
    else: return -1
    
def sortTeamsBySLG(a,b):
    if a.stats["SLG"] < b.stats["SLG"]:  return 1
    if a.stats["SLG"] == b.stats["SLG"]: return 0
    else: return -1
      
def sortTeamsByW(a,b):
    if a.stats["W"] < b.stats["W"]:  return 1
    if a.stats["W"] == b.stats["W"]: return 0
    else: return -1
def sortTeamsByPowerRank(a,b):
    if a.powerRank < b.powerRank:  return -1
    if a.powerRank == b.powerRank: return 0
    else: return 1
def sortTeamsByL(a,b):
    if a.stats["L"] < b.stats["L"]:  return -1
    if a.stats["L"] == b.stats["L"]: return 0
    else: return 1
def sortTeamsByK(a,b):
    if a.stats["K"] < b.stats["K"]:  return 1
    if a.stats["K"] == b.stats["K"]: return 0
    else: return -1
def sortTeamsByQS(a,b):
    if a.stats["QS"] < b.stats["QS"]:  return 1
    if a.stats["QS"] == b.stats["QS"]: return 0
    else: return -1
def sortTeamsBySV(a,b):
    if a.stats["SV"] < b.stats["SV"]:  return 1
    if a.stats["SV"] == b.stats["SV"]: return 0
    else: return -1
def sortTeamsByHLD(a,b):
    if a.stats["HLD"] < b.stats["HLD"]:  return 1
    if a.stats["HLD"] == b.stats["HLD"]: return 0
    else: return -1
def sortTeamsByERA(a,b):
    if a.stats["ERA"] < b.stats["ERA"]:  return -1
    if a.stats["ERA"] == b.stats["ERA"]: return 0
    else: return 1
def sortTeamsByWHIP(a,b):
    if a.stats["WHIP"] < b.stats["WHIP"]:  return -1
    if a.stats["WHIP"] == b.stats["WHIP"]: return 0
    else: return 1

def sortTeamsByRemaining(a,b):
    if a.remaining < b.remaining:  return 1
    if a.remaining == b.remaining: return 0
    else: return -1

def sortTeamsByRosterSize(a,b):
    if a.numPlayers <  b.numPlayers:  return 1
    if a.numPlayers == b.numPlayers: return 0
    else: return -1

def sortByPlayerValue(a,b):
    if a.currentValue <  b.currentValue:  return 1
    if a.currentValue == b.currentValue: return 0
    else: return -1
    
def sortByPlayerCost(a,b):
    if a.cost <  b.cost:  return 1
    if a.cost == b.cost: return 0
    else: return -1
