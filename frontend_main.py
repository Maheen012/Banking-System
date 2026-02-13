from account_manager import AccountManager
from session import Session, SessionMode
from transaction import Transaction
from transaction_manager import TransactionManager
# import other necessary modules and classes

class FrontendMain:
    def __init__(self):
        self.accountManager = AccountManager()
        self.transactionManager = TransactionManager()
        self.session = Session()
        self.accountsFile = "current_accounts.txt"
        self.transactionsFile = "transactions.txt"

        self.commands = {
            'create': self.handleCreate,
            'deposit': self.handleDeposit,
            'paybill': self.handlePayBill,
            'withdraw': self.handleWithdraw,
            'transfer': self.handleTransfer,
            'disable': self.handleDisable,
            'delete': self.handleDelete,
            'changeplan': self.handleChangePlan,
        }

    def run(self):
        self.welcomeMessage() # display welcome message
        self.accountManager.loadAccountsFromFile(self.accountsFile) # load accounts from file

        while True:
            command = input("ATM> ").strip().lower()
            self.processCommand(command)

    def welcomeMessage(self):
        print("================================")
        print("Welcome to the Bank ATM System!")
        print("================================")

    def processCommand(self, command: str):
        if command in ["exit","quit"]:
            print("Thank you for using the ATM. Goodbye!")
            exit(0)

        elif command == "login":
            self.handleLogin()
        elif command == "logout":
            self.handleLogout()
        elif command in self.commands:
            self.commands[command]()
        else:
            print("Invalid command!")
    
    # Session commands
    


    # didnt complete






    # Standard user commands
    def handleCreate(self):
        if not self.session.isLoggedIn():
            print("You must be logged in!")
            return
        
        if not self.session.isAdmin():
            print("Only admins can create accounts!")
            return
        
        try:
            holderName = input("Enter account holder name: ")
            if not holderName or len(holderName) > 20:
                print("Name cannot be empty or longer than 20 characters!")
                return
            balance = float(input("Enter starting balance ($): "))
            if balance < 0:
                print("Balance cannot be negative!")
                return
            
            account = self.accountManager.createAccount(holderName, balance)
            print("Account successfully created!")
            print(f"New Account Number: {account.accountNumber}")

            # record transaction (05 is creation code)
            transaction = Transaction("05", holderName, account.accountNumber, balance, "")
            self.transactionManager.addTransaction(transaction)

        except ValueError:
            print("Invalid amount entered!")

    def handleDeposit(self):
        if not self.session.isLoggedIn():
            print("You must be logged in to deposit!")
            return
        
        if self.session.isAdmin():
            holderName = input("Enter account holder name: ").strip()
        else:
            holderName = self.session.currentUser

        accountNumber = input("Enter account number: ")
        
        try:
            amount = float(input("Enter deposit amount($): "))
            if amount <= 0:
                print("Deposit amount must be positive!")
                return
            
            account = self.accountManager.getAccount(accountNumber)
            if not account:
                print("Account was not found! Please try again.")
                return
            
            # Standard users can only deposit to their own account
            if not self.session.isAdmin() and not account.matchesOwner(holderName):
                print("You can only deposit to your own account!")
                return

            # account.adjustBalance(amount)
            print("Deposit was successful! Funds will be availble in next session.")

            # record transaction (04 is deposit code)
            transaction = Transaction("04", holderName, account.accountNumber, amount, "")
            self.transactionManager.addTransaction(transaction)

        except ValueError:
            print("Invalid amount entered!")

    def handlePayBill(self):
        if not self.session.isLoggedIn():
            print("You must be logged in to pay a bill!")
            return
        
        if self.session.isAdmin():
            holderName = input("Enter account holder name: ").strip()
        else:
            holderName = self.session.currentUser

        accountNumber = input("Enter account number: ")
        
        # valid payees and print options
        validPayees = {
            'ec': 'The Bright Light Electric Company (EC)',
            'cq': 'Credit Card Company Q (CQ)',
            'fi': 'Fast Internet, Inc. (FI)'
        }

        payeeCode = input("Enter payee code (EC, CQ, FI): ").strip().lower()
        if payeeCode not in validPayees:
            print("Invalid payee code!")
            return
        
        try:
            amount = float(input("Enter bill amount($): "))
            if amount <= 0:
                print("Bill amount must be positive!")
                return
            
            if not self.session.canPayBill(amount):
                print("Session paybill limit exceeded ($2000)!")
                return
            
            account = self.accountManager.getAccount(accountNumber)
            if not account:
                print("Account was not found! Please try again.")
                return
            
            if not self.session.isAdmin() and account.holderName != holderName:
                print("You can only pay bills from your own account!")
                return
            
            if account.balance - amount < 0:
                print("Insufficient funds!")
                return
            
            account.adjustBalance(-amount)
            print("Bill payment was successful!")
            print(f"Payee: {validPayees[payeeCode]}")
            print(f"Current Balance: ${account.balance:.2f}")

            # record transaction (03 is paybill code)
            transaction = Transaction("03", holderName, account.accountNumber, amount, validPayees[payeeCode])
            self.transactionManager.addTransaction(transaction)

        except ValueError:
            print("Invalid amount entered!")


    # Admin commands (commented out)
    def handleWithdraw(self):
        
    def handleTransfer(self):
        
    def handleDisable(self):
        
    def handleDelete(self):
        
    def handleChangePlan(self):
        


if __name__ == "__main__":
    frontend = FrontendMain()
    frontend.run()