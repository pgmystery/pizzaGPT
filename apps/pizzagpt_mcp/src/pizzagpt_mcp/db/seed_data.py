import argparse
import os
from sqlmodel import Session, select

from pizzagpt_mcp.db import database
from pizzagpt_mcp.db.models import *  # type: ignore


# Build parser but don't execute it at import time
_parser = argparse.ArgumentParser(description="DB init and seed/restore")
_parser.add_argument(
    "--mode",
    choices=["seed", "restore-sql", "auto"],
    default="auto",
    help="seed: ORM seed; restore-sql: import .sql; auto: restore if dump exists else seed",
)
_parser.add_argument(
    "--dump",
    default=os.getenv("DB_SQL_DUMP", "seed_dump.sql"),
    help="Path to SQL dump file for restore-sql/auto",
)


def already_seeded(session: Session) -> bool:
    return session.exec(select(Customer).limit(1)).first() is not None


def seed_with_orm():
    # ensure DB is initialized/migrated before seeding
    database.init_db()
    with Session(database.get_engine()) as session:
        if already_seeded(session):
            print("Seed skipped: data already present.")
            return

        # Ingredients
        ingredients = [
            Ingredient(name="Mozzarella", cost_cents=50),
            Ingredient(name="Tomato Sauce", cost_cents=20),
            Ingredient(name="Basil", cost_cents=10),
            Ingredient(name="Pepperoni", cost_cents=70),
            Ingredient(name="Mushrooms", cost_cents=40),
        ]
        session.add_all(ingredients)

        # Menu items
        margherita_s = MenuItem(
            name="Margherita", description="Tomato, mozzarella, basil", size="12in", price_cents=899
        )
        margherita_l = MenuItem(
            name="Margherita", description="Tomato, mozzarella, basil", size="16in", price_cents=1299
        )
        pepperoni_m = MenuItem(
            name="Pepperoni", description="Tomato, mozzarella, pepperoni", size="14in", price_cents=1199
        )
        funghi_m = MenuItem(
            name="Funghi", description="Tomato, mozzarella, mushrooms", size="14in", price_cents=1099
        )
        session.add_all([margherita_s, margherita_l, pepperoni_m, funghi_m])

        # Customers
        alice = Customer(name="Alice Johnson", email="alice@example.com", phone="+15551001")
        bob = Customer(name="Bob Smith", email="bob@example.com", phone="+15551002")
        session.add_all([alice, bob])
        session.commit()

        # Orders
        order1 = Order(customer_id=alice.id, status=OrderStatus.CONFIRMED, notes="Extra napkins, please.")
        session.add(order1)
        session.flush()
        oi1 = OrderItem(order_id=order1.id, menu_item_id=margherita_l.id, quantity=1)
        oi2 = OrderItem(order_id=order1.id, menu_item_id=pepperoni_m.id, quantity=2)
        order1.subtotal_cents = margherita_l.price_cents * oi1.quantity + pepperoni_m.price_cents * oi2.quantity
        order1.discount_cents = 0
        order1.tax_cents = int(round(order1.subtotal_cents * 0.08))
        order1.total_cents = order1.subtotal_cents - order1.discount_cents + order1.tax_cents
        oi1.line_total_cents = margherita_l.price_cents * oi1.quantity
        oi2.line_total_cents = pepperoni_m.price_cents * oi2.quantity
        session.add_all([oi1, oi2])

        order2 = Order(customer_id=bob.id, status=OrderStatus.PREPARING)
        session.add(order2)
        session.flush()
        oi3 = OrderItem(order_id=order2.id, menu_item_id=funghi_m.id, quantity=1, special_requests="Well done")
        oi4 = OrderItem(order_id=order2.id, menu_item_id=margherita_s.id, quantity=3)
        order2.subtotal_cents = funghi_m.price_cents * oi3.quantity + margherita_s.price_cents * oi4.quantity
        order2.discount_cents = 100
        order2.tax_cents = int(round((order2.subtotal_cents - order2.discount_cents) * 0.08))
        order2.total_cents = order2.subtotal_cents - order2.discount_cents + order2.tax_cents
        oi3.line_total_cents = funghi_m.price_cents * oi3.quantity
        oi4.line_total_cents = margherita_s.price_cents * oi4.quantity
        session.add_all([oi3, oi4])

        session.commit()
        print("Seeded via ORM.")


def restore_from_sql(dump_path: str):
    # ensure DB file exists/initialized before restore path resolution
    database.init_db()
    import sqlite3

    url = str(database.get_engine().url)
    if url.startswith("sqlite:///"):
        db_path = url.replace("sqlite:///", "", 1)
    elif url.startswith("sqlite:////"):
        db_path = url.replace("sqlite:////", "/", 1)
    else:
        raise RuntimeError("SQL restore currently supports SQLite only in this helper.")

    if not os.path.exists(dump_path):
        raise FileNotFoundError(f"Dump not found: {dump_path}")

    print(f"Restoring from SQL dump: {dump_path} -> {db_path}")
    with sqlite3.connect(db_path) as conn, open(dump_path, "r", encoding="utf-8") as f:
        sql = f.read()
        conn.executescript(sql)
    print("SQL restore completed.")


def run_seed_or_restore(argv: list[str] | None = None):
    # Parse only when explicitly called
    args = _parser.parse_args(argv)

    mode = args.mode
    dump_path = args.dump

    if mode == "seed":
        seed_with_orm()
    elif mode == "restore-sql":
        restore_from_sql(dump_path)
    else:  # auto
        if os.path.exists(dump_path):
            restore_from_sql(dump_path)
        else:
            seed_with_orm()
