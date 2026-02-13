from enum import Enum
class SessionMode(Enum):
    STANDARD = "standard"
    ADMIN = "admin"

class Session:
    def __init__(self):
        self.loggedIn = False
        self.mode = None 
        self.currentUser = " "
        self.withdrawTotal = 0.0
        self.transferTotal = 0.0
        self.paybillTotal = 0.0

    # start up a session
    def login(self, mode: SessionMode, userName: str = None) -> None:
        self.loggedIn = True
        self.mode = mode
        self.currentUser = userName
        self.resetTotals()

    # end a session
    def logout(self) -> None:
        self.loggedIn = False
        self.mode = None
        self.currentUser = " "  
        self.resetTotals()

    # check if logged in
    def isLoggedIn(self) -> bool:
        return self.loggedIn
    
    # check if admin session
    def isAdmin(self) -> bool:
        return self.loggedIn and self.mode == SessionMode.ADMIN
    
    # check if standard user session
    def canWithdraw(self, amount: float) -> bool:
        if self.mode == SessionMode.ADMIN:
            return True
        return (self.withdrawTotal + amount) <= 500.0
    
    # check if transfer is within limits
    def canTransfer(self, amount: float) -> bool:
        if self.mode == SessionMode.ADMIN:
            return True
        return (self.transferTotal + amount) <= 1000.0
    
    # check if paybill is within limits
    def canPayBill(self, amount: float) -> bool:
        if self.mode == SessionMode.ADMIN:
            return True
        return (self.paybillTotal + amount) <= 2000.0
    
    # record withdrawal amount
    def recordTransfer(self, amount: float) -> None:
        self.transferTotal += amount
    
    # record withdrawal amount
    def recordPayBill(self, amount: float) -> None:
        self.paybillTotal += amount

    def recordWithdraw(self, amount: float) -> None:
        self.withdrawTotal += amount

    # reset totals
    def resetTotals(self) -> None:
        self.withdrawTotal = 0.0
        self.transferTotal = 0.0
        self.paybillTotal = 0.0