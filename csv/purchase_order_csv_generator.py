import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("en_AU")
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "purchase_order_generator_config.json"
DEFAULT_PURCHASE_ORDER_COUNT = 200


def generate_purchase_order_id():
    """Generate unique purchase order ID."""
    return f"CSV-PO-{random.randint(100000, 999999)}"


def generate_purchase_order_note():
    """Generate purchase order note text."""
    notes = [
        "Expedited delivery required",
        "Standard procurement terms apply",
        "Bulk purchase for Q1 inventory",
        "Urgent restock order",
        "Annual vendor contract renewal",
        "Special pricing negotiated",
        "Volume discount applied",
    ]
    return random.choice(notes)


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


def generate_purchase_line_item_id():
    return f"PO-LINE-{random.randint(100000, 999999)}"


def generate_purchase_line_item_name():
    adjectives = ["Premium", "Standard", "Bulk", "Industrial", "Commercial", "Quality", "Economy"]
    nouns = ["Material", "Component", "Supply", "Part", "Equipment", "Tool", "Resource"]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"


def generate_purchase_line_note():
    notes = [
        "Inspect upon delivery",
        "Store in cool, dry place",
        "Handle with care",
        "Quality check required",
        "Direct to warehouse",
        "Requires vendor certification",
    ]
    return random.choice(notes)


def generate_purchase_line_item_price():
    return round(random.uniform(10, 5000), 2)


def generate_purchase_line_item_quantity():
    return random.randint(1, 100)


PURCHASE_LINE_ITEM_ACCOUNTING_CODES = [
    "Account Payable",
    "Inventory",
    "Cost of Goods Sold",
    "Purchase Returns",
    "Raw Materials",
    "Operating Supplies",
    "Equipment Purchase",
    "Freight In",
]

TAX_CODES = ["GST", "VAT", "PST", "HST", "QST", "EXEMPT"]

UOM_CHOICES = ["EA", "BX", "CS", "PK", "KG", "LB", "L", "GAL", "M", "FT"]


def get_default_purchase_order_custom_attributes(prefix="ca_purchase_order_attr_"):
    """Default set of 10 purchase order custom attributes."""
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

    default_options = ["A", "B", "C", "D"]
    return [
        make_attr("CA_BOOL", "bool"),
        make_attr("CA_CHECKBOX", "checkboxes", options=default_options),
        make_attr("CA_DATE", "date"),
        make_attr("CA_DROPDOWN", "dropdown", options=default_options),
        make_attr("CA_DROPDOWN_WITH_MULTISELECT", "dropdown_multi", options=default_options),
        make_attr("CA_MONEY", "money"),
        make_attr("CA_QUANTITY", "quantity", quantity_min=1, quantity_max=50),
        make_attr("CA_NUMBER", "number"),
        make_attr("CA_RADIO", "radio", options=default_options),
        make_attr("CA_TEXT", "text"),
    ]


def get_default_purchase_line_item_custom_attributes():
    return get_default_purchase_order_custom_attributes(prefix="ca_purchase_order_item_attr_")


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
        "min_items_per_purchase_order": 1,
        "max_items_per_purchase_order": 5,
    }


def _fallback_system_identifiers(count=5):
    return [f"ITEM-{random.randint(1000, 9999)}" for _ in range(count)]


def _generate_placeholder_account_ids(count=10):
    """Create placeholder account IDs when none provided."""
    ids = []
    for _ in range(count):
        ids.append(f"CSV-ACC-{random.randint(10000, 99999)}-VND")
    return ids


def generate_purchase_order_rows(
    purchase_order_count,
    account_rows=None,
    account_ids=None,
    default_currency="AUD",
    warehouse_config=None,
    custom_attributes=None,
    item_config=None,
    line_item_custom_attributes=None,
):
    """
    Create purchase order rows using either generated account data or user-supplied account IDs.
    """
    account_choices = _derive_account_choices(account_rows, account_ids, default_currency=default_currency)
    if not account_choices:
        raise ValueError("No account IDs available to associate with purchase orders.")

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

    # Warehouse configuration
    if warehouse_config is None:
        warehouse_config = {"use_warehouse": False, "warehouses": []}
    use_warehouse = warehouse_config.get("use_warehouse", False)
    warehouses = warehouse_config.get("warehouses", [])

    rows = []
    for idx in range(purchase_order_count):
        account_id, currency = random.choice(account_choices)

        # Generate issue and due dates
        issue_date = datetime.now() + timedelta(days=random.randint(-30, 30))
        due_date = issue_date + timedelta(days=random.randint(15, 90))
        expected_completion_date = issue_date + timedelta(days=random.randint(0, 60))

        row = {
            "purchase_order_id": generate_purchase_order_id(),
            "purchase_order_origin": f"CSV IMPORT - {idx + 1}",
            "purchase_order_currency": currency or default_currency,
            "purchase_order_issue_date": issue_date.strftime("%Y-%m-%d"),
            "purchase_order_due_date": due_date.strftime("%Y-%m-%d"),
            "purchase_order_expected_completion_date": expected_completion_date.strftime("%Y-%m-%d"),
            "purchase_order_price_tax_inclusive": random.choice(["TRUE", "FALSE"]),
            "purchase_order_purchase_order_note": generate_purchase_order_note(),
            "purchase_order_account_id": account_id,
            "purchase_order_custom_form_template": "",
            "purchase_line_item_id": "",
            "purchase_line_item_name": "",
            "purchase_line_item_quantity": "",
            "purchase_line_item_price": "",
            "purchase_line_item_discount": "",
            "purchase_line_purchase_price_is_tax_inclusive": "",
            "purchase_line_item_purchase_tax_code": "",
            "purchase_line_item_purchase_tax_rate": "",
            "purchase_line_item_price_tax_exempt": "",
            "purchase_line_item_accounting_code": "",
            "purchase_line_purchase_line_note": "",
            "purchase_line_base_uom": "",
            "purchase_line_purchase_uom": "",
            "purchase_line_tax_inclusive_based_on": "",
            "purchase_line_discount_type": "",
            "purchase_line_rate_option": "",
            "purchase_line_charge_type": "",
            "purchase_line_item_warehouse_id": "",
        }

        min_items = max(1, int(item_config.get("min_items_per_purchase_order", 1)))
        max_items = max(min_items, int(item_config.get("max_items_per_purchase_order", min_items)))
        total_items = random.randint(min_items, max_items)

        for item_idx in range(total_items):
            item_row = row.copy()
            item_row["purchase_line_item_id"] = ""
            item_row["purchase_line_item_name"] = ""
            item_row["purchase_line_item_accounting_code"] = ""

            is_system_item = False
            if include_system and include_line_items:
                is_system_item = random.random() < 0.5
            elif include_system:
                is_system_item = True
            else:
                is_system_item = False

            if is_system_item:
                identifier = random.choice(system_identifiers)
                item_row["purchase_line_item_id"] = identifier
            elif include_line_items:
                item_row["purchase_line_item_name"] = generate_purchase_line_item_name()
                item_row["purchase_line_item_quantity"] = generate_purchase_line_item_quantity()
                item_row["purchase_line_item_price"] = generate_purchase_line_item_price()
                item_row["purchase_line_item_accounting_code"] = random.choice(PURCHASE_LINE_ITEM_ACCOUNTING_CODES)
                item_row["purchase_line_purchase_line_note"] = generate_purchase_line_note()

                # Discount
                if random.random() < discount_probability:
                    discount_value = round(random.uniform(5, 250), 2)
                    item_row["purchase_line_item_discount"] = discount_value
                else:
                    item_row["purchase_line_item_discount"] = ""

                # Tax settings
                item_row["purchase_line_purchase_price_is_tax_inclusive"] = random.choice(["TRUE", "FALSE"])
                item_row["purchase_line_item_purchase_tax_code"] = random.choice(TAX_CODES)
                item_row["purchase_line_item_purchase_tax_rate"] = round(random.uniform(5, 20), 2)

                if random.random() < 0.1:
                    item_row["purchase_line_item_price_tax_exempt"] = "TRUE"
                else:
                    item_row["purchase_line_item_price_tax_exempt"] = ""

                # UOM
                base_uom = random.choice(UOM_CHOICES)
                item_row["purchase_line_base_uom"] = base_uom
                item_row["purchase_line_purchase_uom"] = random.choice([base_uom] + UOM_CHOICES)

                # Tax inclusive based on
                item_row["purchase_line_tax_inclusive_based_on"] = random.choice(["PRICE", "TOTAL", ""])

                # Discount type
                item_row["purchase_line_discount_type"] = "FIXED"

                # Rate option
                item_row["purchase_line_rate_option"] = "FIXED"

                # Charge type
                item_row["purchase_line_charge_type"] = "FIXED"

                # Warehouse
                if use_warehouse and warehouses:
                    item_row["purchase_line_item_warehouse_id"] = random.choice(warehouses)
                else:
                    item_row["purchase_line_item_warehouse_id"] = ""

                # Line item custom attributes
                for attr in line_item_custom_attributes:
                    item_row[attr["column_name"]] = _random_value_for_attr(attr)

            # Purchase order level custom attributes
            for attr in custom_attributes:
                item_row[attr["column_name"]] = _random_value_for_attr(attr)

            # Clear purchase order fields for subsequent items
            if item_idx > 0:
                for key in list(item_row.keys()):
                    # Keep mandatory fields in all rows
                    if key in ("purchase_order_id", "purchase_order_account_id",
                              "purchase_order_currency", "purchase_order_issue_date",
                              "purchase_order_due_date", "purchase_order_expected_completion_date"):
                        continue
                    if key.startswith("purchase_line_"):
                        continue
                    if key.startswith("ca_purchase_order_item_attr_"):
                        continue
                    item_row[key] = ""

            rows.append(item_row)
    return rows


def generate_purchase_order_csv(
    purchase_order_count,
    account_rows=None,
    account_ids=None,
    default_currency="AUD",
    warehouse_config=None,
    custom_attributes=None,
    item_config=None,
    line_item_custom_attributes=None,
):
    """Generate a purchase order CSV file and return its filepath."""
    rows = generate_purchase_order_rows(
        purchase_order_count,
        account_rows=account_rows,
        account_ids=account_ids,
        default_currency=default_currency,
        warehouse_config=warehouse_config,
        custom_attributes=custom_attributes,
        item_config=item_config,
        line_item_custom_attributes=line_item_custom_attributes,
    )
    df = pd.DataFrame(rows).fillna("")

    # Prefix date columns with tab character to prevent Excel auto-conversion
    date_columns = ['purchase_order_issue_date', 'purchase_order_due_date', 'purchase_order_expected_completion_date']

    # Add custom attribute date columns
    if custom_attributes:
        for attr in custom_attributes:
            if attr.get('type') == 'date':
                date_columns.append(attr['column_name'])
    if line_item_custom_attributes:
        for attr in line_item_custom_attributes:
            if attr.get('type') == 'date':
                date_columns.append(attr['column_name'])

    # Prefix dates with tab character for Excel
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"\t{x}" if x and x != "" else x)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"PURCHASE_ORDER_DUMMY_DATA_{purchase_order_count}_{timestamp}.csv"
    filepath = f"C:\\Users\\Rahman\\Downloads\\{filename}"
    df.to_csv(filepath, index=False, quoting=1)  # QUOTE_MINIMAL

    print(f"\nSuccessfully generated {purchase_order_count} purchase orders!")
    print(f"File saved to: {filepath}")
    if rows:
        print("\nSample data:")
        print(f"  First Purchase Order ID: {rows[0]['purchase_order_id']}")
        print(f"  First Account ID: {rows[0]['purchase_order_account_id']}")
    unique_ids = len({row['purchase_order_id'] for row in rows}) == len(rows)
    print(f"  All purchase order IDs unique: {unique_ids}")
    return filepath


def prompt_purchase_order_account_ids():
    """Prompt the user for account IDs to attach to purchase orders."""
    while True:
        raw = input("Enter vendor account IDs (comma-separated): ").strip()
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


def prompt_purchase_order_item_config():
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

    # Max items per purchase order (min is always 1)
    while True:
        max_raw = input("Maximum items per purchase order (default 5): ").strip()
        if max_raw == "":
            max_items = 5
            break
        try:
            max_items = int(max_raw)
            if max_items >= 1:
                break
            print("Please enter a number >= 1.")
        except ValueError:
            print("Please enter a valid number.")

    config["min_items_per_purchase_order"] = 1
    config["max_items_per_purchase_order"] = max_items

    return config


def prompt_warehouse_config():
    """
    Prompt user for warehouse configuration.

    Returns dict with:
        use_warehouse: bool
        warehouses: list[str]
    """
    use_warehouse = input("Do you want warehouse column? (y/N, default n): ").strip().lower()
    if use_warehouse not in ("y", "yes"):
        return {"use_warehouse": False, "warehouses": []}

    use_default = input("Do you want to use default warehouses? (Y/n, default y): ").strip().lower()
    if use_default in ("", "y", "yes"):
        warehouses = ["W-1", "W-2", "W-3"]
    else:
        while True:
            raw = input("Enter warehouse names (comma-separated, e.g., W-1,W-2,W-3): ").strip()
            warehouses = [w.strip() for w in raw.split(",") if w.strip()]
            if warehouses:
                break
            print("Please enter at least one warehouse name.")

    return {"use_warehouse": True, "warehouses": warehouses}


def prompt_purchase_order_custom_attributes():
    """
    Prompt user for purchase order-level custom attributes (default: none).
    """
    use_attrs = input("Do you want purchase order custom attributes? (y/N, default n): ").strip().lower()
    if use_attrs not in ("y", "yes"):
        return []

    while True:
        raw = input("How many purchase order custom attributes? (>=1, default 10): ").strip()
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
        default_choice = input("Use default 10 purchase order custom attributes? (y/N, default n): ").strip().lower()
        if default_choice in ("y", "yes"):
            return get_default_purchase_order_custom_attributes()

    return collect_custom_attrs("ca_purchase_order_attr_", count)


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


def prompt_purchase_line_item_custom_attributes():
    """
    Prompt user for custom attributes on purchase line items.
    """
    use_attrs = input("Do you want purchase line item custom attributes? (y/N, default n): ").strip().lower()
    if use_attrs not in ("y", "yes"):
        return []

    while True:
        raw = input("How many purchase line item custom attributes? (>=1, default 10): ").strip()
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
        default_choice = input("Use default 10 purchase line item custom attributes? (y/N, default n): ").strip().lower()
        if default_choice in ("y", "yes"):
            return get_default_purchase_line_item_custom_attributes()

    return collect_custom_attrs("ca_purchase_order_item_attr_", count)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Generate purchase order CSV data.")
        parser.add_argument(
            "count",
            type=int,
            nargs="?",
            default=DEFAULT_PURCHASE_ORDER_COUNT,
            help=f"Number of purchase orders to generate (default: {DEFAULT_PURCHASE_ORDER_COUNT})",
        )
        parser.add_argument(
            "--batch",
            action="store_true",
            help="Generate multiple files: 200, 300, 400, and 500 purchase orders",
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
                filepath = generate_purchase_order_csv(
                    count,
                    account_ids=_generate_placeholder_account_ids(),
                    warehouse_config={"use_warehouse": False, "warehouses": []},
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

        purchase_order_count = max(1, args.count)

        if args.load_config:
            try:
                cfg = load_generation_config(args.load_config)
            except OSError as exc:
                print(f"ERROR: Could not load config from {args.load_config}: {exc}")
                raise SystemExit(1)

            if args.count == DEFAULT_PURCHASE_ORDER_COUNT:
                purchase_order_count = int(cfg.get("purchase_order_count", purchase_order_count))
            account_ids = cfg.get("account_ids") or _generate_placeholder_account_ids()
            warehouse_cfg = cfg.get("warehouse_config") or {"use_warehouse": False, "warehouses": []}
            purchase_order_attrs = cfg.get("purchase_order_custom_attributes") or []
            item_config = cfg.get("item_config") or default_item_config()
            line_item_custom_attrs = cfg.get("line_item_custom_attributes") or []
        else:
            account_ids = prompt_purchase_order_account_ids()
            warehouse_cfg = prompt_warehouse_config()
            purchase_order_attrs = prompt_purchase_order_custom_attributes()
            item_config = prompt_purchase_order_item_config()
            line_item_custom_attrs = prompt_purchase_line_item_custom_attributes()

            if args.save_config:
                config = {
                    "purchase_order_count": purchase_order_count,
                    "account_ids": account_ids,
                    "warehouse_config": warehouse_cfg,
                    "purchase_order_custom_attributes": purchase_order_attrs,
                    "item_config": item_config,
                    "line_item_custom_attributes": line_item_custom_attrs,
                }
                save_generation_config(args.save_config, config)

        generate_purchase_order_csv(
            purchase_order_count,
            account_ids=account_ids,
            warehouse_config=warehouse_cfg,
            custom_attributes=purchase_order_attrs,
            item_config=item_config,
            line_item_custom_attributes=line_item_custom_attrs,
        )
    except KeyboardInterrupt:
        print("\nPurchase order generation cancelled by user.")
