import argparse
import argparse
import json
import random
from datetime import datetime
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("en_AU")
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "order_generator_config.json"


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


def generate_line_item_uuid():
    return f"LI-{random.randint(100000, 999999)}"


def generate_line_item_id():
    return f"LINE-{random.randint(100000, 999999)}"


def generate_line_item_name():
    adjectives = ["Premium", "Deluxe", "Standard", "Basic", "Ultimate", "Eco", "Smart"]
    nouns = ["Subscription", "Package", "Bundle", "Service", "Addon", "Module", "Plan"]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"


def generate_line_item_description():
    return fake.sentence(nb_words=10)


def generate_line_item_invoice_note():
    notes = [
        "Includes onboarding and provisioning.",
        "Apply standard billing terms.",
        "Priority delivery requested by client.",
        "Requires monthly reconciliation.",
        "Coordinate with fulfillment team.",
    ]
    return random.choice(notes)


def generate_line_item_price():
    return round(random.uniform(10, 5000), 2)


def generate_line_item_quantity():
    return random.randint(1, 50)


DEFAULT_ORDER_ATTR_OPTIONS = ["A", "B", "C", "D"]
DEFAULT_ORDER_RADIO_OPTIONS = [str(i) for i in range(1, 51)]


def get_default_order_custom_attributes(prefix="ca_order_attr_"):
    """Default set of 10 order custom attributes."""
    def make_attr(name, attr_type, options=None, quantity_min=None, quantity_max=None):
        return {
            "column_name": f"{prefix}{name}",
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


def get_default_line_item_custom_attributes():
    return get_default_order_custom_attributes(prefix="ca_order_line_item_attr_")


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
    if attr_type == "string":
        return fake.word()
    if attr_type == "radio":
        return random.choice(options) if options else ""
    if attr_type == "text":
        return fake.sentence(nb_words=6)
    return ""


def default_item_config():
    return {
        "include_system_items": True,
        "include_line_items": True,
        "system_identifier_type": "uuid",
        "system_identifiers": [],
    }


def _fallback_system_identifiers(identifier_type, count=5):
    identifiers = []
    for _ in range(count):
        if identifier_type == "code":
            identifiers.append(f"SYS-CODE-{random.randint(1000, 9999)}")
        else:
            identifiers.append(f"00000000-0000-0000-0000-{random.randint(100000000000, 999999999999)}")
    return identifiers


def generate_order_rows(
    order_count,
    account_rows=None,
    account_ids=None,
    default_currency="AUD",
    custom_attributes=None,
    item_config=None,
    line_item_custom_attributes=None,
):
    """
    Create order rows using either generated account data or user-supplied account IDs.
    """
    account_choices = _derive_account_choices(account_rows, account_ids, default_currency=default_currency)
    if not account_choices:
        raise ValueError("No account IDs available to associate with orders.")

    if custom_attributes is None:
        custom_attributes = []
    if line_item_custom_attributes is None:
        line_item_custom_attributes = []
    if item_config is None:
        item_config = default_item_config()

    include_system = bool(item_config.get("include_system_items", True))
    include_line_items = bool(item_config.get("include_line_items", True))
    if not include_system and not include_line_items:
        include_line_items = True

    system_identifier_type = item_config.get("system_identifier_type", "uuid").lower()
    if system_identifier_type not in ("uuid", "code"):
        system_identifier_type = "uuid"
    system_identifiers = item_config.get("system_identifiers") or []
    if include_system and not system_identifiers:
        system_identifiers = _fallback_system_identifiers(system_identifier_type)
    discount_probability = float(item_config.get("line_item_discount_probability", 0.12))
    discount_probability = max(0.0, min(1.0, discount_probability))

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

        if include_system:
            identifier = random.choice(system_identifiers)
            if system_identifier_type == "code":
                row["system_item_code"] = identifier
                row["system_item_uuid"] = ""
            else:
                row["system_item_uuid"] = identifier
                row["system_item_code"] = ""

        if include_line_items:
            row["line_item_uuid"] = generate_line_item_uuid()
            row["line_item_id"] = generate_line_item_id()
            row["line_item_name"] = generate_line_item_name()
            row["line_item_order_quantity"] = generate_line_item_quantity()
            row["line_item_invoice_note"] = generate_line_item_invoice_note()
            row["line_item_description"] = generate_line_item_description()
            row["line_item_price_snapshot_price"] = generate_line_item_price()

            if random.random() < discount_probability:
                discount_type = random.choice(["FIXED", "PERCENTAGE"])
                if discount_type == "FIXED":
                    discount_value = round(random.uniform(5, 250), 2)
                else:
                    discount_value = random.randint(1, 100)
                row["line_item_discount_type"] = discount_type
                row["line_item_discount"] = discount_value
            else:
                row["line_item_discount_type"] = ""
                row["line_item_discount"] = ""

            tax_choices = ["TRUE", "FALSE", ""]
            row["line_item_tax_exempt"] = random.choice(tax_choices)

            for attr in line_item_custom_attributes:
                row[attr["column_name"]] = _random_value_for_attr(attr)

        for attr in custom_attributes:
            row[attr["column_name"]] = _random_value_for_attr(attr)
        rows.append(row)
    return rows


def generate_order_csv(
    order_count,
    account_rows=None,
    account_ids=None,
    default_currency="AUD",
    custom_attributes=None,
    item_config=None,
    line_item_custom_attributes=None,
):
    """Generate an order CSV file and return its filepath."""
    rows = generate_order_rows(
        order_count,
        account_rows=account_rows,
        account_ids=account_ids,
        default_currency=default_currency,
        custom_attributes=custom_attributes,
        item_config=item_config,
        line_item_custom_attributes=line_item_custom_attributes,
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


def save_generation_config(path, config):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2)
        print(f"Configuration saved to {path}")
    except OSError as exc:
        print(f"WARNING: Could not save configuration to {path}: {exc}")


def load_generation_config(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def prompt_order_item_config():
    """
    Prompt for system vs line item generation settings.
    """
    print(
        "Which items should be generated?\n"
        "  1) System items only\n"
        "  2) Line items only\n"
        "  3) Both (default)\n"
    )
    include_system = True
    include_line = True
    while True:
        choice = input("Enter choice (1-3, default 3): ").strip()
        if choice in ("", "3"):
            include_system = True
            include_line = True
            break
        if choice == "1":
            include_system = True
            include_line = False
            break
        if choice == "2":
            include_system = False
            include_line = True
            break
        print("Please enter 1, 2, or 3.")

    config = {
        "include_system_items": include_system,
        "include_line_items": include_line,
        "system_identifier_type": "uuid",
        "system_identifiers": [],
    }

    if include_system:
        while True:
            raw_type = input("Are your system item identifiers UUIDs or codes? (uuid/code, default uuid): ").strip().lower()
            if raw_type in ("", "uuid", "code"):
                identifier_type = raw_type if raw_type in ("uuid", "code") else "uuid"
                break
            print("Please enter 'uuid' or 'code'.")

        while True:
            raw_ids = input("Enter system item identifiers (comma-separated, e.g., ID1,ID2): ").strip()
            identifiers = [value.strip() for value in raw_ids.split(",") if value.strip()]
            if identifiers:
                config["system_identifiers"] = identifiers
                break
            print("Please enter at least one identifier.")

        config["system_identifier_type"] = identifier_type

    return config


def prompt_order_custom_attributes():
    """
    Prompt user for order-level custom attributes (default: none).
    """
    use_attrs = input("Do you want order custom attributes? (y/N, default n): ").strip().lower()
    if use_attrs not in ("y", "yes"):
        return []

    while True:
        raw = input("How many order custom attributes? (>=1, default 10): ").strip()
        if raw == "":
            count = 10
            break
        try:
            count = int(raw)
        except ValueError:
            print("Please enter a whole number 1 or greater.")
            continue
        if count >= 1:
            break
        print("Please enter a whole number 1 or greater.")

    if count == 10:
        default_choice = input("Use default 10 order custom attributes? (y/N, default n): ").strip().lower()
        if default_choice in ("y", "yes"):
            return get_default_order_custom_attributes()

    return collect_custom_attrs("ca_order_attr_", count)


def collect_custom_attrs(prefix, count):
    attrs = []
    for idx in range(1, count + 1):
        print(f"\nCustom attribute {idx}/{count}")
        while True:
            name = input("  Enter attribute name (e.g., ATTR_NAME, or 'skip' to skip): ").strip()
            if name.lower() == "skip":
                print("  Skipping this attribute.")
                name = ""
                break
            if name:
                break
            print("  Name cannot be empty.")
        if not name:
            continue
        normalized = name.replace(" ", "_").upper()
        column_name = f"{prefix}{normalized}"

        type_menu = (
            "  Select type:\n"
            "    1) Boolean\n"
            "    2) Number\n"
            "    3) String\n"
            "    4) Text\n"
            "    5) Date\n"
            "    6) Money\n"
            "    7) Quantity\n"
            "    8) Dropdown\n"
            "    9) Dropdown (MultiSelect)\n"
            "   10) Checkboxes\n"
            "   11) Radio\n"
        )
        print(type_menu, end="")
        type_map = {
            "1": "bool",
            "2": "number",
            "3": "string",
            "4": "text",
            "5": "date",
            "6": "money",
            "7": "quantity",
            "bool": "bool",
            "boolean": "bool",
            "number": "number",
            "string": "string",
            "text": "text",
            "date": "date",
            "money": "money",
            "quantity": "quantity",
            "8": "dropdown",
            "dropdown": "dropdown",
            "9": "dropdown_multi",
            "multiselect": "dropdown_multi",
            "dropdown_multiselect": "dropdown_multi",
            "10": "checkboxes",
            "checkboxes": "checkboxes",
            "11": "radio",
            "radio": "radio",
        }
        valid_types = set(type_map.values())

        quantity_min = None
        quantity_max = None

        while True:
            raw_type = input("  Enter type (1-11 or name): ").strip().lower()
            attr_type = type_map.get(raw_type)
            if attr_type in valid_types:
                break
            print("  Invalid type. Please enter 1-11 or a valid type name.")

        if attr_type == "quantity":
            quantity_min = 1
            quantity_max = 50
            while True:
                range_raw = input("  Enter quantity range as min-max (default 1-50): ").strip()
                if range_raw == "":
                    break
                parts = [p.strip() for p in range_raw.replace(" ", "").split("-") if p.strip()]
                if len(parts) != 2:
                    print("  Please enter range in format min-max, e.g., 5-90.")
                    continue
                try:
                    min_val = int(parts[0])
                    max_val = int(parts[1])
                except ValueError:
                    print("  Please enter whole numbers for min and max.")
                    continue
                if min_val > max_val:
                    print("  Min cannot be greater than max.")
                    continue
                quantity_min = min_val
                quantity_max = max_val
                break

        options = []
        if attr_type in ("dropdown", "dropdown_multi", "checkboxes", "radio"):
            raw_opts = input("  Enter options (comma-separated, default A,B,C,D): ").strip()
            if not raw_opts:
                raw_opts = "A,B,C,D"
            options = [o.strip() for o in raw_opts.split(",") if o.strip()]

        attrs.append(
            {
                "column_name": column_name,
                "type": attr_type,
                "constant": False,
                "value": None,
                "options": options,
                "quantity_min": quantity_min,
                "quantity_max": quantity_max,
            }
        )
    return attrs


def prompt_line_item_custom_attributes():
    """
    Prompt user for custom attributes on line items.
    """
    use_attrs = input("Do you want line item custom attributes? (y/N, default n): ").strip().lower()
    if use_attrs not in ("y", "yes"):
        return []

    while True:
        raw = input("How many line item custom attributes? (>=1, default 10): ").strip()
        if raw == "":
            count = 10
            break
        try:
            count = int(raw)
        except ValueError:
            print("Please enter a whole number 1 or greater.")
            continue
        if count >= 1:
            break
        print("Please enter a whole number 1 or greater.")

    if count == 10:
        default_choice = input("Use default 10 line item custom attributes? (y/N, default n): ").strip().lower()
        if default_choice in ("y", "yes"):
            return get_default_line_item_custom_attributes()

    return collect_custom_attrs("ca_order_line_item_attr_", count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate order CSV data.")
    parser.add_argument("count", type=int, nargs="?", default=200, help="Number of orders to generate (default: 200)")
    parser.add_argument(
        "--save-config",
        dest="save_config",
        nargs="?",
        const=str(DEFAULT_CONFIG_PATH),
        default=None,
        help=f"Path to save interactive configuration (default if omitted: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--load-config",
        dest="load_config",
        type=str,
        default=None,
        help="Path to load configuration (skips interactive prompts)",
    )
    args = parser.parse_args()

    if args.load_config:
        try:
            cfg = load_generation_config(args.load_config)
        except OSError as exc:
            print(f"ERROR: Could not load config from {args.load_config}: {exc}")
            raise SystemExit(1)

        order_count = int(cfg.get("order_count", args.count))
        account_ids = cfg.get("account_ids", [])
        if not account_ids:
            account_ids = prompt_order_account_ids()
        order_attrs = cfg.get("order_custom_attributes")
        if order_attrs is None:
            order_attrs = []
        item_config = cfg.get("item_config") or default_item_config()
        line_item_custom_attrs = cfg.get("line_item_custom_attributes") or []
    else:
        print("Standalone order CSV generation:")
        order_count = max(1, args.count)
        account_ids = prompt_order_account_ids()
        order_attrs = prompt_order_custom_attributes()
        item_config = prompt_order_item_config()
        line_item_custom_attrs = prompt_line_item_custom_attributes()

        if args.save_config:
            config = {
                "order_count": order_count,
                "account_ids": account_ids,
                "order_custom_attributes": order_attrs,
                "item_config": item_config,
                "line_item_custom_attributes": line_item_custom_attrs,
            }
            save_generation_config(args.save_config, config)

    generate_order_csv(
        order_count,
        account_ids=account_ids,
        custom_attributes=order_attrs,
        item_config=item_config,
        line_item_custom_attributes=line_item_custom_attrs,
    )
