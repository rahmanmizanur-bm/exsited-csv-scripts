import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("en_AU")
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "purchase_payment_generator_config.json"
DEFAULT_PURCHASE_PAYMENT_COUNT = 100


def generate_purchase_payment_id(row_num):
    """Generate purchase payment ID based on row number."""
    return f"CSV-PPMT-{str(row_num).zfill(3)}"


def generate_purchase_payment_origin():
    """Generate purchase payment origin."""
    origin_type = random.choice(["SUP", "PO"])
    row_num = random.randint(1, 999)
    return f"CSV-{origin_type}-{str(row_num).zfill(3)}"


def generate_purchase_payment_date():
    """Generate purchase payment date (today or future - 0 to 90 days ahead)."""
    today = datetime.now()
    offset_days = random.randint(0, 90)
    payment_date = today + timedelta(days=offset_days)
    return payment_date.strftime("%Y-%m-%d")


def generate_purchase_payment_amount(min_amount=100, max_amount=50000):
    """Generate purchase payment amount >= minimum (not zero)."""
    return round(random.uniform(min_amount, max_amount), 2)


def generate_purchase_payment_note():
    """Generate random purchase payment note."""
    notes = [
        "Payment issued via bank transfer to supplier",
        "Supplier payment processed successfully",
        "Wire transfer completed for invoice",
        "Electronic payment sent to vendor",
        "Check payment issued and mailed",
        "Payment applied to supplier account",
        "Advance payment for upcoming order",
        "Partial payment - balance scheduled",
        "ACH payment processed to supplier",
        "Cash payment issued and recorded",
        "Payment completed - purchase order settled",
        "Online payment gateway transaction completed",
        "Direct debit payment to supplier processed",
        "Mobile payment app transaction confirmed",
        "Payment reconciliation with supplier completed",
    ]
    return random.choice(notes)


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


def load_purchase_invoice_ids_from_csv(csv_path):
    """Load purchase invoice IDs from existing purchase invoice CSV file."""
    try:
        df = pd.read_csv(csv_path)
        if "purchase_invoice_id" in df.columns:
            purchase_invoice_ids = df["purchase_invoice_id"].dropna().unique().tolist()
            return [str(piid).strip() for piid in purchase_invoice_ids if piid]
        else:
            print(f"WARNING: No 'purchase_invoice_id' column found in {csv_path}")
            return []
    except FileNotFoundError:
        print(f"WARNING: Purchase invoice CSV file not found at {csv_path}")
        return []
    except Exception as e:
        print(f"WARNING: Error reading purchase invoice CSV: {e}")
        return []


def generate_purchase_invoice_id():
    """Generate random purchase invoice ID as fallback."""
    return f"CSV-PINV-{random.randint(100000, 999999)}"


def _get_purchase_invoice_choices(purchase_invoice_csv_path=None, purchase_invoice_ids_param=None):
    """
    Get purchase invoice IDs from various sources in priority order:
    1. purchase_invoice_ids_param (command line override)
    2. purchase_invoice_csv_path (load from CSV)
    """
    if purchase_invoice_ids_param:
        return [piid.strip() for piid in purchase_invoice_ids_param if piid.strip()]

    if purchase_invoice_csv_path:
        loaded_ids = load_purchase_invoice_ids_from_csv(purchase_invoice_csv_path)
        if loaded_ids:
            return loaded_ids

    return []


def generate_purchase_payment_rows(
    purchase_payment_count,
    purchase_invoice_csv_path=None,
    purchase_invoice_ids=None,
    custom_attributes=None,
    multi_invoice_enabled=False,
    min_amount=100,
    max_amount=50000,
    payment_processors=None,
):
    """
    Generate purchase payment rows with optional multi-invoice support.

    Args:
        purchase_payment_count: Number of purchase payment records to generate
        purchase_invoice_csv_path: Path to purchase invoice CSV file
        purchase_invoice_ids: List of purchase invoice IDs (overrides CSV)
        custom_attributes: List of custom attribute definitions
        multi_invoice_enabled: If True, creates multiple rows per payment
        min_amount: Minimum payment amount
        max_amount: Maximum payment amount
        payment_processors: List of payment processors (default: ["Cash"])

    Returns:
        List of purchase payment row dictionaries
    """
    purchase_invoice_choices = _get_purchase_invoice_choices(purchase_invoice_csv_path, purchase_invoice_ids)
    if not purchase_invoice_choices:
        raise ValueError("No purchase invoice IDs available for purchase payment generation.")

    if not payment_processors:
        payment_processors = ["Cash"]

    if custom_attributes is None:
        custom_attributes = []

    rows = []

    for payment_num in range(1, purchase_payment_count + 1):
        purchase_payment_id = generate_purchase_payment_id(payment_num)
        purchase_payment_origin = generate_purchase_payment_origin()
        purchase_payment_date = generate_purchase_payment_date()
        purchase_payment_processor = random.choice(payment_processors)
        purchase_payment_amount = generate_purchase_payment_amount(min_amount, max_amount)
        purchase_payment_note = generate_purchase_payment_note()

        # Apply custom attributes BEFORE invoice references (for proper column order)
        custom_attrs = {}
        for attr in custom_attributes:
            col_name = attr["column_name"]
            if attr.get("constant") and attr.get("value") is not None:
                custom_attrs[col_name] = attr["value"]
            else:
                custom_attrs[col_name] = _random_value_for_attr(attr)

        if multi_invoice_enabled:
            num_invoices = random.randint(2, min(5, len(purchase_invoice_choices)))
            selected_invoices = random.sample(purchase_invoice_choices, num_invoices)
        else:
            selected_invoices = [random.choice(purchase_invoice_choices)]

        for purchase_invoice_id in selected_invoices:
            row = {
                "purchase_payment_id": purchase_payment_id,
                "purchase_payment_origin": purchase_payment_origin,
                "purchase_payment_date": purchase_payment_date,
                "purchase_payment_processor": purchase_payment_processor,
                "purchase_payment_amount": purchase_payment_amount,
                "purchase_payment_note": purchase_payment_note,
            }
            # Add custom attributes before invoice ID (for proper column order)
            row.update(custom_attrs)
            row["purchase_payment_invoice_id"] = purchase_invoice_id
            rows.append(row)

    return rows


def generate_purchase_payment_csv(
    purchase_payment_count,
    purchase_invoice_csv_path=None,
    purchase_invoice_ids=None,
    custom_attributes=None,
    multi_invoice_enabled=False,
    min_amount=100,
    max_amount=50000,
    payment_processors=None,
):
    """Generate a purchase payment CSV file and return its filepath."""
    rows = generate_purchase_payment_rows(
        purchase_payment_count,
        purchase_invoice_csv_path=purchase_invoice_csv_path,
        purchase_invoice_ids=purchase_invoice_ids,
        custom_attributes=custom_attributes,
        multi_invoice_enabled=multi_invoice_enabled,
        min_amount=min_amount,
        max_amount=max_amount,
        payment_processors=payment_processors,
    )

    df = pd.DataFrame(rows).fillna("")

    date_columns = ["purchase_payment_date"]

    # Add custom attribute date columns
    if custom_attributes:
        for attr in custom_attributes:
            if attr.get('type') == 'date':
                date_columns.append(attr['column_name'])

    # Prefix dates with tab character to force text format in Excel
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"\t{x}" if x and x != "" else x)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"PURCHASE_PAYMENT_DUMMY_DATA_{purchase_payment_count}_{timestamp}.csv"
    filepath = f"C:\\Users\\Rahman\\Downloads\\{filename}"
    df.to_csv(filepath, index=False, quoting=1)

    print(f"\nSuccessfully generated {purchase_payment_count} purchase payment records!")
    print(f"File saved to: {filepath}")
    print(f"Total CSV rows: {len(rows)}")
    if rows:
        print("\nSample data:")
        print(f"  First Purchase Payment ID: {rows[0]['purchase_payment_id']}")
        print(f"  First Purchase Invoice ID: {rows[0]['purchase_payment_invoice_id']}")
        print(f"  Payment Amount Range: ${min([r['purchase_payment_amount'] for r in rows]):.2f} - ${max([r['purchase_payment_amount'] for r in rows]):.2f}")
    unique_payments = len({row['purchase_payment_id'] for row in rows if row.get('purchase_payment_id')})
    print(f"  Total unique purchase payment IDs: {unique_payments}")

    return filepath


def prompt_purchase_invoice_ids():
    """Prompt user for purchase invoice IDs (comma-separated)."""
    print("\nPurchase Payment Invoice Configuration:")
    print("1. Load from existing purchase invoice CSV file")
    print("2. Enter purchase invoice IDs manually (comma-separated)")

    choice = input("Choose option (1/2, default: 2): ").strip()

    if choice == "1":
        csv_path = input("Enter path to purchase invoice CSV file: ").strip()
        if csv_path and Path(csv_path).exists():
            return None, csv_path
        else:
            print("File not found. Please enter purchase invoice IDs manually.")
            while True:
                raw = input("Enter purchase invoice IDs (comma-separated): ").strip()
                purchase_invoice_ids = [piid.strip() for piid in raw.split(",") if piid.strip()]
                if purchase_invoice_ids:
                    return purchase_invoice_ids, None
                print("Please enter at least one purchase invoice ID.")
    else:
        while True:
            raw = input("Enter purchase invoice IDs (comma-separated): ").strip()
            purchase_invoice_ids = [piid.strip() for piid in raw.split(",") if piid.strip()]
            if purchase_invoice_ids:
                return purchase_invoice_ids, None
            print("Please enter at least one purchase invoice ID.")


def get_default_custom_attributes():
    """Return the default set of 10 custom attributes when requested."""
    dropdown_options = ["A", "B", "C", "D"]

    def make_attr(name, attr_type, options=None, quantity_min=None, quantity_max=None):
        return {
            "column_name": f"ca_purchase_payment_attr_{name}",
            "type": attr_type,
            "constant": False,
            "value": None,
            "options": options or [],
            "quantity_min": quantity_min,
            "quantity_max": quantity_max,
        }

    return [
        make_attr("CA_BOOL", "bool"),
        make_attr("CA_CHECKBOX", "checkboxes", options=dropdown_options),
        make_attr("CA_DATE", "date"),
        make_attr("CA_DROPDOWN", "dropdown", options=dropdown_options),
        make_attr("CA_DROPDOWN_WITH_MULTISELECT", "dropdown_multi", options=dropdown_options),
        make_attr("CA_MONEY", "money"),
        make_attr("CA_QUANTITY", "quantity", quantity_min=1, quantity_max=50),
        make_attr("CA_NUMBER", "number"),
        make_attr("CA_RADIO", "radio", options=dropdown_options),
        make_attr("CA_TEXT", "text"),
    ]


def collect_custom_attrs(prefix, count):
    """Collect custom attribute definitions from user."""
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


def prompt_custom_attributes():
    """
    Prompt user for purchase payment custom attributes (default: none).
    """
    use_attrs = input("Do you want purchase payment custom attributes? (y/N, default n): ").strip().lower()
    if use_attrs not in ("y", "yes"):
        return []

    while True:
        raw = input("How many purchase payment custom attributes? (>=1, default 10): ").strip()
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
        default_choice = input("Use default 10 purchase payment custom attributes? (y/N, default n): ").strip().lower()
        if default_choice in ("y", "yes"):
            return get_default_custom_attributes()

    return collect_custom_attrs("ca_purchase_payment_attr_", count)


def prompt_multi_invoice():
    """Prompt user for multi-invoice support."""
    response = input("Do you want multiple purchase invoices per payment? (y/N, default: n): ").strip().lower()
    return response in ("y", "yes")


def prompt_payment_processors():
    """Prompt user for payment processor options."""
    print("\nPayment Processor Configuration:")
    raw = input("Enter payment processors (comma-separated, default: Cash): ").strip()
    if not raw:
        return ["Cash"]
    processors = [p.strip() for p in raw.split(",") if p.strip()]
    return processors if processors else ["Cash"]


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
        parser = argparse.ArgumentParser(description="Generate purchase payment CSV data.")
        parser.add_argument(
            "count",
            type=int,
            nargs="?",
            default=DEFAULT_PURCHASE_PAYMENT_COUNT,
            help=f"Number of purchase payment records to generate (default: 100)",
        )
        parser.add_argument(
            "--purchase-invoice-csv",
            dest="purchase_invoice_csv",
            type=str,
            default=None,
            help="Path to purchase invoice CSV file to load purchase invoice IDs",
        )
        parser.add_argument(
            "--purchase-invoice-ids",
            dest="purchase_invoice_ids",
            type=str,
            default=None,
            help="Comma-separated purchase invoice IDs (overrides purchase invoice CSV)",
        )
        parser.add_argument(
            "--multi-invoice",
            dest="multi_invoice",
            action="store_true",
            help="Enable multiple purchase invoices per payment",
        )
        parser.add_argument(
            "--payment-processors",
            dest="payment_processors",
            type=str,
            default=None,
            help="Comma-separated payment processors (default: Cash)",
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

        purchase_payment_count = max(1, args.count)

        if args.load_config:
            try:
                cfg = load_generation_config(args.load_config)
            except OSError as exc:
                print(f"ERROR: Could not load config from {args.load_config}: {exc}")
                raise SystemExit(1)

            if args.count == DEFAULT_PURCHASE_PAYMENT_COUNT:
                purchase_payment_count = int(cfg.get("purchase_payment_count", purchase_payment_count))
            purchase_invoice_csv_path = cfg.get("purchase_invoice_csv_path")
            purchase_invoice_ids_cfg = cfg.get("purchase_invoice_ids")
            custom_attrs = cfg.get("custom_attributes") or []
            multi_invoice = bool(cfg.get("multi_invoice_enabled", False))
            payment_processors_cfg = cfg.get("payment_processors", ["Cash"])
        else:
            if args.purchase_invoice_ids:
                purchase_invoice_ids_cfg = [piid.strip() for piid in args.purchase_invoice_ids.split(",") if piid.strip()]
                purchase_invoice_csv_path = None
            elif args.purchase_invoice_csv:
                purchase_invoice_csv_path = args.purchase_invoice_csv
                purchase_invoice_ids_cfg = None
            else:
                purchase_invoice_ids_cfg, purchase_invoice_csv_path = prompt_purchase_invoice_ids()

            custom_attrs = prompt_custom_attributes()

            if args.multi_invoice:
                multi_invoice = True
            elif args.purchase_invoice_ids or args.purchase_invoice_csv:
                multi_invoice = False
            else:
                multi_invoice = prompt_multi_invoice()

            if args.payment_processors:
                payment_processors_cfg = [p.strip() for p in args.payment_processors.split(",") if p.strip()]
            elif args.purchase_invoice_ids or args.purchase_invoice_csv:
                payment_processors_cfg = ["Cash"]
            else:
                payment_processors_cfg = prompt_payment_processors()

            if args.save_config:
                config = {
                    "purchase_payment_count": purchase_payment_count,
                    "purchase_invoice_csv_path": purchase_invoice_csv_path,
                    "purchase_invoice_ids": purchase_invoice_ids_cfg,
                    "custom_attributes": custom_attrs,
                    "multi_invoice_enabled": multi_invoice,
                    "payment_processors": payment_processors_cfg,
                    "payment_amount_min": 100,
                    "payment_amount_max": 50000,
                }
                save_generation_config(args.save_config, config)

        generate_purchase_payment_csv(
            purchase_payment_count,
            purchase_invoice_csv_path=purchase_invoice_csv_path,
            purchase_invoice_ids=purchase_invoice_ids_cfg,
            custom_attributes=custom_attrs,
            multi_invoice_enabled=multi_invoice,
            payment_processors=payment_processors_cfg,
        )
    except KeyboardInterrupt:
        print("\nPurchase payment generation cancelled by user.")
