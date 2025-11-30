import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("en_AU")
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "item_generator_config.json"
DEFAULT_ITEM_COUNT = 200

ITEM_TYPES = [
    "STANDARD",
    "GIFT_CERTIFICATE",
    "DIRECT_COST",
    "VARIATION",
    "BUNDLE",
    "FAMILY",
]

BASE_UOMS = [
    "Metre",
    "Kilometre",
    "Gram",
    "Kilogram",
    "Litre",
    "Kilolitre",
    "Week",
    "Month",
    "Year",
    "Watt",
    "Kilowatt",
]

ACCOUNTING_CODES = [
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


def generate_item_id():
    return f"CSV-ITEM-{random.randint(10000, 99999)}"


def random_text():
    return fake.sentence(nb_words=10)


def random_price(min_value=5, max_value=1000):
    return round(random.uniform(min_value, max_value), 2)


def prompt_yes_no(message, default=False):
    default_char = "y" if default else "n"
    raw = input(f"{message} (y/N, default {default_char}): ").strip().lower()
    if raw == "":
        return default
    return raw in ("y", "yes")


def prompt_item_types():
    use_multi = prompt_yes_no("Do you want multiple item types?", default=False)
    if not use_multi:
        return ["STANDARD"]
    print(
        "Available item types:\n"
        "  1) STANDARD\n"
        "  2) GIFT_CERTIFICATE\n"
        "  3) DIRECT_COST\n"
        "  4) VARIATION\n"
        "  5) BUNDLE\n"
        "  6) FAMILY\n"
        "Enter numbers (comma-separated) or 'all' for every type."
    )
    while True:
        raw = input("Selection (default all): ").strip().lower()
        if not raw or raw == "all":
            return ITEM_TYPES[:]
        try:
            selected = [int(n.strip()) for n in raw.split(",")]
        except ValueError:
            print("Please enter valid numbers or 'all'.")
            continue
        valid = [
            ITEM_TYPES[i - 1]
            for i in selected
            if 1 <= i <= len(ITEM_TYPES)
        ]
        if valid:
            return valid
        print("Please select at least one valid option.")


def prompt_uom_config():
    use_uom = prompt_yes_no("Do you want to specify base UOMs?", default=False)
    if not use_uom:
        return {"use_uom": False, "uoms": [], "allow_auto": True}
    while True:
        raw = input(
            "Enter a single base UOM. Leave blank to let generator choose defaults: "
        ).strip()
        if raw.lower() == "auto" or raw == "":
            return {"use_uom": True, "uoms": BASE_UOMS[:], "allow_auto": True}
        if "," in raw:
            print("Please enter only one UOM (not comma-separated).")
            continue
        allow_auto = prompt_yes_no("Allow generator to choose random UOMs?", default=True)
        return {"use_uom": True, "uoms": [raw], "allow_auto": allow_auto}


def prompt_group_config(total_items):
    use_group = prompt_yes_no("Do you want item groups?", default=False)
    if not use_group:
        return {"group_names": [], "assign_count": 0}
    while True:
        raw = input("Enter item group names (comma-separated): ").strip()
        groups = [g.strip() for g in raw.split(",") if g.strip()]
        if groups:
            break
        print("Please enter at least one group name.")
    default_assign = max(1, total_items // 10)
    while True:
        raw = input(
            f"How many items should have a group? (0-{total_items}, default {default_assign}): "
        ).strip()
        if raw == "":
            assign_count = default_assign
            break
        try:
            assign_count = int(raw)
        except ValueError:
            print("Please enter a valid number.")
            continue
        if 0 <= assign_count <= total_items:
            break
        print(f"Enter a number between 0 and {total_items}.")
    return {"group_names": groups, "assign_count": assign_count}


def prompt_custom_form_config():
    use_form = prompt_yes_no("Do you want item_custom_form values?", default=False)
    if not use_form:
        return {"forms": []}
    default_choice = prompt_yes_no("Use default custom form (Default for Item)?", True)
    if default_choice:
        return {"forms": ["Default for Item"]}
    while True:
        raw = input(
            "Enter item custom form names (comma-separated, e.g., Item_Default_Form_1): "
        ).strip()
        forms = [f.strip() for f in raw.split(",") if f.strip()]
        if forms:
            return {"forms": forms}
        print("Please enter at least one custom form name.")


def prompt_custom_attributes(prefix):
    use_attrs = input("Do you want custom attributes? (Y/n, default y): ").strip().lower()
    if use_attrs in ("n", "no"):
        return 0, []

    while True:
        raw = input("How many custom attributes do you want? (>=1, default 10): ").strip()
        if raw == "":
            count = 10
            break
        try:
            count = int(raw)
        except ValueError:
            print("Enter a valid number.")
            continue
        if count >= 1:
            break
        print("Please enter a positive number.")
    if count == 10:
        use_defaults = prompt_yes_no(f"Use default 10 attributes for {prefix}?", True)
        if use_defaults:
            if prefix == "ca_item_attr_":
                return 10, get_default_custom_attributes(prefix)
            return 10, get_default_line_custom_attributes(prefix)
    attrs = []
    for idx in range(1, count + 1):
        print(f"\nCustom attribute {idx}/{count}")
        name = ""
        while not name:
            raw_name = input("  Enter attribute name (e.g., COLOR): ").strip()
            if raw_name:
                name = raw_name.replace(" ", "_").upper()
            else:
                print("  Name cannot be empty.")
        column_name = f"{prefix}{name}"
        attr_type = prompt_attribute_type()
        quantity_min, quantity_max = None, None
        if attr_type == "quantity":
            quantity_min, quantity_max = prompt_quantity_range()
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
                "options": options,
                "quantity_min": quantity_min,
                "quantity_max": quantity_max,
            }
        )
    return len(attrs), attrs


def prompt_attribute_type():
    menu = (
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
    print(menu, end="")
    type_map = {
        "1": "bool",
        "2": "number",
        "3": "string",
        "4": "text",
        "5": "date",
        "6": "money",
        "7": "quantity",
        "8": "dropdown",
        "9": "dropdown_multi",
        "10": "checkboxes",
        "11": "radio",
        "bool": "bool",
        "boolean": "bool",
        "number": "number",
        "string": "string",
        "text": "text",
        "date": "date",
        "money": "money",
        "quantity": "quantity",
        "dropdown": "dropdown",
        "dropdown_multi": "dropdown_multi",
        "checkboxes": "checkboxes",
        "radio": "radio",
    }
    while True:
        raw = input("  Enter type (1-11 or name): ").strip().lower()
        attr_type = type_map.get(raw)
        if attr_type:
            return attr_type
        print("  Invalid choice.")


def prompt_quantity_range():
    qmin, qmax = 1, 50
    while True:
        raw = input("  Enter quantity range as min-max (default 1-50): ").strip()
        if raw == "":
            break
        parts = [p.strip() for p in raw.replace(" ", "").split("-") if p.strip()]
        if len(parts) != 2:
            print("  Please enter format min-max, e.g., 5-90.")
            continue
        try:
            min_val = int(parts[0])
            max_val = int(parts[1])
        except ValueError:
            print("  Use whole numbers.")
            continue
        if min_val > max_val:
            print("  Min cannot be greater than max.")
            continue
        qmin, qmax = min_val, max_val
        break
    return qmin, qmax


def get_default_custom_attributes(prefix):
    dropdown = ["A", "B", "C", "D"]
    defaults = [
        {"name": "CA_BOOL", "type": "bool"},
        {"name": "CA_CHECKBOX", "type": "checkboxes", "options": dropdown},
        {"name": "CA_DATE", "type": "date"},
        {"name": "CA_DROPDOWN", "type": "dropdown", "options": dropdown},
        {
            "name": "CA_DROPDOWN_WITH_MULTISELECT",
            "type": "dropdown_multi",
            "options": dropdown,
        },
        {"name": "CA_MONEY", "type": "money"},
        {
            "name": "CA_QUANTITY",
            "type": "quantity",
            "quantity_min": 1,
            "quantity_max": 50,
        },
        {"name": "CA_NUMBER", "type": "number"},
        {"name": "CA_RADIO", "type": "radio", "options": dropdown},
        {"name": "CA_TEXT", "type": "text"},
    ]
    results = []
    for item in defaults:
        results.append(
            {
                "column_name": f"{prefix}{item['name']}",
                "type": item["type"],
                "options": item.get("options", []),
                "quantity_min": item.get("quantity_min"),
                "quantity_max": item.get("quantity_max"),
            }
        )
    return results


def get_default_line_custom_attributes(prefix):
    return get_default_custom_attributes(prefix)


def prompt_sale_currency_config():
    raw = input("Enter sale currencies (comma-separated, default AUD): ").strip()
    if not raw:
        return ["AUD"]
    return [c.strip().upper() for c in raw.split(",") if c.strip()]


def prompt_tax_config(entity_name):
    use_tax = prompt_yes_no(f"Do you want tax codes for {entity_name}?", default=False)
    if not use_tax:
        return []
    while True:
        raw = input("Enter tax code UUIDs (comma-separated): ").strip()
        codes = [c.strip() for c in raw.split(",") if c.strip()]
        if codes:
            return codes
        print("Enter at least one tax code.")


def prompt_accounting_code_usage(section_name):
    return prompt_yes_no(
        f"Enable accounting code assignment for {section_name}?", default=True
    )


def prompt_discount_profile():
    use_profile = prompt_yes_no("Do you want item_sale_discount_profile values?", False)
    if not use_profile:
        return []
    while True:
        raw = input("Enter discount profile names (comma-separated): ").strip()
        profiles = [p.strip() for p in raw.split(",") if p.strip()]
        if profiles:
            return profiles
        print("Enter at least one profile name.")


def prompt_pricing_levels():
    use_levels = prompt_yes_no(
        "Do you want item_sale_sales_pricing_level_list entries?", False
    )
    if not use_levels:
        return []
    while True:
        raw = input("Enter pricing level names (comma-separated): ").strip()
        levels = [p.strip() for p in raw.split(",") if p.strip()]
        if levels:
            return levels
        print("Enter at least one pricing level.")


def prompt_supplier_management():
    use_supplier = prompt_yes_no("Do you want supplier management?", False)
    if not use_supplier:
        return {"use": False, "suppliers": [], "prices": []}
    while True:
        raw_sup = input("Enter supplier account IDs (comma-separated): ").strip()
        suppliers = [s.strip() for s in raw_sup.split(",") if s.strip()]
        if suppliers:
            break
        print("Enter at least one supplier.")
    prices = [str(random_price(5, 800)) for _ in suppliers]
    print(f"Auto-generated supplier prices: {', '.join(prices)}")
    return {"use": True, "suppliers": suppliers, "prices": prices}


def prompt_inventory_config():
    use_inventory = prompt_yes_no("Do you want inventory management?", False)
    if not use_inventory:
        return {"use": False, "warehouses": []}
    while True:
        raw = input("Enter warehouse names (comma-separated): ").strip()
        warehouses = [w.strip() for w in raw.split(",") if w.strip()]
        if warehouses:
            break
        print("Enter at least one warehouse.")
    return {"use": True, "warehouses": warehouses}


def random_bool(probability):
    return random.random() < probability


def _random_value_for_attr(attr):
    attr_type = attr["type"]
    options = attr.get("options") or []
    if attr_type == "bool":
        return random.choice(["TRUE", "FALSE"])
    if attr_type == "number":
        return random.randint(0, 1000)
    if attr_type == "string":
        return fake.word()
    if attr_type == "text":
        return fake.sentence(nb_words=8)
    if attr_type == "date":
        today = datetime.now()
        offset_days = random.randint(-365, 365)
        random_date = today + timedelta(days=offset_days)
        return random_date.date().isoformat()
    if attr_type == "money":
        return round(random.uniform(10, 1000), 2)
    if attr_type == "quantity":
        qmin = attr.get("quantity_min") or 1
        qmax = attr.get("quantity_max") or 50
        qmin, qmax = int(qmin), int(qmax)
        if qmin > qmax:
            qmin, qmax = qmax, qmin
        return random.randint(qmin, qmax)
    if attr_type == "dropdown":
        return random.choice(options) if options else ""
    if attr_type == "dropdown_multi":
        if not options:
            return ""
        k = random.randint(1, len(options))
        return ",".join(random.sample(options, k=k))
    if attr_type == "checkboxes":
        if not options:
            return ""
        k = random.randint(1, len(options))
        return ",".join(random.sample(options, k=k))
    if attr_type == "radio":
        return random.choice(options) if options else ""
    return ""


def save_config(path, config):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2)
        print(f"Configuration saved to {path}")
    except OSError as exc:
        print(f"WARNING: Could not save configuration: {exc}")


def load_config(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def generate_item_data(
    num_rows,
    item_types,
    uom_config,
    group_config,
    custom_form_config,
    custom_attributes,
    sale_currencies,
    sale_tax_codes,
    sale_accounting_enabled,
    discount_profiles,
    pricing_levels,
    sale_properties_enabled,
    purchase_currencies,
    purchase_tax_codes,
    purchase_accounting_enabled,
    supplier_config,
    inventory_config,
    line_custom_attributes,
):
    data = []
    group_names = group_config.get("group_names", [])
    assign_count = group_config.get("assign_count", 0)
    group_indices = set(random.sample(range(num_rows), min(assign_count, num_rows))) if group_names and assign_count > 0 else set()
    warehouses = inventory_config.get("warehouses", [])

    for i in range(num_rows):
        item_id = generate_item_id()
        item_name = fake.catch_phrase()
        row = {
            "item_id": item_id,
            "item_name": item_name,
            "item_display_name": item_name,
            "item_type": random.choice(item_types),
            "item_description": random_text(),
            "item_invoice_note": random_text(),
            "item_origin": f"CSV IMPORT - {i + 1}",
            "item_base_uom": "",
            "item_upc_code": f"UPC-{random.randint(100000, 999999)}",
            "item_item_number": f"ITEM-{random.randint(1000, 9999)}",
            "item_group": "",
            "item_custom_form": "",
            "item_sale_enabled": "TRUE",
            "item_sale_sales_currency_list": ",".join(sale_currencies),
            "item_sale_charge_type": "FIXED",
            "item_sale_pricing_method": "STANDARD",
            "item_sale_pricing_type": "PER_UNIT",
            "item_sale_sales_uom_list": "",
            "item_sale_sales_currency": random.choice(sale_currencies),
            "item_sale_price": random_price(),
            "item_sale_price_tax_inclusive": "TRUE" if random_bool(0.1) else "",
            "item_sale_tax_code": random.choice(sale_tax_codes) if sale_tax_codes and random_bool(0.6) else "",
            "item_sale_accounting_code_revenue": "Sales Revenue" if sale_accounting_enabled and random_bool(0.7) else "",
            "item_sale_discount_profile": random.choice(discount_profiles) if discount_profiles and random_bool(0.5) else "",
            "item_sale_invoice_note": random_text(),
            "item_sale_use_pricing_level": "TRUE" if pricing_levels and random_bool(0.2) else "",
            "item_sale_sales_pricing_level_list": random.choice(pricing_levels) if pricing_levels and random_bool(0.2) else "",
            "item_sale_use_future_pricing": "TRUE" if random_bool(0.1) else "",
            "item_sale_use_on_sale_price": "",
            "item_sale_sale_price": "",
            "item_sale_sale_price_variant": "",
            "item_sale_fulfillment_mode": "",
            "item_sale_billing_mode": "",
            "item_sale_payment_mode": "",
            "item_purchase_enabled": "TRUE",
            "item_purchase_purchase_currency_list": ",".join(purchase_currencies),
            "item_purchase_pricing_type": "PER_UNIT",
            "item_purchase_purchase_uom_list": "",
            "item_purchase_price": random_price(5, 800),
            "item_purchase_purchase_currency": random.choice(purchase_currencies),
            "item_purchase_tax_exempt": "TRUE" if random_bool(0.1) else "",
            "item_purchase_price_tax_inclusive": "TRUE" if random_bool(0.1) else "",
            "item_purchase_tax_code": random.choice(purchase_tax_codes) if purchase_tax_codes and random_bool(0.6) else "",
            "item_purchase_accounting_code": "Cost of Goods Sold" if purchase_accounting_enabled and random_bool(0.7) else "",
            "item_purchase_purchase_order_note": random_text(),
            "item_purchase_use_supplier_management": "",
            "item_purchase_suppliers": "",
            "item_purchase_supplier_price": "",
            "item_inventory_enabled": "",
            "item_inventory_enable_warehouse_management": "",
            "item_inventory_warehouse_list": "",
            "item_inventory_default_warehouse": "",
            "item_inventory_enable_low_stock_notification": "",
            "item_inventory_low_stock_threshold_based_on": "",
            "item_inventory_enable_reordering": "",
            "item_inventory_reorder_threshold_based_on": "",
            "item_inventory_qty_avl_on_sale_determination": "",
            "item_inventory_qty_avl_on_sale": "",
            "item_inventory_use_temporary_qa_value": "",
            "item_inventory_use_pre_order": "",
        }

        if uom_config.get("use_uom"):
            uoms = uom_config.get("uoms") or BASE_UOMS
            row["item_base_uom"] = random.choice(uoms)

        if i in group_indices and group_names:
            row["item_group"] = random.choice(group_names)

        forms = custom_form_config.get("forms", [])
        if forms:
            row["item_custom_form"] = random.choice(forms)

        sale_properties = sale_properties_enabled or prompt_yes_no(
            "Use sale properties (fulfillment/billing/payment)?", True
        )
        if sale_properties:
            row["item_sale_fulfillment_mode"] = random.choice(["MANUAL", "AUTOMATIC"])
            row["item_sale_billing_mode"] = random.choice(["MANUAL", "AUTOMATIC"])
            row["item_sale_payment_mode"] = random.choice(["MANUAL", "AUTOMATIC"])

        if random_bool(0.15):
            row["item_sale_use_on_sale_price"] = "TRUE"
            row["item_sale_sale_price"] = random_price()
            row["item_sale_sale_price_variant"] = "FIXED"

        if supplier_config.get("use") and random_bool(0.5):
            row["item_purchase_use_supplier_management"] = "TRUE"
            suppliers = supplier_config["suppliers"]
            prices = supplier_config["prices"]
            row["item_purchase_suppliers"] = ",".join(suppliers)
            row["item_purchase_supplier_price"] = ",".join(prices)

        if inventory_config.get("use") and random_bool(0.2):
            row["item_inventory_enabled"] = "TRUE"
            row["item_inventory_enable_warehouse_management"] = "TRUE"
            row["item_inventory_warehouse_list"] = ",".join(warehouses)
            row["item_inventory_default_warehouse"] = random.choice(warehouses)
            row["item_inventory_enable_low_stock_notification"] = "TRUE" if random_bool(0.5) else ""
            row["item_inventory_low_stock_threshold_based_on"] = random.choice(
                ["INDIVIDUAL_WAREHOUSE", "ALL_WAREHOUSE"]
            )
            row["item_inventory_enable_reordering"] = "TRUE" if random_bool(0.5) else ""
            row["item_inventory_reorder_threshold_based_on"] = random.choice(
                ["INDIVIDUAL_WAREHOUSE", "ALL_WAREHOUSE"]
            )
            determinations = [
                "QUANTITY_ON_HAND",
                "QUANTITY_ON_ORDER",
                "QUANTITY_ON_PURCHASE_RETURN",
                "QUANTITY_ON_RETURN",
                "QUANTITY_PROMISED",
            ]
            row["item_inventory_qty_avl_on_sale_determination"] = ",".join(
                random.sample(determinations, random.randint(1, len(determinations)))
            )
            row["item_inventory_qty_avl_on_sale"] = random.choice(
                ["UNLIMITED", "QTY_AVAILABLE"]
            )
            row["item_inventory_use_temporary_qa_value"] = "TRUE" if random_bool(0.5) else ""
            row["item_inventory_use_pre_order"] = "TRUE" if random_bool(0.5) else ""

        for attr in custom_attributes:
            row[attr["column_name"]] = _random_value_for_attr(attr)

        for attr in line_custom_attributes:
            row[attr["column_name"]] = _random_value_for_attr(attr)

        data.append(row)

    df = pd.DataFrame(data).fillna("")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"ITEM_DUMMY_DATA_{num_rows}_{timestamp}.csv"
    filepath = f"C:\\Users\\Rahman\\Downloads\\{filename}"
    df.to_csv(filepath, index=False)

    print(f"\nSuccessfully generated {num_rows} items!")
    print(f"File saved to: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Generate item CSV data.")
    parser.add_argument(
        "count",
        type=int,
        nargs="?",
        default=DEFAULT_ITEM_COUNT,
        help=f"Number of items to generate (default: {DEFAULT_ITEM_COUNT})",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Generate multiple files: 200, 300, 400, and 500 items",
    )
    parser.add_argument(
        "--save-config",
        dest="save_config",
        nargs="?",
        const=str(DEFAULT_CONFIG_PATH),
        default=None,
        help=f"Path to save configuration (default {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--load-config",
        dest="load_config",
        type=str,
        default=None,
        help="Path to load configuration (skips prompts)",
    )
    args = parser.parse_args()

    if args.batch:
        counts = [200, 300, 400, 500]
        print("=== BATCH MODE: Generating multiple files ===\n")
        files = []
        for count in counts:
            print(f"\n{'=' * 60}")
            files.append(
                generate_item_data(
                    count,
                    item_types=["STANDARD"],
                    uom_config={"use_uom": False, "uoms": [], "allow_auto": True},
                    group_config={"group_names": [], "assign_count": 0},
                    custom_form_config={"forms": []},
                    custom_attributes=[],
                    sale_currencies=["AUD"],
                    sale_tax_codes=[],
                    sale_accounting_enabled=True,
                    discount_profiles=[],
                    pricing_levels=[],
                    sale_properties_enabled=True,
                    purchase_currencies=["AUD"],
                    purchase_tax_codes=[],
                    purchase_accounting_enabled=True,
                    supplier_config={"use": False, "suppliers": [], "prices": []},
                    inventory_config={"use": False, "warehouses": []},
                    line_custom_attributes=[],
                )
            )
            print(f"{'=' * 60}\n")
        print("\n=== BATCH GENERATION COMPLETE ===")
        for f in files:
            print(f"  - {f}")
        return

    item_count = max(1, args.count)

    if args.load_config:
        try:
            cfg = load_config(args.load_config)
        except OSError as exc:
            print(f"ERROR: Could not load config: {exc}")
            raise SystemExit(1)
        if args.count == DEFAULT_ITEM_COUNT:
            item_count = int(cfg.get("item_count", item_count))
        item_types = cfg.get("item_types", ["STANDARD"])
        uom_config = cfg.get("uom_config", {"use_uom": False})
        group_config = cfg.get("group_config", {"group_names": [], "assign_count": 0})
        custom_form_config = cfg.get("custom_form_config", {"forms": []})
        _, custom_attributes = cfg.get("custom_attribute_count", 0), cfg.get("custom_attributes", [])
        sale_currencies = cfg.get("sale_currencies", ["AUD"])
        sale_tax_codes = cfg.get("sale_tax_codes", [])
        sale_accounting_enabled = cfg.get("sale_accounting_enabled", True)
        discount_profiles = cfg.get("discount_profiles", [])
        pricing_levels = cfg.get("pricing_levels", [])
        sale_properties_enabled = cfg.get("sale_properties_enabled", True)
        purchase_currencies = cfg.get("purchase_currencies", ["AUD"])
        purchase_tax_codes = cfg.get("purchase_tax_codes", [])
        purchase_accounting_enabled = cfg.get("purchase_accounting_enabled", True)
        supplier_config = cfg.get("supplier_config", {"use": False, "suppliers": [], "prices": []})
        inventory_config = cfg.get("inventory_config", {"use": False, "warehouses": []})
        _, line_custom_attributes = cfg.get("line_custom_attribute_count", 0), cfg.get(
            "line_custom_attributes", []
        )
    else:
        item_types = prompt_item_types()
        uom_config = prompt_uom_config()
        group_config = prompt_group_config(item_count)
        custom_form_config = prompt_custom_form_config()
        attr_count, custom_attributes = prompt_custom_attributes("ca_item_attr_")
        line_attr_count, line_custom_attributes = (0, [])

        sale_currencies = prompt_sale_currency_config()
        sale_tax_codes = prompt_tax_config("sale")
        sale_accounting_enabled = prompt_accounting_code_usage("sale")
        discount_profiles = prompt_discount_profile()
        pricing_levels = prompt_pricing_levels()
        sale_properties_enabled = prompt_yes_no(
            "Enable sale properties (fulfillment/billing/payment)?", True
        )

        purchase_currencies = prompt_sale_currency_config()
        purchase_tax_codes = prompt_tax_config("purchase")
        purchase_accounting_enabled = prompt_accounting_code_usage("purchase")

        supplier_config = prompt_supplier_management()
        inventory_config = prompt_inventory_config()

        if args.save_config:
            cfg = {
                "item_count": item_count,
                "item_types": item_types,
                "uom_config": uom_config,
                "group_config": group_config,
                "custom_form_config": custom_form_config,
                "custom_attribute_count": attr_count,
                "custom_attributes": custom_attributes,
                "line_custom_attribute_count": line_attr_count,
                "line_custom_attributes": line_custom_attributes,
                "sale_currencies": sale_currencies,
                "sale_tax_codes": sale_tax_codes,
                "sale_accounting_enabled": sale_accounting_enabled,
                "discount_profiles": discount_profiles,
                "pricing_levels": pricing_levels,
                "sale_properties_enabled": sale_properties_enabled,
                "purchase_currencies": purchase_currencies,
                "purchase_tax_codes": purchase_tax_codes,
                "purchase_accounting_enabled": purchase_accounting_enabled,
                "supplier_config": supplier_config,
                "inventory_config": inventory_config,
            }
            save_config(args.save_config, cfg)

    generate_item_data(
        item_count,
        item_types,
        uom_config,
        group_config,
        custom_form_config,
        custom_attributes,
        sale_currencies,
        sale_tax_codes,
        sale_accounting_enabled,
        discount_profiles,
        pricing_levels,
        sale_properties_enabled,
        purchase_currencies,
        purchase_tax_codes,
        purchase_accounting_enabled,
        supplier_config,
        inventory_config,
        [],
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nItem generation cancelled by user.")
