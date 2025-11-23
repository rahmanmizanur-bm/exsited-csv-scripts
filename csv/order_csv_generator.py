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


DEFAULT_ORDER_ATTR_OPTIONS = ["A", "B", "C", "D"]
DEFAULT_ORDER_RADIO_OPTIONS = [str(i) for i in range(1, 51)]


def get_default_order_custom_attributes():
    """Default set of 10 order custom attributes."""
    def make_attr(name, attr_type, options=None, quantity_min=None, quantity_max=None):
        return {
            "column_name": f"ca_order_attr_{name}",
            "type": attr_type,
            "constant": False,
            "value": None,
            "options": options or [],
            "quantity_min": quantity_min,
            "quantity_max": quantity_max,
        }

    return [
        make_attr("CA_BOOL", "bool"),
        make_attr("CA_CHECKBOX", "checkboxes", options=DEFAULT_ORDER_ATTR_OPTIONS),
        make_attr("CA_DATE", "date"),
        make_attr("CA_DROPDOWN", "dropdown", options=DEFAULT_ORDER_ATTR_OPTIONS),
        make_attr("CA_DROPDOWN_WITH_MULTISELECT", "dropdown_multi", options=DEFAULT_ORDER_ATTR_OPTIONS),
        make_attr("CA_MONEY", "money"),
        make_attr("CA_QUANTITY", "quantity", quantity_min=1, quantity_max=50),
        make_attr("CA_NUMBER", "number"),
        make_attr("CA_RADIO", "radio", options=DEFAULT_ORDER_RADIO_OPTIONS),
        make_attr("CA_TEXT", "text"),
    ]


def _random_value_for_attr(attr):
    attr_type = attr["type"]
    options = attr.get("options") or []
    if attr_type == "bool":
        return random.choice([True, False])
    if attr_type == "checkboxes":
        k = random.randint(1, len(options)) if options else 0
        return ",".join(random.sample(options, k=k)) if k else ""
    if attr_type == "date":
        return datetime.now().strftime("%Y-%m-%d")
    if attr_type == "dropdown":
        return random.choice(options) if options else ""
    if attr_type == "dropdown_multi":
        k = random.randint(1, len(options)) if options else 0
        return ",".join(random.sample(options, k=k)) if k else ""
    if attr_type == "money":
        return round(random.uniform(1, 10000), 2)
    if attr_type == "quantity":
        qmin = attr.get("quantity_min") or 1
        qmax = attr.get("quantity_max") or 50
        qmin = int(qmin)
        qmax = int(qmax)
        if qmin > qmax:
            qmin, qmax = qmax, qmin
        return random.randint(qmin, qmax)
    if attr_type == "number":
        return random.randint(0, 1000)
    if attr_type == "radio":
        return random.choice(options) if options else ""
    if attr_type == "text":
        return fake.sentence(nb_words=6)
    return ""


def generate_order_rows(order_count, account_rows=None, account_ids=None, default_currency="AUD", custom_attributes=None):
    """
    Create order rows using either generated account data or user-supplied account IDs.
    """
    account_choices = _derive_account_choices(account_rows, account_ids, default_currency=default_currency)
    if not account_choices:
        raise ValueError("No account IDs available to associate with orders.")

    if custom_attributes is None:
        custom_attributes = []
    rows = []
    for _ in range(order_count):
        order_name = generate_order_name()
        account_id, currency = random.choice(account_choices)
        row = {
            "order_id": generate_order_id(),
            "order_name": order_name,
            "order_display_name": order_name,
            "order_description": generate_order_description(),
            "order_invoice_note": generate_order_invoice_note(order_name),
            "order_currency": currency or default_currency,
            "order_account_id": account_id,
        }
        for attr in custom_attributes:
            row[attr["column_name"]] = _random_value_for_attr(attr)
        rows.append(row)
    return rows


def generate_order_csv(order_count, account_rows=None, account_ids=None, default_currency="AUD", custom_attributes=None):
    """Generate an order CSV file and return its filepath."""
    rows = generate_order_rows(
        order_count,
        account_rows=account_rows,
        account_ids=account_ids,
        default_currency=default_currency,
        custom_attributes=custom_attributes,
    )
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
    use_defaults = input("Use default order custom attributes? (y/N, default n): ").strip().lower()
    order_attrs = get_default_order_custom_attributes() if use_defaults in ("y", "yes") else []
    generate_order_csv(order_count, account_ids=account_ids, custom_attributes=order_attrs)
