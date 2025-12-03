# File: manufacturing_dashboard/main.py
from __future__ import annotations
from typing import Optional
from datetime import datetime

from .storage import InMemoryStore
from .users import UserAccount, AdminUser, StandardUser
from .seed import seed


def print_order(order) -> None:
    print(
        f"Order_ID={order.Order_ID} | Account_ID={order.Account_ID} | Part_ID={order.Part_ID} | "
        f"Qty={order.Order_Quantity} | Price=${order.Order_Price:.2f} | Status={order.Order_Status} | "
        f"Date={order.Order_Date.isoformat(timespec='seconds')}"
    )


def run_demo() -> None:
    store = InMemoryStore()
    admin, std = seed(store)

    print("== Manufacturing Dashboard Demo ==")
    print("\n-- Standard User: view_account_info() --")
    print(std.view_account_info())

    print("\n-- Standard User: view_current_orders() --")
    for o in std.view_current_orders():
        print_order(o)

    print("\n-- Standard User: view_previous_orders() --")
    for o in std.view_previous_orders():
        print_order(o)

    print("\n-- Standard User: order_parts() (ordering 12 Bolts) --")
    bolt_part_id = next(pid for pid, part in store.parts.items() if part.Part_Name == "Bolt")
    new_order = std.order_parts(part_id=bolt_part_id, quantity=12)
    if new_order:
        print_order(new_order)

    print("\n-- Admin User: sort_orders() by Price desc --")
    for o in admin.sort_orders(key="Order_Price", reverse=True):
        print_order(o)

    print("\n-- Admin User: update_modify_orders() (set newest order to PREVIOUS and change quantity) --")
    newest = max(store.orders.values(), key=lambda x: x.Order_Date)
    admin.update_modify_orders(order_id=newest.Order_ID, new_status="PREVIOUS", new_quantity=newest.Order_Quantity + 3)
    print_order(store.orders[newest.Order_ID])

    print("\n-- Authentication: UserAccount.login() --")
    # Any user can call login; using std instance as entry
    logged_in = std.login(username="admin", password="admin123")
    print(f"Login as 'admin' successful? {isinstance(logged_in, AdminUser)}")

    print("\n-- Password change: change_password() --")
    ok = std.change_password("newpass456")
    print(f"Password changed? {ok}")
    re_login = std.login(username="conor", password="newpass456")
    print(f"Re-login as 'conor' successful? {isinstance(re_login, StandardUser)}")

    print("\n-- Admin creates a new account: create_account() --")
    new_std = admin.create_account(
        username="jane",
        password="pw123",
        privilege="STANDARD",
        company="RiverWorks",
        shipping_address="44 Water St",
        contact_info="jane@riverworks.com",
    )
    print(f"Created account: {new_std.view_account_info()}")


if __name__ == "__main__":
    run_demo()
