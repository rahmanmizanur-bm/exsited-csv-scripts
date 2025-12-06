import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("en_AU")
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "purchase_invoice_generator_config.json"
DEFAULT_PURCHASE_INVOICE_COUNT = 200


def generate_purchase_invoice_id():
    """Generate unique purchase invoice ID."""
    return f"CSV-PINV-{random.randint(100000, 999999)}"


def generate_purchase_invoice_note():
    """Generate random purchase invoice note text."""
    notes = [
        "Payment due upon receipt. Thank you for your service.",
        "Please submit invoice as per payment terms.",
        "Contact our procurement department for any queries.",
        "Net payment terms apply as specified in purchase order.",
        "Please reference purchase invoice number when submitting invoice.",
        "All amounts shown in the specified currency.",
        "Goods received and inspected - approved for payment.",
        "Thank you for your prompt service and delivery.",
        "Payment will be processed within agreed terms.",
        "Invoice approved and forwarded to accounts payable.",
    ]
    return random.choice(notes)


def generate_issue_date():
    """Generate purchase invoice issue date within past 90 days or current/future."""
    today = datetime.now()
    # Allow current date or future dates (0 to 90 days in future)
    offset_days = random.randint(0, 90)
    issue_date = today + timedelta(days=offset_days)
    return issue_date.strftime("%Y-%m-%d")


def generate_due_date(issue_date_str):
    """Generate due date that is greater than or equal to issue date."""
    issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d")
    days_until_due = random.randint(7, 90)
    due_date = issue_date + timedelta(days=days_until_due)
    return due_date.strftime("%Y-%m-%d")


def _derive_account_choices(account_ids, default_currency="AUD"):
    """Build list of (account_id, currency) tuples for assignment."""
    choices = []
    if account_ids:
        for account_id in account_ids:
            account_id = account_id.strip()
            if account_id:
                choices.append((account_id, default_currency))
    return choices


def generate_line_item_id():
    """Generate line item ID for system items."""
    return f"ITEM-{random.randint(1000, 9999)}"


def generate_line_item_name():
    """Generate line item name for non-system items."""
    adjectives = ["Premium", "Standard", "Professional", "Enterprise", "Basic", "Advanced", "Bulk"]
    items = ["Materials", "Supplies", "Equipment", "Service", "Parts", "Components", "Resources"]
    return f"{random.choice(adjectives)} {random.choice(items)}"


def generate_line_item_quantity():
    """Generate valid quantity for line item."""
    return random.randint(1, 100)


def generate_line_item_price():
    """Generate valid price for line item."""
    return round(random.uniform(10, 5000), 2)


LINE_ITEM_ACCOUNTING_CODES = [
    "Account Payable",
    "Cash and Cash Equivalent",
    "Inventory",
    "Purchase Expense",
    "Operating Expense",
    "Cost of Goods Sold",
    "Capital Equipment",
    "Supplies Expense",
]


def get_default_purchase_invoice_custom_attributes(prefix="ca_purchase_invoice_attr_"):
    """Default set of 10 purchase invoice custom attributes."""
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


def get_default_line_item_custom_attributes():
    """Default set of 10 line item custom attributes."""
    return get_default_purchase_invoice_custom_attributes(prefix="ca_purchase_invoice_item_attr_")


def _random_value_for_attr(attr):
    """Generate random value based on attribute type."""
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
    """Default configuration for purchase invoice items."""
    return {
        "include_system_items": True,
        "include_line_items": True,
        "system_identifiers": [],
        "min_items_per_purchase_invoice": 1,
        "max_items_per_purchase_invoice": 5,
    }


def _fallback_system_identifiers(count=5):
    """Generate fallback system identifiers if none provided."""
    return [f"ITEM-{random.randint(1000, 9999)}" for _ in range(count)]


def _generate_placeholder_account_ids(count=10):
    """Create placeholder account IDs when none provided."""
    ids = []
    for _ in range(count):
        ids.append(f"CSV-ACC-{random.randint(10000, 99999)}-SUP")
    return ids


def generate_purchase_invoice_rows(
    purchase_invoice_count,
    account_ids=None,
    default_currency="AUD",
    custom_form_template="Default for Purchase Invoice",
    tax_config=None,
    custom_attributes=None,
    item_config=None,
    line_item_custom_attributes=None,
):
    """
    Create purchase invoice rows with line items.

    Args:
        purchase_invoice_count: Number of purchase invoices to generate
        account_ids: List of supplier account IDs to associate with purchase invoices
        default_currency: Default currency if not specified
        custom_form_template: Custom form template name
        tax_config: Dict with tax_uuids list
        custom_attributes: Purchase invoice-level custom attributes
        item_config: Configuration for items (system vs line items)
        line_item_custom_attributes: Line item custom attributes
    """
    account_choices = _derive_account_choices(account_ids, default_currency=default_currency)
    if not account_choices:
        raise ValueError("No account IDs available to associate with purchase invoices.")

    if custom_attributes is None:
        custom_attributes = []
    if line_item_custom_attributes is None:
        line_item_custom_attributes = []
    if item_config is None:
        item_config = default_item_config()
    if tax_config is None:
        tax_config = {"tax_uuids": []}

    include_system = bool(item_config.get("include_system_items", True))
    include_line_items = bool(item_config.get("include_line_items", True))
    if not include_system and not include_line_items:
        include_line_items = True

    system_identifiers = item_config.get("system_identifiers") or []
    if include_system and not system_identifiers:
        system_identifiers = _fallback_system_identifiers()

    tax_uuids = tax_config.get("tax_uuids", [])

    rows = []
    for idx in range(purchase_invoice_count):
        account_id, currency = random.choice(account_choices)
        issue_date = generate_issue_date()
        due_date = generate_due_date(issue_date)

        row = {
            "purchase_invoice_id": generate_purchase_invoice_id(),
            "purchase_invoice_origin": f"CSV IMPORT - {idx + 1}",
            "purchase_invoice_currency": currency or default_currency,
            "purchase_invoice_account_id": account_id,
            "purchase_invoice_issue_date": issue_date,
            "purchase_invoice_due_date": due_date,
            "purchase_invoice_price_tax_inclusive": "",
            "purchase_invoice_purchase_invoice_note": generate_purchase_invoice_note(),
            "purchase_invoice_custom_form_template": custom_form_template,
        }

        # Randomly set purchase_invoice_price_tax_inclusive for some rows
        if random.random() < 0.3:
            row["purchase_invoice_price_tax_inclusive"] = "TRUE"

        # Apply purchase invoice-level custom attributes BEFORE line items (for proper column order)
        for attr in custom_attributes:
            row[attr["column_name"]] = _random_value_for_attr(attr)

        min_items = max(1, int(item_config.get("min_items_per_purchase_invoice", 1)))
        max_items = max(min_items, int(item_config.get("max_items_per_purchase_invoice", min_items)))
        total_items = random.randint(min_items, max_items)

        for item_idx in range(total_items):
            item_row = row.copy()
            is_system_item = False

            if include_system and include_line_items:
                is_system_item = random.random() < 0.5
            elif include_system:
                is_system_item = True
            else:
                is_system_item = False

            if is_system_item:
                identifier = random.choice(system_identifiers)
                item_row["purchase_invoice_line_item_id"] = identifier
                item_row["purchase_invoice_item_name"] = ""
            elif include_line_items:
                item_row["purchase_invoice_line_item_id"] = ""
                item_row["purchase_invoice_item_name"] = generate_line_item_name()

            item_row["purchase_invoice_line_item_order_quantity"] = generate_line_item_quantity()
            item_row["purchase_invoice_line_item_price"] = generate_line_item_price()

            # Tax UUID (randomly assign from provided list or skip)
            if tax_uuids and random.random() < 0.8:
                item_row["purchase_invoice_line_item_tax_uuid"] = random.choice(tax_uuids)
            else:
                item_row["purchase_invoice_line_item_tax_uuid"] = ""

            # Tax exempt (random rows)
            if random.random() < 0.1:
                item_row["purchase_invoice_line_item_tax_exempt"] = "TRUE"
            else:
                item_row["purchase_invoice_line_item_tax_exempt"] = ""

            # Apply line item custom attributes (after all line item fields)
            for attr in line_item_custom_attributes:
                item_row[attr["column_name"]] = _random_value_for_attr(attr)

            # Blank out purchase invoice-level fields for additional items (except mandatory fields)
            if item_idx > 0:
                for key in list(item_row.keys()):
                    if key in ("purchase_invoice_id", "purchase_invoice_account_id", "purchase_invoice_currency",
                               "purchase_invoice_issue_date", "purchase_invoice_due_date"):
                        continue
                    if key.startswith("purchase_invoice_line_item_"):
                        continue
                    if key.startswith("ca_purchase_invoice_item_attr_"):
                        continue
                    item_row[key] = ""

            rows.append(item_row)

    return rows


def generate_purchase_invoice_csv(
    purchase_invoice_count,
    account_ids=None,
    default_currency="AUD",
    custom_form_template="Default for Purchase Invoice",
    tax_config=None,
    custom_attributes=None,
    item_config=None,
    line_item_custom_attributes=None,
):
    """Generate a purchase invoice CSV file and return its filepath and purchase invoice IDs."""
    rows = generate_purchase_invoice_rows(
        purchase_invoice_count,
        account_ids=account_ids,
        default_currency=default_currency,
        custom_form_template=custom_form_template,
        tax_config=tax_config,
        custom_attributes=custom_attributes,
        item_config=item_config,
        line_item_custom_attributes=line_item_custom_attributes,
    )
    df = pd.DataFrame(rows).fillna("")

    # Prefix date columns with tab character to prevent Excel auto-conversion
    date_columns = ['purchase_invoice_issue_date', 'purchase_invoice_due_date']

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
    filename = f"PURCHASE_INVOICE_DUMMY_DATA_{purchase_invoice_count}_{timestamp}.csv"
    filepath = f"C:\\Users\\Rahman\\Downloads\\{filename}"
    df.to_csv(filepath, index=False, quoting=1)  # QUOTE_MINIMAL

    print(f"\nSuccessfully generated {purchase_invoice_count} purchase invoices!")
    print(f"File saved to: {filepath}")
    if rows:
        print("\nSample data:")
        print(f"  First Purchase Invoice ID: {rows[0]['purchase_invoice_id']}")
        print(f"  First Account ID: {rows[0]['purchase_invoice_account_id']}")

    purchase_invoice_ids = list({row['purchase_invoice_id'] for row in rows if row.get('purchase_invoice_id')})
    print(f"  Total unique purchase invoice IDs: {len(purchase_invoice_ids)}")
    return filepath, purchase_invoice_ids


def prompt_purchase_invoice_account_ids():
    """Prompt the user for supplier account IDs to attach to purchase invoices."""
    while True:
        raw = input("Enter supplier account IDs (comma-separated): ").strip()
        account_ids = [value.strip() for value in raw.split(",") if value.strip()]
        if account_ids:
            return account_ids
        print("Please enter at least one account ID.")


def prompt_custom_form_template():
    """Prompt user for custom form template with default."""
    use_custom = input("Do you want to use a custom form template? (y/N, default n): ").strip().lower()
    if use_custom not in ("y", "yes"):
        return "Default for Purchase Invoice"

    default = "Default for Purchase Invoice"
    raw = input(f"Enter custom form template (default: {default}): ").strip()
    return raw if raw else default


def prompt_tax_config():
    """
    Prompt user for tax configuration (UUID-based).

    Returns dict with:
        tax_uuids: list[str]
    """
    use_tax = input("Do you want tax configuration? (y/N, default n): ").strip().lower()
    if use_tax not in ("y", "yes"):
        return {"tax_uuids": []}

    tax_uuids = []

    while True:
        uuid = input("Enter tax UUID (or press Enter to finish): ").strip()
        if not uuid:
            break
        tax_uuids.append(uuid)

        if tax_uuids:
            more = input("Add another tax UUID? (y/N, default n): ").strip().lower()
            if more not in ("y", "yes"):
                break

    return {"tax_uuids": tax_uuids}


def prompt_purchase_invoice_item_config():
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
        "system_identifiers": [],
    }

    if include_system:
        while True:
            raw_ids = input("Enter system item IDs (comma-separated, e.g., ITEM-1001,ITEM-1002): ").strip()
            identifiers = [value.strip() for value in raw_ids.split(",") if value.strip()]
            if identifiers:
                config["system_identifiers"] = identifiers
                break
            print("Please enter at least one system item ID.")

    # Max items per purchase invoice (min is always 1)
    min_items = 1
    while True:
        max_raw = input("Maximum items per purchase invoice (default 5): ").strip()
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

    config["min_items_per_purchase_invoice"] = min_items
    config["max_items_per_purchase_invoice"] = max_items

    return config


def prompt_purchase_invoice_custom_attributes():
    """
    Prompt user for purchase invoice-level custom attributes (default: 10).
    """
    use_attrs = input("Do you want purchase invoice custom attributes? (y/N, default n): ").strip().lower()
    if use_attrs not in ("y", "yes"):
        return []

    while True:
        raw = input("How many purchase invoice custom attributes? (>=1, default 10): ").strip()
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
        default_choice = input("Use default 10 purchase invoice custom attributes? (y/N, default n): ").strip().lower()
        if default_choice in ("y", "yes"):
            return get_default_purchase_invoice_custom_attributes()

    return collect_custom_attrs("ca_purchase_invoice_attr_", count)


def prompt_line_item_custom_attributes():
    """
    Prompt user for custom attributes on line items (default: 10).
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

    return collect_custom_attrs("ca_purchase_invoice_item_attr_", count)


def collect_custom_attrs(prefix, count):
    """Collect custom attribute definitions from user input."""
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


def save_generation_config(path, config):
    """Save generation configuration to JSON."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2)
        print(f"Configuration saved to {path}")
    except OSError as exc:
        print(f"WARNING: Could not save configuration to {path}: {exc}")


def load_generation_config(path):
    """Load generation configuration from JSON."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Generate purchase invoice CSV data.")
        parser.add_argument(
            "count",
            type=int,
            nargs="?",
            default=DEFAULT_PURCHASE_INVOICE_COUNT,
            help=f"Number of purchase invoices to generate (default: {DEFAULT_PURCHASE_INVOICE_COUNT})",
        )
        parser.add_argument(
            "--batch",
            action="store_true",
            help="Generate multiple files: 200, 300, 400, and 500 purchase invoices",
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
                filepath, _ = generate_purchase_invoice_csv(
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

        purchase_invoice_count = max(1, args.count)

        if args.load_config:
            try:
                cfg = load_generation_config(args.load_config)
            except OSError as exc:
                print(f"ERROR: Could not load config from {args.load_config}: {exc}")
                raise SystemExit(1)

            if args.count == DEFAULT_PURCHASE_INVOICE_COUNT:
                purchase_invoice_count = int(cfg.get("purchase_invoice_count", purchase_invoice_count))
            account_ids = cfg.get("account_ids") or _generate_placeholder_account_ids()
            custom_form_template = cfg.get("custom_form_template", "Default for Purchase Invoice")
            tax_cfg = cfg.get("tax_config") or {"tax_uuids": []}
            purchase_invoice_attrs = cfg.get("purchase_invoice_custom_attributes") or []
            item_config = cfg.get("item_config") or default_item_config()
            line_item_custom_attrs = cfg.get("line_item_custom_attributes") or []
        else:
            account_ids = prompt_purchase_invoice_account_ids()
            custom_form_template = prompt_custom_form_template()
            tax_cfg = prompt_tax_config()
            purchase_invoice_attrs = prompt_purchase_invoice_custom_attributes()
            item_config = prompt_purchase_invoice_item_config()
            line_item_custom_attrs = prompt_line_item_custom_attributes()

            if args.save_config:
                config = {
                    "purchase_invoice_count": purchase_invoice_count,
                    "account_ids": account_ids,
                    "custom_form_template": custom_form_template,
                    "tax_config": tax_cfg,
                    "purchase_invoice_custom_attributes": purchase_invoice_attrs,
                    "item_config": item_config,
                    "line_item_custom_attributes": line_item_custom_attrs,
                }
                save_generation_config(args.save_config, config)

        generate_purchase_invoice_csv(
            purchase_invoice_count,
            account_ids=account_ids,
            custom_form_template=custom_form_template,
            tax_config=tax_cfg,
            custom_attributes=purchase_invoice_attrs,
            item_config=item_config,
            line_item_custom_attributes=line_item_custom_attrs,
        )
    except KeyboardInterrupt:
        print("\nPurchase invoice generation cancelled by user.")
