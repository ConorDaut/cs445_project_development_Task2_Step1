# File: manufacturing_dashboard/users.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Literal
from datetime import datetime

from .storage import InMemoryStore, AccountRecord, Order, Part

Privilege = Literal["STANDARD", "ADMIN"]


@dataclass
class UserAccount:
    Account_ID: int
    Account_Username: str
    Account_Password: str
    Account_Privilege: Privilege
    _store: InMemoryStore

    # Operations: login(), change_password(), create_account(), view_current_orders(), view_previous_orders()

    def login(self, username: str, password: str) -> Optional["UserAccount"]:
        record = self._store.get_account_by_username(username)
        if record and record.Account_Password == password:
            if record.Account_Privilege == "ADMIN":
                return AdminUser.from_record(record, self._store)
            else:
                return StandardUser.from_record(record, self._store)
        return None

    def change_password(self, new_password: str) -> bool:
        return self._store.update_password(self.Account_ID, new_password)

    def create_account(
        self,
        username: str,
        password: str,
        privilege: Privilege,
        company: Optional[str] = None,
        shipping_address: Optional[str] = None,
        contact_info: Optional[str] = None,
    ) -> "UserAccount":
        record = self._store.create_account(
            username=username,
            password=password,
            privilege=privilege,
            company=company,
            shipping_address=shipping_address,
            contact_info=contact_info,
        )
        if record.Account_Privilege == "ADMIN":
            return AdminUser.from_record(record, self._store)
        return StandardUser.from_record(record, self._store)

    def view_current_orders(self) -> List[Order]:
        return [o for o in self._store.get_orders_for_account(self.Account_ID) if o.Order_Status.upper() == "CURRENT"]

    def view_previous_orders(self) -> List[Order]:
        return [o for o in self._store.get_orders_for_account(self.Account_ID) if o.Order_Status.upper() == "PREVIOUS"]


@dataclass
class StandardUser(UserAccount):
    Account_Company: Optional[str] = None
    Account_Shipping_Address: Optional[str] = None
    Account_Contact_Info: Optional[str] = None

    # Operations: view_account_info() and order_parts()

    def view_account_info(self) -> dict:
        return {
            "Account_ID": self.Account_ID,
            "Account_Username": self.Account_Username,
            "Account_Privilege": self.Account_Privilege,
            "Account_Company": self.Account_Company,
            "Account_Shipping_Address": self.Account_Shipping_Address,
            "Account_Contact_Info": self.Account_Contact_Info,
        }

    def order_parts(self, part_id: int, quantity: int) -> Optional[Order]:
        part = self._store.get_part(part_id)
        if not part or quantity <= 0:
            return None
        price = part.Part_Price * quantity
        order = self._store.create_order(
            account_id=self.Account_ID,
            price=price,
            quantity=quantity,
            status="CURRENT",
            part_id=part.Part_ID,
            order_date=datetime.utcnow(),
        )
        self._store.link_part_to_order(part.Part_ID, order.Order_ID)
        return order

    @staticmethod
    def from_record(record: AccountRecord, store: InMemoryStore) -> "StandardUser":
        return StandardUser(
            Account_ID=record.Account_ID,
            Account_Username=record.Account_Username,
            Account_Password=record.Account_Password,
            Account_Privilege="STANDARD",
            _store=store,
            Account_Company=record.Account_Company,
            Account_Shipping_Address=record.Account_Shipping_Address,
            Account_Contact_Info=record.Account_Contact_Info,
        )


@dataclass
class AdminUser(UserAccount):
    # Operations: sort_orders() and update_modify_orders()

    def sort_orders(self, key: str = "Order_Date", reverse: bool = False) -> List[Order]:
        orders = list(self._store.orders.values())
        valid_keys = {"Order_ID", "Account_ID", "Order_Price", "Order_Quantity", "Order_Date", "Order_Status", "Part_ID"}
        if key not in valid_keys:
            key = "Order_Date"
        return sorted(orders, key=lambda o: getattr(o, key), reverse=reverse)

    def update_modify_orders(
        self,
        order_id: int,
        new_status: Optional[str] = None,
        new_price: Optional[float] = None,
        new_quantity: Optional[int] = None,
    ) -> bool:
        ok = True
        if new_status is not None:
            ok = ok and self._store.update_order_status(order_id, new_status)
        if new_price is not None or new_quantity is not None:
            ok = ok and self._store.update_order_price_quantity(order_id, price=new_price, quantity=new_quantity)
        return ok

    @staticmethod
    def from_record(record: AccountRecord, store: InMemoryStore) -> "AdminUser":
        return AdminUser(
            Account_ID=record.Account_ID,
            Account_Username=record.Account_Username,
            Account_Password=record.Account_Password,
            Account_Privilege="ADMIN",
            _store=store,
        )
