"""
TransactionManager

Stores transactions during a session
and writes them to the daily transactions file.
"""
from transaction import Transaction
class TransactionManager:
    def __init__(self):
        # all transactions in the system
        self.transactions = []
        self.transactionFile = ""

    # add new transaction
    def addTransaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def writeTransactionsToFile(self, filename: str):
        with open(filename, "w") as file:
            for transaction in self.transactions:
                file.write(transaction.formatForFile() + "\n")

            # write end of transactions record
            file.write("00                      00000 00000.00   \n")

    # retrieve all transactions
    def getAllTransactions(self):
        return self.transactions
    
    # clear all transactions
    def clearTransactions(self):
        self.transactions = []