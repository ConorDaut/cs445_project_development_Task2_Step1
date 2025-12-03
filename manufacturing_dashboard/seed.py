# File: manufacturing_dashboard/seed.py
from __future__ import annotations
from typing import Tuple
from .storage import InMemoryStore
from .users import AdminUser, StandardUser


def seed(store: InMemoryStore) -> Tuple[AdminUser, StandardUser]:
    # Seed parts
    p1 = store.create_part(name="Gear", size="M12", price=19.99)
    p2 = store.create_part(name="Bolt", size="M8", price=0.59)
    p3 = store.create_part(name="Bearing", size="6203", price=7.49)

    # Seed accounts
    admin_record = store.create_account("admin", "admin123", "ADMIN")
    std_record = store.create_account(
        "conor", "pass123", "STANDARD", company="Cape Manufacturing LLC", shipping_address="123 River Rd, Cape Girardeau, MO", contact_info="conor@cape-mfg.com"
    )

    admin = AdminUser.from_record(admin_record, store)
    std = StandardUser.from_record(std_record, store)

    # Seed orders
    o1 = store.create_order(account_id=std.Account_ID, price=p1.Part_Price * 10, quantity=10, status="CURRENT", part_id=p1.Part_ID)
    store.link_part_to_order(p1.Part_ID, o1.Order_ID)

    o2 = store.create_order(account_id=std.Account_ID, price=p2.Part_Price * 200, quantity=200, status="PREVIOUS", part_id=p2.Part_ID)
    store.link_part_to_order(p2.Part_ID, o2.Order_ID)

    o3 = store.create_order(account_id=std.Account_ID, price=p3.Part_Price * 5, quantity=5, status="CURRENT", part_id=p3.Part_ID)
    store.link_part_to_order(p3.Part_ID, o3.Order_ID)

    return admin, std
