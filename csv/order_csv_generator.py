import argparse
import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("en_AU")
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "order_generator_config.json"
DEFAULT_ORDER_COUNT = 200


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
DEFAULT_ORDER_RADIO_OPTIONS = DEFAULT_ORDER_ATTR_OPTIONS[:]
LINE_ITEM_ACCOUNTING_CODES = [
    "Account Receivable",
    "Cash and Cash Equivalent",
    "Inventory",
    "Sales Revenue",
    "Event Charge",
    "Deduction",
    "Alteration",
    "Cancellation",
    "Chargeback",
]


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
        today = datetime.now()
        offset_days = random.randint(-365, 365)
        random_date = today + timedelta(days=offset_days)
        return random_date.strftime("%Y-%m-%d")
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
        "system_identifiers": [],
        "min_items_per_order": 1,
        "max_items_per_order": 5,
    }


def _fallback_system_identifiers(count=5):
    return [f"ITEM-{random.randint(1000, 9999)}" for _ in range(count)]


def _generate_placeholder_account_ids(count=10):
    """Create placeholder account IDs when none provided."""
    ids = []
    for _ in range(count):
        ids.append(f"CSV-ACC-{random.randint(10000, 99999)}-CUS")
    return ids


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

    system_identifiers = item_config.get("system_identifiers") or []
    if include_system and not system_identifiers:
        system_identifiers = _fallback_system_identifiers()
    discount_probability = float(item_config.get("line_item_discount_probability", 0.12))
    discount_probability = max(0.0, min(1.0, discount_probability))

    rows = []
    for idx in range(order_count):
        order_name = generate_order_name()
        account_id, currency = random.choice(account_choices)
        row = {
            "order_id": generate_order_id(),
            "order_name": order_name,
            "order_display_name": order_name,
            "order_description": generate_order_description(),
            "order_origin": f"CSV IMPORT - {idx + 1}",
            "order_billing_start_date": "",
            "order_order_start_date": "",
            "order_consolidate_invoice": "",
            "order_consolidate_key": "",
            "order_communication_preference": "",
            "order_payment_mode": "",
            "order_payment_term_alignment": "",
            "order_payment_term": "",
            "order_allow_installment": "",
            "order_installment_type": "",
            "order_installment_count": "",
            "order_installment_amount": "",
            "order_installment_period": "",
            "order_invoice_note": generate_order_invoice_note(order_name),
            "order_currency": currency or default_currency,
            "order_account_id": account_id,
            "line_item_uuid": "",
            "line_item_id": "",
            "line_item_accounting_code": "",
        }

        billing_choices = [
            "RATING_START_DATE",
            "SUBSCRIPTION_START_DATE",
            "SUBSCRIPTION_ACTIVATION_DATE",
            "SUBSCRIPTION_ACCEPTANCE_DATE",
        ]
        if random.random() < 0.8:
            billing_choice = random.choice(billing_choices)
            row["order_billing_start_date"] = billing_choice
            if billing_choice == "SUBSCRIPTION_START_DATE":
                future_days = random.randint(0, 90)
                start_date = datetime.now() + timedelta(days=future_days)
                date_value = start_date.strftime("%Y-%m-%d")
                row["order_order_start_date"] = date_value

        comm_channels = ['EMAIL', 'POSTAL_EMAIL', 'TEXT_MESSAGE', 'VOICE_MAIL']
        comm_count = random.randint(1, len(comm_channels))
        row["order_communication_preference"] = ",".join(random.sample(comm_channels, k=comm_count))

        row["order_payment_mode"] = random.choice(["MANUAL", "AUTOMATIC"])
        row["order_payment_term_alignment"] = random.choice(["BILLING_DATE", "INVOICE_DATE"])
        row["order_payment_term"] = row["order_payment_term_alignment"]

        allow_installment = random.random() < 0.3

        if not allow_installment and random.random() < 0.4:
            row["order_consolidate_invoice"] = "TRUE"
            if random.random() < 0.8:
                row["order_consolidate_key"] = f"ORDER-CONS-{random.randint(1000, 9999)}"

        if allow_installment:
            row["order_allow_installment"] = "TRUE"
            row["order_installment_type"] = random.choice(["FIXED_TERM", "FIXED_EMI"])
            installment_period_choices = ['1 Day', '1 Week']
            installment_period_choices += [f"{m} Month" for m in range(1, 13)]
            installment_period_choices += [f"{y} Year" for y in range(1, 11)]
            row["order_installment_period"] = random.choice(installment_period_choices)
            if row["order_installment_type"] == "FIXED_TERM":
                row["order_installment_count"] = str(random.randint(2, 100))
            else:
                row["order_installment_amount"] = str(round(random.uniform(10, 500), 2))
        else:
            row["order_allow_installment"] = ""

        min_items = max(1, int(item_config.get("min_items_per_order", 1)))
        max_items = max(min_items, int(item_config.get("max_items_per_order", min_items)))
        total_items = random.randint(min_items, max_items)

        for item_idx in range(total_items):
            item_row = row.copy()
            item_row["line_item_uuid"] = ""
            item_row["line_item_id"] = ""
            item_row["line_item_accounting_code"] = ""
            is_system_item = False
            if include_system and include_line_items:
                is_system_item = random.random() < 0.5
            elif include_system:
                is_system_item = True
            else:
                is_system_item = False

            if is_system_item:
                identifier = random.choice(system_identifiers)
                item_row["line_item_uuid"] = identifier
                item_row["line_item_id"] = identifier
            elif include_line_items:
                item_row["line_item_name"] = generate_line_item_name()
                item_row["line_item_order_quantity"] = generate_line_item_quantity()
                item_row["line_item_invoice_note"] = generate_line_item_invoice_note()
                item_row["line_item_description"] = generate_line_item_description()
                item_row["line_item_price_snapshot_price"] = generate_line_item_price()
                item_row["line_item_accounting_code"] = random.choice(LINE_ITEM_ACCOUNTING_CODES)

                if random.random() < discount_probability:
                    discount_type = random.choice(["FIXED", "PERCENTAGE"])
                    if discount_type == "FIXED":
                        discount_value = round(random.uniform(5, 250), 2)
                    else:
                        discount_value = random.randint(1, 100)
                    item_row["line_item_discount_type"] = discount_type
                    item_row["line_item_discount"] = discount_value
                else:
                    item_row["line_item_discount_type"] = ""
                    item_row["line_item_discount"] = ""

                if random.random() < 0.1:
                    item_row["line_item_tax_exempt"] = "TRUE"
                else:
                    item_row["line_item_tax_exempt"] = ""

                for attr in line_item_custom_attributes:
                    item_row[attr["column_name"]] = _random_value_for_attr(attr)

            for attr in custom_attributes:
                item_row[attr["column_name"]] = _random_value_for_attr(attr)

            if item_idx > 0:
                for key in list(item_row.keys()):
                    if key in ("order_id", "order_account_id"):
                        continue
                    if key.startswith("line_item_"):
                        continue
                    item_row[key] = ""

            rows.append(item_row)
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

    print(f"\nSuccessfully generated {order_count} orders!")
    print(f"File saved to: {filepath}")
    if rows:
        print("\nSample data:")
        print(f"  First Order ID: {rows[0]['order_id']}")
        print(f"  First Account ID: {rows[0]['order_account_id']}")
    unique_ids = len({row['order_id'] for row in rows}) == len(rows)
    print(f"  All order IDs unique: {unique_ids}")
    return filepath


def prompt_order_account_ids():
    """Prompt the user for account IDs to attach to orders."""
    while True:
        raw = input("Enter account IDs (comma-separated): ").strip()
        account_ids = [value.strip() for value in raw.split(",") if value.strip()]
        if account_ids:
            return account_ids
        print("Please enter at least one account ID.")


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
        "system_identifier_type": "code",
        "system_identifiers": [],
    }

    if include_system:
        while True:
            raw_ids = input("Enter system item codes (comma-separated, e.g., ITEM1,ITEM2): ").strip()
            identifiers = [value.strip() for value in raw_ids.split(",") if value.strip()]
            if identifiers:
                config["system_identifiers"] = identifiers
                break
            print("Please enter at least one system item code.")

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
    try:
        parser = argparse.ArgumentParser(description="Generate order CSV data.")
        parser.add_argument(
            "count",
            type=int,
            nargs="?",
            default=DEFAULT_ORDER_COUNT,
            help=f"Number of orders to generate (default: {DEFAULT_ORDER_COUNT})",
        )
        parser.add_argument(
            "--batch",
            action="store_true",
            help="Generate multiple files: 200, 300, 400, and 500 orders",
        )
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

        if args.batch:
            print("=== BATCH MODE: Generating multiple files ===\n")
            counts = [200, 300, 400, 500]
            files = []
            for count in counts:
                print(f"\n{'=' * 60}")
                filepath = generate_order_csv(
                    count,
                    account_ids=_generate_placeholder_account_ids(),
                    custom_attributes=[],
                    item_config=default_item_config(),
                    line_item_custom_attributes=[],
                )
                files.append(filepath)
                print(f"{'=' * 60}\n")
            print("\n=== BATCH GENERATION COMPLETE ===")
            print(f"Generated {len(files)} files:")
            for f in files:
                print(f"  - {f}")
            raise SystemExit(0)

        order_count = max(1, args.count)

        if args.load_config:
            try:
                cfg = load_generation_config(args.load_config)
            except OSError as exc:
                print(f"ERROR: Could not load config from {args.load_config}: {exc}")
                raise SystemExit(1)

            if args.count == DEFAULT_ORDER_COUNT:
                order_count = int(cfg.get("order_count", order_count))
            account_ids = cfg.get("account_ids") or _generate_placeholder_account_ids()
            order_attrs = cfg.get("order_custom_attributes") or []
            item_config = cfg.get("item_config") or default_item_config()
            line_item_custom_attrs = cfg.get("line_item_custom_attributes") or []
        else:
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
    except KeyboardInterrupt:
        print("\nOrder generation cancelled by user.")
