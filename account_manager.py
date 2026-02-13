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
    def createAccount(self, holderName: str, balance: float, password: str, email: str = None) -> Account:
        accountNumber = f"{self.nextAccountNumber:05d}"
        account = Account(accountNumber, holderName, balance, password, email)
        self.accounts[accountNumber] = account
        self.nextAccountNumber += 1
        return account
    # save accounts to file
    def saveAccountsToFile(self, filename: str):
        with open(filename, "w") as file:
            for account in self.accounts.values():
                status = "active" if account.isActive() else "disabled"
                line = f"{account.accountNumber} {account.holderName} {status} {account.balance:.2f} {account.password} {account.email}"
                file.write(line + "\n")
    # find account by holder name
    def findByHolderName(self, holderName: str):
        for account in self.accounts.values():
            if account.holderName.lower() == holderName.lower():
                return account
        return None
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
        try:
            with open(filename, "r") as file:
                for raw in file:
                    line = raw.strip()
                    if not line or line.startswith("END_OF_FILE"):
                        break
                    parts = line.split()
                    if len(parts) < 6:
                        continue
                    acctNum = parts[0]
                    holderName = parts[1]
                    status = parts[2]
                    balance = float(parts[3])
                    password = parts[4]
                    email = parts[5]
                    account = Account(acctNum, holderName, balance, password, email)
                    if status.lower() == "disabled" or status.lower() == "d":
                        account.disable()
                    self.accounts[acctNum] = account
                    num = int(acctNum)
                    if num >= self.nextAccountNumber:
                        self.nextAccountNumber = num + 1
        except FileNotFoundError:
            print(f"Account file '{filename}' not found.")