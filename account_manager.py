"""
AccountManager

Manages all account objects.
Loads accounts from file and performs account operations.
"""

from account import Account, AccountPlan
class AccountManager:
    def __init__(self):
       
        # all accounts in the system
        self.accounts = {}
        self.nextAccountNumber = 1

    # create new account
    def createAccount(self, holderName: str, balance: float) -> Account:
        accountNumber = f"{self.nextAccountNumber:05d}"
        account = Account(accountNumber, holderName, balance)
        self.accounts[accountNumber] = account
        self.nextAccountNumber += 1
        return account
    
    # find account by number
    def getAccount(self, accountNumber: str) -> Account:
        return self.accounts.get(accountNumber)
    
    def deleteAccount(self, accountNumber: str):
        if accountNumber in self.accounts:
            del self.accounts[accountNumber]
    
    # disable account
    def disableAccount(self, accountNumber: str):
        account = self.getAccount(accountNumber)
        if account:
            account.disable()
    
    # change account plan
    def changeAccountPlan(self, accountNumber: str, newPlan: str) -> None:
        account = self.getAccount(accountNumber)
        if account:
            account.changePlan(newPlan)

    def loadAccountsFromFile(self, filename: str):
        # add logic
        try:
            with open(filename, "r") as file:
                for raw in file:
                    line = raw.strip()

                    if not line or line.startswith("END_OF_FILE"):
                        break
                    if len(line) < 30:
                        continue

                    acctNum = line[0:5].strip()
                    holderName = line[6:26].strip()
                    status = line[27]
                    balanceStr = line[29:].strip()
                    account = Account(acctNum, holderName, float(balanceStr))
                    if status == "D":
                            account.disable()
                    self.accounts[acctNum] = account

                    num = int(acctNum)
                    if num >= self.nextAccountNumber:
                        self.nextAccountNumber = num + 1

        except FileNotFoundError:
            print(f"Account file '{filename}' not found.")       