"""
Account

Represents a bank account.
Stores account details including status and plan,
and provides basic account operations.
"""

from enum import Enum

class AccountStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"

class AccountPlan(Enum):
    STANDARD = "standard"
    STUDENT = "student"

class Account:
    def __init__(self, accountNumber: str, holderName: str, balance: float):
        # account info
        self.accountNumber = accountNumber
        self.holderName = holderName
        self.balance = balance
        # account default status 
        self.status = AccountStatus.ACTIVE
        self.plan = AccountPlan.STANDARD

    # check if account is active
    def isActive(self) -> bool:
        return self.status == AccountStatus.ACTIVE

    # verify name matches account owner
    def matchesOwner(self, name: str) -> bool:
        return self.holderName.lower() == name.lower()

    # deposit or withdraw funds
    def adjustBalance(self, amount: float) -> None:
        self.balance += amount

    # disable account
    def disable(self) -> None:
        self.status = AccountStatus.DISABLED

    # change account plan
    def changePlan(self, newPlan: AccountPlan) -> None:
        self.plan = newPlan

    # debugging/display
    def __str__(self):
        return f"{self.accountNumber} | {self.holderName} | ${self.balance:.2f} | {self.status.value} | {self.plan.value}"