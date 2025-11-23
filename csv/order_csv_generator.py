import argparse
import random
from datetime import datetime

import pandas as pd
from faker import Faker

fake = Faker("en_AU")


def generate_order_id():
    """Generate unique order ID."""
    return f"CSV-ORD-{random.randint(100000, 999999)}"


def generate_order_name():
    """Generate a readable order name."""
    prefixes = ["Wholesale", "Retail", "Subscription", "Enterprise", "Priority", "Express"]
    descriptors = ["Bundle", "Plan", "Package", "Order", "Shipment", "Service"]
    return f"{random.choice(prefixes)} {random.choice(descriptors)} {random.randint(1, 999)}"


def generate_order_description():
    """Generate order description text."""
    descriptions = [
        "Monthly recurring subscription order",
        "One-off purchase for enterprise client",
        "Annual wholesale plan renewal",
        "Quarterly shipment for retail partner",
        "Custom implementation work order",
        "Expedited service engagement",
        "Pilot program enrollment",
    ]
    return random.choice(descriptions)


def generate_order_invoice_note(order_name):
    """Generate an invoice note referencing the order name."""
    notes = [
        "Invoice includes expedited fulfillment.",
        "Ensure payment per standard net terms.",
        "Apply loyalty discount if eligible.",
        "Reference PO provided by customer.",
        "Contact finance for billing adjustments.",
    ]
    return f"{random.choice(notes)} ({order_name})"


def _derive_account_choices(account_rows=None, account_ids=None, default_currency="AUD"):
    """Build list of (account_id, currency) tuples for assignment."""
    choices = []
    if account_rows:
        for row in account_rows:
            account_id = row.get("account_id")
            if not account_id:
                continue
            currency = row.get("account_currency") or default_currency
            choices.append((account_id, currency))
    elif account_ids:
        for account_id in account_ids:
            account_id = account_id.strip()
            if account_id:
                choices.append((account_id, default_currency))
    return choices


def generate_order_rows(order_count, account_rows=None, account_ids=None, default_currency="AUD"):
    """
    Create order rows using either generated account data or user-supplied account IDs.
    """
    account_choices = _derive_account_choices(account_rows, account_ids, default_currency=default_currency)
    if not account_choices:
        raise ValueError("No account IDs available to associate with orders.")

    rows = []
    for _ in range(order_count):
        order_name = generate_order_name()
        account_id, currency = random.choice(account_choices)
        rows.append(
            {
                "order_id": generate_order_id(),
                "order_name": order_name,
                "order_display_name": order_name,
                "order_description": generate_order_description(),
                "order_invoice_note": generate_order_invoice_note(order_name),
                "order_currency": currency or default_currency,
                "order_account_id": account_id,
            }
        )
    return rows


def generate_order_csv(order_count, account_rows=None, account_ids=None, default_currency="AUD"):
    """Generate an order CSV file and return its filepath."""
    rows = generate_order_rows(order_count, account_rows=account_rows, account_ids=account_ids, default_currency=default_currency)
    df = pd.DataFrame(rows).fillna("")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"ORDER_DUMMY_DATA_{order_count}_{timestamp}.csv"
    filepath = f"C:\\Users\\Rahman\\Downloads\\{filename}"
    df.to_csv(filepath, index=False)

    print(f"Successfully generated {order_count} orders.")
    print(f"Order file saved to: {filepath}")
    return filepath


def prompt_order_account_ids():
    """Prompt the user for account IDs to attach to orders."""
    while True:
        raw = input("Enter account IDs (comma-separated): ").strip()
        account_ids = [value.strip() for value in raw.split(",") if value.strip()]
        if account_ids:
            return account_ids
        print("Please enter at least one account ID.")


def prompt_order_count(default_count):
    """Prompt for number of orders to generate."""
    while True:
        raw = input(f"How many orders should be generated? (>=1, default {default_count}): ").strip()
        if raw == "":
            return max(1, default_count)
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number 1 or greater.")
            continue
        if value >= 1:
            return value
        print("Please enter a whole number 1 or greater.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate order CSV data.")
    parser.add_argument("count", type=int, nargs="?", default=200, help="Number of orders to generate (default: 200)")
    args = parser.parse_args()

    print("Standalone order CSV generation:")
    order_count = prompt_order_count(args.count)
    account_ids = prompt_order_account_ids()
    generate_order_csv(order_count, account_ids=account_ids)
