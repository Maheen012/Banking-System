"""
FrontendMain

Controls execution of the ATM system.
Reads commands from standard input.
Loads accounts from current_accounts.txt.
Writes daily transactions to transactions.txt.
"""

from account_manager import AccountManager
from session import Session, SessionMode
from transaction import Transaction
from transaction_manager import TransactionManager
from account import AccountPlan


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
            self.transactionManager.writeTransactionsToFile(self.transactionsFile)
            print("Transactions saved to file.")
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

    def handleLogin(self):
        if self.session.isLoggedIn():
            print("Already logged in!")
            return

        modeInput = input("Enter mode (admin/standard): ").strip().lower()

        if modeInput == "admin":
            mode = SessionMode.ADMIN
        elif modeInput == "standard":
            mode = SessionMode.STANDARD
        else:
            print("Invalid mode!")
            return

        username = input("Enter username: ").strip()

        if not username:
            print("Username cannot be empty!")
            return

        self.session.login(mode, username)
        print(f"Login successful. Welcome {username}.")

    def handleLogout(self):
        if not self.session.isLoggedIn():
            print("No user currently logged in!")
            return

        print("Logging out...")
        self.session.logout()

        # Write all recorded transactions to output file
        self.transactionManager.writeTransactionsToFile(self.transactionsFile)

        print("Transactions saved to file.")


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
            self.session.recordPayBill(amount)
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
        if not self.session.isLoggedIn():
            print("You must be logged in!")
            return

        if self.session.isAdmin():
            holderName = input("Enter account holder name: ").strip()
        else:
            holderName = self.session.currentUser
        accountNumber = input("Enter account number: ").strip()

        try:
            amount = float(input("Enter withdrawal amount ($): "))
            if amount <= 0:
                print("Amount must be positive!")
                return

            if not self.session.canWithdraw(amount):
                print("Withdrawal limit exceeded!")
                return

            account = self.accountManager.getAccount(accountNumber)

            if not account:
                print("Account not found!")
                return

            if not self.session.isAdmin() and account.holderName != holderName:
                print("You can only withdraw from your own account!")
                return

            if account.balance < amount:
                print("Insufficient funds!")
                return

            account.adjustBalance(-amount)
            self.session.recordWithdraw(amount)

            print("Withdrawal successful.")

            transaction = Transaction("01", holderName, accountNumber, amount, "")
            self.transactionManager.addTransaction(transaction)

        except ValueError:
            print("Invalid amount entered!")
            
    def handleTransfer(self):
        if not self.session.isLoggedIn():
            print("You must be logged in!")
            return

        if self.session.isAdmin():
            holderName = input("Enter account holder name: ").strip()
        else:
            holderName = self.session.currentUser
        fromAccountNum = input("Enter source account number: ").strip()
        toAccountNum = input("Enter destination account number: ").strip()

        try:
            amount = float(input("Enter transfer amount ($): "))
            if amount <= 0:
                print("Amount must be positive!")
                return

            if not self.session.canTransfer(amount):
                print("Transfer limit exceeded!")
                return

            fromAccount = self.accountManager.getAccount(fromAccountNum)
            toAccount = self.accountManager.getAccount(toAccountNum)

            if not fromAccount or not toAccount:
                print("Invalid account number!")
                return

            if not self.session.isAdmin() and fromAccount.holderName != holderName:
                print("You can only transfer from your own account!")
                return

            if fromAccount.balance < amount:
                print("Insufficient funds!")
                return

            fromAccount.adjustBalance(-amount)
            toAccount.adjustBalance(amount)
            self.session.recordTransfer(amount)

            print("Transfer successful.")

            transaction = Transaction("02", holderName, fromAccountNum, amount, toAccountNum)
            self.transactionManager.addTransaction(transaction)

        except ValueError:
            print("Invalid amount entered!")

# Admin Only Operations
# handleDisable will disable an existing account, and record a disable transaction. Its also an admin only operation
    def handleDisable(self):
    # Ensures a user is logged in before proceeding
        if not self.session.isLoggedIn():
            print("You must be logged in!")
            return
    # Only admins are allowed to disable accounts
        if not self.session.isAdmin():
            print("Only admins can disable accounts!")
            return
    # Prompt admin for account number to disable
        accountNumber = input("Enter account number to disable: ").strip()
        account = self.accountManager.getAccount(accountNumber)
    # Validate that account exists
        if not account:
            print("Account not found!")
            return
     # Prevent disabling an already disabled account
        if not account.isActive():
            print("Account already disabled!")
            return

        self.accountManager.disableAccount(accountNumber)
        print("Account disabled successfully.")
    # Record disable transaction (07 = disable code)
        transaction = Transaction("07", account.holderName, accountNumber, 0.0, "")
        self.transactionManager.addTransaction(transaction)

# handleDelete deletes an existing account and record a delete transaction. Its also an admin only operation.
    def handleDelete(self):
 # Ensure a user is logged in before proceeding
        if not self.session.isLoggedIn():
            print("You must be logged in!")
            return
 # Only admins are allowed to delete accounts
        if not self.session.isAdmin():
            print("Only admins can delete accounts!")
            return

        accountNumber = input("Enter account number to delete: ").strip()
        account = self.accountManager.getAccount(accountNumber)
# Validate account existence
        if not account:
            print("Account not found!")
            return

        self.accountManager.deleteAccount(accountNumber)
        print("Account deleted successfully.")
 # Record delete transaction (06 = delete code)
        transaction = Transaction("06", account.holderName, accountNumber, 0.0, "")
        self.transactionManager.addTransaction(transaction)

# handleChangePlan changes the payment plan of an account and record a change plan transaction. Its also an admin only operation
    def handleChangePlan(self):
# Ensure a user is logged in
        if not self.session.isLoggedIn():
            print("You must be logged in!")
            return
# Only admins are allowed to change account plans
        if not self.session.isAdmin():
            print("Only admins can change account plans!")
            return

        accountNumber = input("Enter account number: ").strip()
        newPlanInput = input("Enter new plan (S for Student, N for Normal): ").strip().upper()

        account = self.accountManager.getAccount(accountNumber)
 # Validate account existence
        if not account:
            print("Account not found!")
            return
            
# Determine correct AccountPlan enum value
        if newPlanInput == "S":
            newPlan = AccountPlan.STUDENT
        elif newPlanInput == "N":
            newPlan = AccountPlan.NORMAL
        else:
            print("Invalid plan type!")
            return
 # Update account plan through AccountManager
        self.accountManager.changeAccountPlan(accountNumber, newPlan)
        print("Account plan updated successfully.")
 # Record change-plan transaction (08 = change plan code)
        transaction = Transaction("08", account.holderName, accountNumber, 0.0, newPlanInput)
        self.transactionManager.addTransaction(transaction)
        


if __name__ == "__main__":
    frontend = FrontendMain()

    frontend.run()
