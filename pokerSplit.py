import sys
import numpy as np

class Transaction:
    def __init__(self,sender,receiver,dollarAmount):
        self.sender = sender
        self.receiver = receiver
        self.dollarAmount = dollarAmount
        self.addedToTab = False
    def log(self):
        print(self.sender + ' sends %.2f ' % self.dollarAmount + ' to ' + self.receiver)


class PlayerSlate:
    def __init__(self,initialSlate,moneyInvested,preferedLinks):
        self.initialSlate = initialSlate
        self.moneyInvested = moneyInvested
        self.currentSlate = initialSlate.copy()
        self.preferedLinks = preferedLinks
        self.nPlayers = len(initialSlate)
        
        self.moneyInPot = sum([value for _, value in moneyInvested.items()])
        self.chipsInPot = sum([value for _, value in initialSlate.items()])
        # Convert slates to dollars
        self.convertChipsToDollarSlate(self.initialSlate)
        self.convertChipsToDollarSlate(self.currentSlate)
        self.removeInitialInvestment(self.initialSlate)
        self.removeInitialInvestment(self.currentSlate)
        self.transactions = []

    def removeInitialInvestment(self,slate):
        for key, value in slate.items():
                slate[key] -= self.moneyInvested[key]

    def convertChipsToDollarSlate(self,slate):
        for key, value in slate.items():
                slate[key] *= self.moneyInPot/self.chipsInPot

    def log(self,slate):
        print('================================================')
        for key, value in slate.items():
            if value>0.01:
                print(key + ' is owed  %.2f dollars' % (value))
            elif value<-0.01:
                print(key + ' owes  %.2f dollars' % (-value))
            else:
                print(key + ' has clean slate')

    def logTransactions(self):
        print('================================================')
        for transaction in self.transactions:
            transaction.log()


    def update(self,checkConsistency=False):
        

        for transaction in self.transactions:
            if not transaction.addedToTab:
                transaction.addedToTab = True
                self.currentSlate[transaction.sender] +=  transaction.dollarAmount
                self.currentSlate[transaction.receiver] -=  transaction.dollarAmount
      
        if checkConsistency: 
            tmpSlate = self.initialSlate.copy()
            for transaction in self.transactions: 
                tmpSlate[transaction.sender] +=  transaction.dollarAmount
                tmpSlate[transaction.receiver] -=  transaction.dollarAmount         
            for key, value in tmpSlate.items():
                if not self.currentSlate[key] == value:
                    print('Inconsistency during transaction')
                    sys.exit()
            
            tmpSlate = {}

    def equilibrated(self):
        
        equilibrated = True
        for _, value in self.currentSlate.items():
            if abs(value)>0.01:
                equilibrated = False
                break
        return equilibrated

    def sort(self):
        # Sort current slate in Ascending Order
        self.currentSlate = {key: value for key, value in sorted(self.currentSlate.items(), key=lambda item: item[1])}
         

    def biggestOwer(self,sorted=False):
        if not sorted:
            biggestOwer = ''
            amountOwed = 0
            for key, value in self.currentSlate.items():
                if biggestOwer=='' or value<amountOwed:
                    biggestOwer = key
                    amountOwed = value 
        else:
            biggestOwer = list(self.currentSlate.keys())[0]
            amountOwed = self.currentSlate[biggestOwer]
        return biggestOwer, amountOwed
 
    def biggestOwed(self,sorted=False):
        if not sorted:
            biggestOwed = ''
            amountOwed = 0
            for key, value in self.currentSlate.items():
                if biggestOwed=='' or value>amountOwed:
                    biggestOwed = key
                    amountOwed = value
        else: 
            biggestOwed = list(self.currentSlate.keys())[-1]
            amountOwed = self.currentSlate[biggestOwed]
        return biggestOwed, amountOwed

    def biggestPreferedOwed(self,ower):
        listPreferedLinks = self.preferedLinks[ower]
        # Find the biggest owned in the list of prefered links
        biggestOwedLink = np.nan
        biggestOwedLinkAmount = np.nan
        for ilink, link in enumerate(listPreferedLinks):
            amountOwed = self.currentSlate[link]
            if ilink==0 or amountOwed>biggestOwedLinkAmount:
                biggestOwedLink = link
                biggestOwedLinkAmount = amountOwed
        return biggestOwedLink, biggestOwedLinkAmount


    def equilibrate(self):

        while not self.equilibrated():
            # Sort slate from biggest ower to biggest owed
            self.sort()
            # Find the biggest ower
            biggestOwer, amountFromOwer = self.biggestOwer(sorted=True)
            # Find the prefered link first
            biggestOwedLink, biggestOwedLinkAmount = self.biggestPreferedOwed(biggestOwer)
            if not np.isnan(biggestOwedLinkAmount) and biggestOwedLinkAmount*amountFromOwer<0:
                # Compute settlement
                settlement = min(-amountFromOwer,biggestOwedLinkAmount)
                # Transact
                self.addTransaction(sender=biggestOwer,receiver=biggestOwedLink,dollarAmount=settlement)
                self.update(checkConsistency=True)
            else:
                # Find the biggest owed
                biggestOwed, amountToOwed = self.biggestOwed(sorted=True)
                # Compute settlement
                settlement = min(-amountFromOwer,amountToOwed)
                # Transact
                self.addTransaction(sender=biggestOwer,receiver=biggestOwed,dollarAmount=settlement)
                self.update(checkConsistency=True)
             

    def addTransaction(self,sender,receiver,dollarAmount):
        self.transactions.append(Transaction(sender,receiver,dollarAmount))

