import numpy as np
from pokerSplit import *



# Player Slate (in chips)
initialSlate = {}
initialSlate['Drew'] = 38
initialSlate['John'] = 0
initialSlate['Amy'] = 168
initialSlate['Kristin'] = 0
initialSlate['Malik'] = 100
initialSlate['Manuela'] = 237
# Player Investment (in dollars)
buyIn = 10
moneyInvested = {}
moneyInvested['Drew'] =    buyIn
moneyInvested['John'] =    buyIn
moneyInvested['Amy'] =     buyIn
moneyInvested['Kristin'] = buyIn
moneyInvested['Malik'] =   buyIn
moneyInvested['Manuela'] = buyIn
# Prefered transaction links
preferedLinks = {'Drew':	['John'],
                 'John':	['Drew'],
                 'Amy':		[],
                 'Kristin': 	['Malik'],
                 'Malik':	['Kristin'],
                 'Manuela':	[]}
# Construct the split
slate = PlayerSlate(initialSlate=initialSlate,
                    moneyInvested=moneyInvested,
                    preferedLinks=preferedLinks)

# Print initial stat
slate.log(slate.initialSlate)


# Equilibriate scores
slate.equilibrate()
# Print list of transactions
slate.logTransactions()
# Print final slate
slate.log(slate.currentSlate)
