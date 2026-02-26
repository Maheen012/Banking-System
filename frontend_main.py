# =========================================================
# Program: frontend_main.py
# Course: CSCI 3060U - Winter 2025
# Group: Class Project Group 27
# =========================================================
# Purpose:
#   This program simulates the Front End of a banking system ATM.
#   It reads transaction commands from terminal input,
#   processes them one at a time, updates account balances, and
#   generates a daily bank account transaction file at the end of a session.
#   It supports both standard and admin (privileged) modes.
#
# Input Files:
#   - currentaccounts.txt               contains current bank account records
#   - Test input files (.txt)           contain sequences of transactions for testing
#
# Output Files:
#   - transout.atf                      daily transaction file containing all
#                                       transactions performed during the session
#   - Terminal log / Outputs (.out)     captures everything printed to terminal
#                                       during execution (used for testing)
#
# How to Run:
#   - From terminal:
#       python frontend_main.py current_accounts.txt transout.atf
# =========================================================

from account_manager import AccountManager
from session import Session, SessionMode
from transaction import Transaction
from transaction_manager import TransactionManager
from account import AccountPlan
import sys


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
            'viewbalance': self.handleViewBalance,
        }
        self._input_iter = None

    def get_input(self, prompt=""):
        if self._input_iter is not None:
            try:
                value = next(self._input_iter)
                print(f"{prompt}{value}")
                return value
            except StopIteration:
                print("[ERROR] Not enough input lines in command file for prompts.")
                sys.exit(1)
        else:
            return input(prompt)
    def handleViewBalance(self):
        if not self.session.isLoggedIn():
            print("You must be logged in!")
            return

        if self.session.isAdmin():
            holderName = self.get_input("Enter account holder name: ").strip()
        else:
            holderName = self.session.currentUser

        accountNumber = self.get_input("Enter account number: ").strip()
        account = self.accountManager.getAccount(accountNumber)

        if not account:
            print("Account not found!")
            return

        if not self.session.isAdmin() and account.holderName != holderName:
            print("You can only view your own account!")
            return

        print(f"Current Balance: ${account.balance:.2f}")

    def run(self, command_file=None):
        self.welcomeMessage() # display welcome message
        self.accountManager.loadAccountsFromFile(self.accountsFile) # load accounts from file

        if command_file:
            try:
                with open(command_file, 'r') as f:
                    commands = [line.strip() for line in f if line.strip()]
                self._input_iter = iter(commands)
                while True:
                    try:
                        command = next(self._input_iter)
                        print(f"ATM> {command}")  # Echo command for logs
                    except StopIteration:
                        break
                    self.processCommand(command.lower())
            except FileNotFoundError:
                print(f"Command file '{command_file}' not found.")
                sys.exit(1)
        else:
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
            
        
    def handleLogin(self):
        if self.session.isLoggedIn():
            print("Already logged in!")
            return

        while True:
            modeInput = self.get_input("Enter mode (admin/standard): ").strip().lower()
            if modeInput == "admin":
                mode = SessionMode.ADMIN
                break
            elif modeInput == "standard":
                mode = SessionMode.STANDARD
                break
            else:
                print("Mode incorrect, please enter 'admin' or 'standard'.")

        if mode == SessionMode.STANDARD:
            username = self.get_input("Enter account holder name: ").strip()
            account = self.accountManager.findByHolderName(username)

            if not account:
                print("User does not exist.")
                return
            self.session.login(mode, username)
        else:
            self.session.login(mode,"admin")

        print("Login is successful!")

    def handleLogout(self):
        if not self.session.isLoggedIn():
            print("No user currently logged in!")
            return

        print("Logging out...")
        self.session.logout()

        # Write all recorded transactions to output file
        self.transactionManager.writeTransactionsToFile(self.transactionsFile)


        print("Transactions and accounts saved to file.")


    # Standard user commands
    def handleCreate(self):
        if not self.session.isLoggedIn() or not self.session.isAdmin():
            print("Only admins can create accounts!")
            return

        try:
            username = self.get_input("Enter account holder name: ").strip()
            if len(username) > 20:
                print("Name must be 20 characters or less!")
                return

            balance = float(self.get_input("Enter starting balance: "))
            if balance < 0 or balance > 99999.99:
                print("Balance must be between $0.00 and $99,999.99!")
                return

            account = self.accountManager.createAccount(username, balance)
            print("Account successfully created!")
            print(f"New Account Number: {account.accountNumber}")

            transaction = Transaction(
                "05", username, account.accountNumber, balance, ""
            )
            self.transactionManager.addTransaction(transaction)

        except ValueError:
            print("Invalid input!")

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
            transaction = Transaction("03", holderName, account.accountNumber, amount, payeeCode.upper())
            self.transactionManager.addTransaction(transaction)

        except ValueError:
            print("Invalid amount entered!")


    # Admin commands (commented out)
    def handleWithdraw(self):
        if not self.session.isLoggedIn():
            print("You must be logged in!")
            return

        if self.session.isAdmin():
            holderName = self.get_input("Enter account holder name: ").strip()
        else:
            holderName = self.session.currentUser
        accountNumber = self.get_input("Enter account number: ").strip()

        try:
            amount_str = self.get_input("Enter withdrawal amount ($): ").strip()
            amount = float(amount_str)
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
            holderName = self.get_input("Enter account holder name: ").strip()
        else:
            holderName = self.session.currentUser
        fromAccountNum = self.get_input("Enter source account number: ").strip()
        toAccountNum = self.get_input("Enter destination account number: ").strip()

        try:
            amount = float(self.get_input("Enter transfer amount ($): "))
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

    def handleChangePlan(self):
        # Ensure a user is logged in & is admin
        if not self.session.isLoggedIn() or not self.session.isAdmin():
            print("Only admins can change account plans!")
            return

        accountNumber = input("Enter account number: ").strip()
        account = self.accountManager.getAccount(accountNumber)

        if not account:
            print("Account not found!")
            return
        
        newPlanInput = input("Enter new plan (S for Student, N for Non-student): ").strip().upper()

        # Validate account existence
        account = self.accountManager.getAccount(accountNumber)
        if not account:
            print("Account not found!")
            return
            
        # Determine correct AccountPlan enum value
        if newPlanInput == "S":
            newPlan = AccountPlan.STUDENT
        elif newPlanInput == "N":
            newPlan = AccountPlan.NON_STUDENT
        else:
            print("Invalid plan type!")
            return
        
        # Update account plan through AccountManager
        self.accountManager.changeAccountPlan(accountNumber, newPlan)
        print("Account plan updated successfully!")

        # Record change-plan transaction (08 = change plan code)
        transaction = Transaction("08", account.holderName, accountNumber, 0.0, newPlanInput)
        self.transactionManager.addTransaction(transaction)
        


if __name__ == "__main__":
    # Usage: python frontend_main.py <accounts_file> <transactions_file> [<command_file>]
    if len(sys.argv) not in (3, 4):
        print("Usage: python frontend_main.py <accounts_file> <transactions_file> [<command_file>]")
        sys.exit(1)

    accounts_file = sys.argv[1]
    transactions_file = sys.argv[2]
    command_file = sys.argv[3] if len(sys.argv) == 4 else None

    frontend = FrontendMain()
    frontend.accountsFile = accounts_file
    frontend.transactionsFile = transactions_file

    frontend.run(command_file)
