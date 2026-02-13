"""
transaction.py - Represents a single transaction record
"""

# create transaction record
class Transaction:
    def __init__(self, code: str, holderName: str, accountNumber: str, amount: float = 0.0, extra: str = ""):
        self.code = code # transaction code
        self.holderName = holderName # account holder name
        self.accountNumber = accountNumber # account number
        self.amount = amount # transaction amount
        self.extra = extra # additional info

    # format transaction for writing to file
    def formatTransaction(self) -> str:
        # CC_AAAAAAAAAAAAAAAAAAAA_NNNNN_PPPPPPPP_MM
        code = f"{int(self.code):02}" 
        holder = f"{self.holderName[:20]:<20}"

        acctNum = str(self.accountNumber).zfill(5)
        amount = f"{abs(self.amount):08.2f}" 
        extra = f"{self.extra[:2]:<2}" 
        return f"{code} {holder} {acctNum} {amount}{extra}"
    
    def formatForFile(self) -> str:
        return self.formatTransaction()
    # debugging
    def __str__(self):
        return f"{self.code} | {self.holderName} | {self.accountNumber} | {self.amount:.2f} | {self.extra}"