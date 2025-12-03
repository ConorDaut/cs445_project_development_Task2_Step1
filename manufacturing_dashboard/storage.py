# File: manufacturing_dashboard/storage.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import itertools


@dataclass
class Part:
    Part_Name: str
    Part_Size: str
    Part_ID: int
    Part_Price: float
    Order_ID: Optional[int] = None


@dataclass
class Order:
    Order_ID: int
    Account_ID: int
    Order_Price: float
    Order_Quantity: int
    Order_Date: datetime
    Order_Status: str  # e.g., "CURRENT", "PREVIOUS", "PENDING", "SHIPPED"
    Part_ID: int


@dataclass
class AccountRecord:
    Account_ID: int
    Account_Username: str
    Account_Password: str
    Account_Privilege: str  # "STANDARD" or "ADMIN"
    Account_Company: Optional[str] = None
    Account_Shipping_Address: Optional[str] = None
    Account_Contact_Info: Optional[str] = None


class InMemoryStore:
    def __init__(self):
        self._account_id_seq = itertools.count(1000)
        self._order_id_seq = itertools.count(5000)
        self._part_id_seq = itertools.count(2000)

        self.accounts: Dict[int, AccountRecord] = {}
        self.orders: Dict[int, Order] = {}
        self.parts: Dict[int, Part] = {}

    # Accounts
    def create_account(
        self,
        username: str,
        password: str,
        privilege: str,
        company: Optional[str] = None,
        shipping_address: Optional[str] = None,
        contact_info: Optional[str] = None,
    ) -> AccountRecord:
        acc_id = next(self._account_id_seq)
        record = AccountRecord(
            Account_ID=acc_id,
            Account_Username=username,
            Account_Password=password,
            Account_Privilege=privilege,
            Account_Company=company,
            Account_Shipping_Address=shipping_address,
            Account_Contact_Info=contact_info,
        )
        self.accounts[acc_id] = record
        return record

    def get_account_by_username(self, username: str) -> Optional[AccountRecord]:
        for acc in self.accounts.values():
            if acc.Account_Username == username:
                return acc
        return None

    def get_account(self, account_id: int) -> Optional[AccountRecord]:
        return self.accounts.get(account_id)

    def update_password(self, account_id: int, new_password: str) -> bool:
        acc = self.accounts.get(account_id)
        if not acc:
            return False
        acc.Account_Password = new_password
        return True

    # Orders
    def create_order(
        self,
        account_id: int,
        price: float,
        quantity: int,
        status: str,
        part_id: int,
        order_date: Optional[datetime] = None,
    ) -> Order:
        oid = next(self._order_id_seq)
        order = Order(
            Order_ID=oid,
            Account_ID=account_id,
            Order_Price=price,
            Order_Quantity=quantity,
            Order_Date=order_date or datetime.utcnow(),
            Order_Status=status,
            Part_ID=part_id,
        )
        self.orders[oid] = order
        return order

    def get_orders_for_account(self, account_id: int) -> List[Order]:
        return [o for o in self.orders.values() if o.Account_ID == account_id]

    def update_order_status(self, order_id: int, status: str) -> bool:
        order = self.orders.get(order_id)
        if not order:
            return False
        order.Order_Status = status
        return True

    def update_order_price_quantity(
        self, order_id: int, price: Optional[float] = None, quantity: Optional[int] = None
    ) -> bool:
        order = self.orders.get(order_id)
        if not order:
            return False
        if price is not None:
            order.Order_Price = price
        if quantity is not None:
            order.Order_Quantity = quantity
        return True

    # Parts
    def create_part(self, name: str, size: str, price: float) -> Part:
        pid = next(self._part_id_seq)
        part = Part(Part_Name=name, Part_Size=size, Part_ID=pid, Part_Price=price)
        self.parts[pid] = part
        return part

    def get_part(self, part_id: int) -> Optional[Part]:
        return self.parts.get(part_id)

    def link_part_to_order(self, part_id: int, order_id: int) -> bool:
        part = self.parts.get(part_id)
        order = self.orders.get(order_id)
        if not part or not order:
            return False
        part.Order_ID = order_id
        order.Part_ID = part_id
        return True
