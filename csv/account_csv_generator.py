import pandas as pd
import random
from datetime import datetime
from faker import Faker
import argparse
import json
from pathlib import Path

import order_csv_generator

fake = Faker('en_AU')
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "account_generator_config.json"

def generate_account_id():
    """Generate unique account ID in format CSV-ACC-XXXXX-CUS or CSV-ACC-XXXXX-SUP"""
    number = random.randint(10000, 99999)
    suffix = random.choice(['CUS', 'SUP'])
    return f"CSV-ACC-{number}-{suffix}"

def generate_company_name():
    """Generate random company name"""
    company_types = ['Pty Ltd', 'Inc', 'Corp', 'Group', 'Solutions', 'Services', 'Technologies', 'Enterprises']
    prefixes = ['Global', 'Prime', 'Elite', 'Summit', 'Apex', 'Vertex', 'Nexus', 'Quantum']
    industries = ['Tech', 'Logistics', 'Financial', 'Consulting', 'Marketing', 'Digital', 'Industrial', 'Trading']

    if random.random() < 0.5:
        return f"{random.choice(prefixes)} {random.choice(industries)} {random.choice(company_types)}"
    else:
        return f"{fake.company()}"

def generate_person_name():
    """Generate random person full name"""
    return fake.name()

def generate_account_name():
    """Generate account name - 60% company, 40% person"""
    if random.random() < 0.6:
        return generate_company_name()
    else:
        return generate_person_name()

def name_to_domain(name, extensions=None):
    """Convert account name to email domain"""
    domain = name.lower()
    domain = domain.replace(' ', '-')
    domain = domain.replace('&', 'and')
    domain = domain.replace(',', '')
    domain = domain.replace("'", '')
    domain = domain.replace('.', '')
    domain = domain.replace('pty-ltd', '')
    domain = domain.replace('inc', '')
    domain = domain.replace('corp', '')
    domain = domain.strip('-')

    if extensions is None:
        extensions = ['.com.au', '.net.au', '.org.au']
    return domain + random.choice(extensions)

def generate_description():
    """Generate business description"""
    descriptions = [
        'Configurable empowering challenge',
        'Right-sized high-level groupware',
        'Innovative scalable solution',
        'Enterprise-grade platform',
        'Customer-focused service excellence',
        'Advanced technology integration',
        'Streamlined business operations',
        'Comprehensive management system',
        'Strategic business solutions',
        'Next-generation digital platform',
        'Robust infrastructure services',
        'Integrated business intelligence',
        'Flexible enterprise architecture',
        'Optimized workflow automation',
        'Cutting-edge innovation hub'
    ]
    return random.choice(descriptions)

def generate_address():
    """Generate Australian street address"""
    unit_types = ['Apt.', 'Unit', 'Suite']
    has_unit = random.random() < 0.6

    if has_unit:
        unit = f"{random.choice(unit_types)} {random.randint(1, 999)}"
        return f"{unit} {fake.street_address()}"
    else:
        return fake.street_address()

def generate_address_line_2():
    """Generate secondary address line (often empty)"""
    if random.random() < 0.5:
        return ''

    options = [
        f"Apt. {random.randint(1, 999)}",
        f"Suite {random.randint(100, 999)}",
        f"Unit {random.randint(1, 99)}",
        f"{random.randint(1, 999)}/"
    ]
    return random.choice(options)

def generate_phone():
    """Generate Australian landline: 0X XXXX XXXX"""
    area_code = f"0{random.randint(2, 8)}"
    part1 = random.randint(1000, 9999)
    part2 = random.randint(1000, 9999)
    return f"{area_code} {part1} {part2}"

def generate_mobile():
    """Generate Australian mobile: 04XX XXX XXX"""
    prefix = f"04{random.randint(0, 99):02d}"
    part1 = random.randint(100, 999)
    part2 = random.randint(100, 999)
    return f"{prefix} {part1} {part2}"

def generate_postcode():
    """Generate 4-digit Australian postcode"""
    return str(random.randint(2000, 9999))

CONTACT_SALUTATIONS = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Master', 'Sir', 'Frau', 'Fraulein']
CONTACT_DESIGNATIONS = [
    'Analyst',
    'Accountant',
    'Integrator',
    'Investor',
    'Partner',
    'Reseller',
    'Supplier',
    'Vendor',
    'Consultant',
    'Developer',
    'Customer Service Manager',
    'Marketing Manager',
    'Sales Manager',
    'CEO',
    'Director',
    'Vice President',
    'Other',
]


def _random_yes_no_blank():
    return random.choice(['YES', 'NO', ''])


def generate_address_extra_lines():
    """Generate additional address lines 3-5 with optional building/area info."""
    line3 = random.choice(
        [
            '',
            'Business Park',
            'Industrial Estate',
            'Corporate Centre',
            'Technology Park',
            'Office Tower',
        ]
    )
    line4 = random.choice(
        [
            '',
            'Level ' + str(random.randint(1, 25)),
            'Building ' + random.choice(['A', 'B', 'C', 'D']),
            'North Wing',
            'South Wing',
        ]
    )
    line5 = random.choice(
        [
            '',
            'CBD',
            'Business District',
            'Commercial Area',
            'City Centre',
        ]
    )
    return line3, line4, line5


def generate_account_address_fields(line_count, country='Australia'):
    """
    Generate base account address data with configurable line count.

    Args:
        line_count: number of address lines to populate (1-5)
        country: fallback country value
    """
    line_count = max(1, min(5, int(line_count or 1)))

    address_line_1 = generate_address()
    address_line_2 = generate_address_line_2()
    address_line_3, address_line_4, address_line_5 = generate_address_extra_lines()
    lines = [
        address_line_1,
        address_line_2,
        address_line_3,
        address_line_4,
        address_line_5,
    ]

    row_fields = {}
    for idx in range(5):
        key = f"address_1_address_line_{idx + 1}"
        row_fields[key] = lines[idx] if idx < line_count else ""

    row_fields["address_1_post_code"] = generate_postcode()
    row_fields["address_1_city"] = fake.city()
    row_fields["address_1_state"] = fake.state()
    row_fields["address_1_country"] = country
    row_fields["address_1_is_default_billing"] = "YES"
    row_fields["address_1_is_default_shipping"] = "YES"
    return row_fields


def generate_contact(index, domain):
    """Generate contact fields for contact_<index>_*."""
    prefix = f"contact_{index}_"

    salutation = random.choice(CONTACT_SALUTATIONS)
    designation = random.choice(CONTACT_DESIGNATIONS)
    first_name = fake.first_name()
    last_name = fake.last_name()
    middle_name = fake.first_name() if random.random() < 0.3 else ''

    local_part = f"{first_name}.{last_name}".lower().replace(' ', '.')
    email_address = f"{local_part}@{domain}"

    address_line_1 = generate_address()
    address_line_2 = generate_address_line_2()
    address_line_3, address_line_4, address_line_5 = generate_address_extra_lines()

    return {
        f"{prefix}salutation": salutation,
        f"{prefix}designation": designation,
        f"{prefix}first_name": first_name,
        f"{prefix}middle_name": middle_name,
        f"{prefix}last_name": last_name,
        f"{prefix}email_address": email_address,
        f"{prefix}email_address_do_not_email": _random_yes_no_blank(),
        f"{prefix}address_line_1": address_line_1,
        f"{prefix}address_line_2": address_line_2,
        f"{prefix}address_line_3": address_line_3,
        f"{prefix}address_line_4": address_line_4,
        f"{prefix}address_line_5": address_line_5,
        f"{prefix}post_code": generate_postcode(),
        f"{prefix}phone": generate_phone(),
        f"{prefix}phone_do_not_call": _random_yes_no_blank(),
        f"{prefix}fax": generate_phone(),
        f"{prefix}fax_do_not_call": _random_yes_no_blank(),
        f"{prefix}mobile": generate_mobile(),
        f"{prefix}mobile_do_not_call": _random_yes_no_blank(),
        f"{prefix}receive_billing_information": _random_yes_no_blank(),
    }


def blank_contact(index):
    """Return empty fields for contact_<index>_*."""
    prefix = f"contact_{index}_"
    fields = [
        'salutation',
        'designation',
        'first_name',
        'middle_name',
        'last_name',
        'email_address',
        'email_address_do_not_email',
        'address_line_1',
        'address_line_2',
        'address_line_3',
        'address_line_4',
        'address_line_5',
        'post_code',
        'phone',
        'phone_do_not_call',
        'fax',
        'fax_do_not_call',
        'mobile',
        'mobile_do_not_call',
        'receive_billing_information',
    ]
    return {f"{prefix}{field}": '' for field in fields}


def get_default_custom_attributes():
    """Return the default set of 10 custom attributes when requested."""
    dropdown_options = ["A", "B", "C", "D"]
    radio_options = [str(i) for i in range(1, 51)]

    def make_attr(name, attr_type, options=None, quantity_min=None, quantity_max=None):
        return {
            "column_name": f"ca_account_attr_{name}",
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
        make_attr("CA_RADIO", "radio", options=radio_options),
        make_attr("CA_TEXT", "text"),
    ]

def prompt_custom_attributes():
    """
    Prompt user for custom attributes to add to each account row.

    Returns:
        List of dicts with keys: column_name, type, constant, value
    """
    while True:
        try:
            count_input = input("How many custom attributes do you want to add? (0 for none): ").strip()
            if count_input == '':
                return []
            count = int(count_input)
            if count < 0:
                print("Please enter 0 or a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid integer.")

    attributes = []
    if count == 0:
        return attributes

    if count == 10:
        default_choice = input(
            "Use the default set of 10 custom attributes? (y/N, default n): "
        ).strip().lower()
        if default_choice in ("y", "yes"):
            return get_default_custom_attributes()

    for i in range(1, count + 1):
        print(f"\nCustom attribute {i}/{count}")

        # Attribute name
        skip_attr = False
        while True:
            name = input("  Enter custom attribute name (e.g., CA_BOOL, or 'skip' to skip this attribute): ").strip()
            if name.lower() == "skip":
                print("  Skipping this custom attribute.")
                skip_attr = True
                break
            if not name:
                print("  Name cannot be empty.")
                continue
            # Normalise name to match header style
            name_normalised = name.replace(' ', '_').upper()
            column_name = f"ca_account_attr_{name_normalised}"
            break

        if skip_attr:
            continue

        # Attribute type
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
                range_raw = input(
                    "  Enter quantity range as min-max (default 1-50): "
                ).strip()
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

        # For dropdown / multiselect / checkboxes / radio, capture options list
        options = []
        if attr_type in ("dropdown", "dropdown_multi", "checkboxes", "radio"):
            raw_opts = input(
                "  Enter options (comma-separated, e.g., A,B,C,D, default A,B,C,D): "
            ).strip()
            if not raw_opts:
                raw_opts = "A,B,C,D"
            options = [o.strip() for o in raw_opts.split(",") if o.strip()]

        # Constant or random
        while True:
            constant_choice = input("  Use the same value for all rows? (y/N, default n): ").strip().lower()
            if constant_choice in ('y', 'n', ''):
                break
            print("  Please enter 'y' or 'n'.")

        is_constant = constant_choice == 'y'
        value = None

        if is_constant:
            raw = input("  Enter the value to use for all rows: ").strip()
            if attr_type == 'bool':
                value = raw.lower() in ('1', 'true', 'yes', 'y')
            elif attr_type in ('number', 'money', 'quantity'):
                try:
                    if '.' in raw:
                        value = float(raw)
                    else:
                        value = int(raw)
                except ValueError:
                    print("  Could not parse number, defaulting to 0.")
                    value = 0
            elif attr_type == 'date':
                # Validate YYYY-MM-DD format
                while True:
                    try:
                        datetime.strptime(raw, "%Y-%m-%d")
                        value = raw
                        break
                    except ValueError:
                        print("  Invalid date format. Use YYYY-MM-DD (e.g., 2025-05-06).")
                        raw = input("  Enter date value (YYYY-MM-DD): ").strip()
            else:
                # string, text, dropdowns, checkboxes: keep as raw string
                value = raw

        attributes.append(
            {
                'column_name': column_name,
                'type': attr_type,
                'constant': is_constant,
                'value': value,
                'options': options,
                'quantity_min': quantity_min,
                'quantity_max': quantity_max,
            }
        )

    return attributes


def prompt_account_address_config():
    """
    Prompt how many address lines should be populated for the primary account address.

    Returns dict with:
        line_count: int
    """
    while True:
        raw = input(
            "How many address lines should each account have? (1-5, default 1): "
        ).strip()
        if raw == '':
            return {"line_count": 1}
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number between 1 and 5.")
            continue
        if 1 <= value <= 5:
            return {"line_count": value}
        print("Please enter a whole number between 1 and 5.")


def prompt_contact_count():
    """Prompt user for how many contacts (1-5) per account."""
    while True:
        raw = input("How many contacts per account? (1-5, default 5): ").strip()
        if raw == '':
            return 5
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a number between 1 and 5.")
            continue
        if 1 <= value <= 5:
            return value
        print("Please enter a number between 1 and 5.")


def prompt_payment_methods():
    """
    Prompt user for payment method configuration.

    Returns dict with:
        dd_count: int
        ot_count: int
        dd_processor: str
        ot_processor: str
        ot_processors: list[str]
    """
    use_pm = input("Do you want payment methods? (y/n, default n): ").strip().lower()
    if use_pm not in ("y", "yes"):
        return {
            "dd_count": 0,
            "ot_count": 0,
            "dd_processor": "",
            "ot_processor": "",
            "ot_processors": [],
        }

    # Choose types
    while True:
        print(
            "Which payment methods?\n"
            "  1) DIRECT_DEBIT (dd)\n"
            "  2) OTHER (ot)\n"
            "  3) Both (dd + ot)"
        )
        raw_pm = input("Enter choice (1-3): ").strip().lower()
        if raw_pm == "":
            pm_type = "both"
        elif raw_pm in ("1", "dd", "direct_debit"):
            pm_type = "dd"
        elif raw_pm in ("2", "ot", "other"):
            pm_type = "ot"
        elif raw_pm in ("3", "both"):
            pm_type = "both"
        else:
            print("Please enter 1, 2, 3, or dd/ot/both.")
            continue
        break

    dd_count = 0
    ot_count = 0
    dd_processor = ""
    ot_processor = ""

    if pm_type in ("dd", "both"):
        while True:
            raw = input(
                "How many DIRECT_DEBIT methods per account? (>=1, default 1): "
            ).strip()
            if raw == "":
                dd_count = 1
                break
            try:
                val = int(raw)
            except ValueError:
                print("Please enter a whole number 1 or greater.")
                continue
            if val >= 1:
                dd_count = val
                break
            print("Please enter a whole number 1 or greater.")

        if dd_count > 1:
            dd_processor = input(
                "Enter DIRECT_DEBIT processor(s) (use uuid, comma-separated for multiple): "
            ).strip()
        else:
            dd_processor = input(
                "Enter DIRECT_DEBIT processor (use uuid): "
            ).strip()

    if pm_type in ("ot", "both"):
        while True:
            raw = input(
                "How many OTHER methods per account? (>=1, default 1): "
            ).strip()
            if raw == "":
                ot_count = 1
                break
            try:
                val = int(raw)
            except ValueError:
                print("Please enter a whole number 1 or greater.")
                continue
            if val >= 1:
                ot_count = val
                break
            print("Please enter a whole number 1 or greater.")

        # Require at least one processor UUID
        while True:
            if ot_count > 1:
                ot_processor_raw = input(
                    "Enter OTHER processor(s) (use uuid, comma-separated for multiple): "
                ).strip()
            else:
                ot_processor_raw = input(
                    "Enter OTHER processor (use uuid): "
                ).strip()
            if ot_processor_raw:
                ot_processors = [p.strip() for p in ot_processor_raw.split(",") if p.strip()]
                if ot_processors:
                    break
            print("Please enter at least one valid processor uuid.")
        ot_processor = ot_processors[0] if ot_processors else ""

    return {
        "dd_count": dd_count,
        "ot_count": ot_count,
        "dd_processor": dd_processor,
        "ot_processor": ot_processor,
        "ot_processors": ot_processors,
    }


def prompt_tax_config():
    """
    Prompt user for tax configuration.

    Returns dict with:
        tax_codes: list[str]
    """
    use_tax = input("Do you want tax config/columns? (y/n, default n): ").strip().lower()
    if use_tax not in ("y", "yes"):
        return {"tax_codes": []}

    raw = input(
        "Enter account tax code(s) (use uuid, comma-separated for multiple): "
    ).strip()
    if not raw:
        return {"tax_codes": []}

    tax_codes = [code.strip() for code in raw.split(",") if code.strip()]
    return {"tax_codes": tax_codes}


def prompt_accounting_config():
    """
    Prompt user for account accounting code configuration.

    Returns dict with:
        use_accounting_code: bool
    """
    use_acct = input("Do you want account accounting code column? (y/n, default n): ").strip().lower()
    return {"use_accounting_code": use_acct in ("y", "yes")}


def prompt_account_custom_form_config(total_accounts):
    """
    Prompt user for account_custom_form configuration.

    Returns dict with:
        form_names: list[str]
        assign_percent: float (0-100)
    """
    use_form = input("Do you want account_custom_form column? (y/n, default n): ").strip().lower()
    if use_form not in ("y", "yes"):
        return {"form_names": [], "assign_percent": 0.0}

    while True:
        raw_names = input(
            "Enter custom form name(s) (comma-separated, e.g., Account_Custom_Form_1,Account_Custom_Form_2): "
        ).strip()
        form_names = [g.strip() for g in raw_names.split(",") if g.strip()]
        if form_names:
            break
        print("Please enter at least one form name.")

    # Default ~3% of accounts get a custom form (e.g., 3 of 100)
    default_percent = 3.0
    while True:
        raw = input(
            f"What percentage of accounts should have a custom form? (0-100, default {default_percent}%): "
        ).strip()
        if raw == "":
            assign_percent = default_percent
            break
        try:
            val = float(raw)
        except ValueError:
            print("Please enter a valid number between 0 and 100.")
            continue
        if 0.0 <= val <= 100.0:
            assign_percent = val
            break
        print("Please enter a value between 0 and 100.")

    return {"form_names": form_names, "assign_percent": assign_percent}


def prompt_account_user_team_config():
    """
    Prompt user for account_user_team configuration.

    Returns dict with:
        team_names: list[str]
    """
    use_team = input("Do you want account_user_team column? (y/n, default n): ").strip().lower()
    if use_team not in ("y", "yes"):
        return {"team_names": []}

    while True:
        raw_names = input(
            "Enter account user team name(s) (comma-separated, e.g., TeamA,TeamB): "
        ).strip()
        team_names = [g.strip() for g in raw_names.split(",") if g.strip()]
        if team_names:
            break
        print("Please enter at least one team name.")

    return {"team_names": team_names}


def prompt_order_generation_config(default_order_count):
    """
    Prompt whether to generate an order CSV and how many records.

    Args:
        default_order_count: suggested order count
    """
    raw = input("Do you also want to generate an order CSV? (y/n, default n): ").strip().lower()
    if raw not in ("y", "yes"):
        return {"generate_orders": False, "order_count": 0}

    while True:
        raw_count = input(
            f"How many orders should be generated? (>=1, default {default_order_count}): "
        ).strip()
        if raw_count == "":
            return {"generate_orders": True, "order_count": max(1, int(default_order_count))}
        try:
            value = int(raw_count)
        except ValueError:
            print("Please enter a whole number 1 or greater.")
            continue
        if value >= 1:
            return {"generate_orders": True, "order_count": value}
        print("Please enter a whole number 1 or greater.")


def prompt_account_group_config(total_accounts):
    """
    Prompt user for account group configuration.

    Returns dict with:
        group_names: list[str]
        assign_count: int
    """
    use_group = input("Do you want account group column? (y/n, default n): ").strip().lower()
    if use_group not in ("y", "yes"):
        return {"group_names": [], "assign_count": 0}

    while True:
        raw_names = input(
            "Enter account group name(s) (comma-separated, e.g., GroupA,GroupB): "
        ).strip()
        group_names = [g.strip() for g in raw_names.split(",") if g.strip()]
        if group_names:
            break
        print("Please enter at least one group name.")

    # By default, assign a small portion of accounts (about 5%).
    default_assign = max(1, total_accounts // 20)
    default_percent = round(100 * default_assign / total_accounts, 1) if total_accounts else 0.0
    while True:
        raw = input(
            f"How many accounts should have a group? (0-{total_accounts}, default {default_assign} ≈ {default_percent}%): "
        ).strip()
        if raw == "":
            assign_count = default_assign
            break
        try:
            val = int(raw)
        except ValueError:
            print("Please enter a valid integer.")
            continue
        if 0 <= val <= total_accounts:
            assign_count = val
            break
        print(f"Please enter a number between 0 and {total_accounts}.")

    return {"group_names": group_names, "assign_count": assign_count}


def save_generation_config(path, config):
    """Save generation configuration (contacts, custom attributes, payment, tax, etc.) to JSON."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {path}")
    except OSError as exc:
        print(f"WARNING: Could not save configuration to {path}: {exc}")


def load_generation_config(path):
    """Load generation configuration from JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_account_data(num_rows=100, custom_attributes=None, contact_count=5, account_address_config=None, payment_config=None, tax_config=None, accounting_config=None, group_config=None, custom_form_config=None, user_team_config=None, order_config=None):
    """
    Generate random account data CSV file

    Args:
        num_rows: Number of rows to generate (default 100)
    """
    print(f"Generating {num_rows} account records...")

    # Track unique values
    used_account_ids = set()
    used_account_names = set()

    if custom_attributes is None:
        custom_attributes = []

    # Ensure contact_count is between 1 and 5
    contact_count = max(1, min(5, int(contact_count)))

    # Address configuration (number of lines populated)
    if account_address_config is None:
        account_address_config = {"line_count": 1}
    try:
        address_line_count = int(account_address_config.get("line_count", 1))
    except (TypeError, ValueError):
        address_line_count = 1
    address_line_count = max(1, min(5, address_line_count))

    # Default payment configuration (no methods) if not provided
    if payment_config is None:
        payment_config = {
            "dd_count": 0,
            "ot_count": 0,
            "dd_processor": "",
            "ot_processor": "",
            "ot_processors": [],
        }

    # Allow any non-negative numbers of payment methods (no upper bound)
    dd_count = max(0, int(payment_config.get("dd_count", 0)))
    ot_count = max(0, int(payment_config.get("ot_count", 0)))
    dd_processor = payment_config.get("dd_processor", "")
    ot_processor = payment_config.get("ot_processor", "")
    ot_processors = payment_config.get("ot_processors", [])

    # Tax configuration
    if tax_config is None:
        tax_config = {"tax_codes": []}
    tax_codes = tax_config.get("tax_codes", [])

    # Accounting code configuration
    if accounting_config is None:
        accounting_config = {"use_accounting_code": False}
    use_accounting_code = bool(accounting_config.get("use_accounting_code"))

    # Account group configuration
    if group_config is None:
        group_config = {"group_names": [], "assign_count": 0}
    group_names = group_config.get("group_names", [])
    assign_count = int(group_config.get("assign_count", 0))
    assign_count = max(0, min(num_rows, assign_count))
    if group_names and assign_count > 0:
        group_indices = set(random.sample(range(num_rows), assign_count))
    else:
        group_indices = set()

    # Account custom form configuration
    if custom_form_config is None:
        custom_form_config = {"form_names": [], "assign_percent": 0.0}
    form_names = custom_form_config.get("form_names", [])
    assign_percent = float(custom_form_config.get("assign_percent", 0.0))
    if form_names and assign_percent > 0.0:
        form_count = max(1, int(num_rows * assign_percent / 100.0))
        form_count = min(num_rows, form_count)
        custom_form_indices = set(random.sample(range(num_rows), form_count))
    else:
        custom_form_indices = set()

    # Account user team configuration
    if user_team_config is None:
        user_team_config = {"team_names": []}
    team_names = user_team_config.get("team_names", [])

    # Order generation configuration
    if order_config is None:
        order_config = {"generate_orders": False, "order_count": 0}
    generate_orders = bool(order_config.get("generate_orders"))
    if generate_orders:
        try:
            order_count = int(order_config.get("order_count", num_rows))
        except (TypeError, ValueError):
            order_count = num_rows
        order_count = max(1, order_count)
    else:
        order_count = 0

    data = []

    for i in range(num_rows):
        # Generate unique account_id
        while True:
            account_id = generate_account_id()
            if account_id not in used_account_ids:
                used_account_ids.add(account_id)
                break

        # Generate unique account_name
        while True:
            account_name = generate_account_name()
            if account_name not in used_account_names:
                used_account_names.add(account_name)
                break

        # Generate domain from account name
        domain = name_to_domain(account_name)
        website_domain = name_to_domain(account_name, extensions=['.com'])

        # Account-level fixed fields
        account_type = random.choice(['CUSTOMER', 'SUPPLIER', 'CUSTOMER_AND_SUPPLIER'])
        account_currency = random.choice(['AUD', 'USD'])
        account_time_zone = random.choice(
            [
                'Australia/Melbourne',
                'Africa/Abidjan',
                'America/Costa Rica',
                'America/Dawson',
                'Europe/Warsaw',
                'Europe/Rome',
                'Asia/Kuwait',
                'Asia/Kuala Lumpur',
            ]
        )
        account_invoice_mode = random.choice(['AUTOMATIC', 'MANUAL'])

        # 1–4 communication channels, joined by comma (e.g. EMAIL,POSTAL_EMAIL)
        comm_channels = ['EMAIL', 'POSTAL_EMAIL', 'TEXT_MESSAGE', 'VOICE_MAIL']
        comm_count = random.randint(1, len(comm_channels))
        account_communication_preference = ",".join(
            random.sample(comm_channels, k=comm_count)
        )

        account_consolidate_invoice = random.choice(['YES', 'NO'])
        account_payment_mode = random.choice(['AUTOMATIC', 'MANUAL'])

        billing_start_options = [
            'DAY_OF_MONTH',
            'RATING_START_DATE',
            'SUBSCRIPTION_START_DATE',
            'SUBSCRIPTION_ACTIVATION_DATE',
            'SUBSCRIPTION_ACCEPTANCE_DATE',
        ]
        account_billing_start_date = random.choice(billing_start_options)

        account_billing_start_day_of_month = ''
        if account_billing_start_date == 'DAY_OF_MONTH':
            day_choice = random.choice(list(range(1, 31)) + ['END'])
            if day_choice == 'END':
                account_billing_start_day_of_month = 'End of the Month'
            else:
                suffix = 'th'
                if day_choice in (1, 21):
                    suffix = 'st'
                elif day_choice in (2, 22):
                    suffix = 'nd'
                elif day_choice in (3, 23):
                    suffix = 'rd'
                account_billing_start_day_of_month = f"{day_choice}{suffix} of The Month"

        account_payment_term = random.choice(
            [
                'Due on Receipt',
                'Net 7',
                'Net 14',
                'Net 15',
                'Net 21',
                'Net 30',
                'Net 60',
                'Net 90',
            ]
        )

        account_invoice_term = random.choice(
            [
                'Billing Start Date',
                'Net 7',
                'Net 14',
                'Net 15',
                'Net 21',
                'Net 30',
                'Net 60',
                'Net 90',
            ]
        )

        # Billing period: mix of days, weeks, months, years
        billing_period_choices = ['1 Day', '1 Week']
        billing_period_choices += [f"{m} Month" for m in range(1, 13)]
        billing_period_choices += [f"{y} Year" for y in range(1, 11)]
        account_billing_period = random.choice(billing_period_choices)

        # Social links
        profile_slug = (
            account_name.lower()
            .replace(' ', '')
            .replace('&', 'and')
            .replace(',', '')
        )
        account_linkedin = f"https://www.linkedin.com/in/{profile_slug}"
        account_twitter = f"https://x.com/{profile_slug}"
        account_facebook = f"https://www.facebook.com/{profile_slug}"

        # Tax code per account (if configured)
        if tax_codes:
            account_tax_code = random.choice(tax_codes)
        else:
            account_tax_code = ""

        # Create row data
        row = {
            'account_status': 'ACTIVE',
            'account_id': account_id,
            'account_name': account_name,
            'account_display_name': account_name,
            'account_type': account_type,
            'account_description': generate_description(),
            'account_origin': '',
            'account_email_address': f"info@{domain}",
            'account_currency': account_currency,
            'account_time_zone': account_time_zone,
            'account_website': f"https://{website_domain}",
            'account_tax': '',
            'account_tax_code': account_tax_code,
            'account_tax_rate': '',
            'account_invoice_mode': account_invoice_mode,
            'account_communication_preference': account_communication_preference,
            'account_linkedin': account_linkedin,
            'account_twitter': account_twitter,
            'account_facebook': account_facebook,
            'account_consolidate_invoice': account_consolidate_invoice,
            'account_payment_mode': account_payment_mode,
            'account_billing_start_date': account_billing_start_date,
            'account_billing_start_day_of_month': account_billing_start_day_of_month,
            'account_payment_term': account_payment_term,
            'account_invoice_term': account_invoice_term,
            'account_billing_period': account_billing_period,
        }

        # Add primary account address fields
        row.update(generate_account_address_fields(address_line_count))

        # Add contacts up to requested count only
        for idx in range(1, contact_count + 1):
            row.update(generate_contact(idx, domain))

        # Add accounting code if configured
        if use_accounting_code:
            accounting_codes = [
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
            # Randomly decide whether this row gets a code (e.g., ~70% of rows)
            if random.random() < 0.7:
                row["account_accounting_code"] = random.choice(accounting_codes)

        # Add DIRECT_DEBIT payment methods
        for idx in range(1, dd_count + 1):
            prefix = f"payment_method_dd_{idx}_"
            is_default = 'YES' if idx == 1 else 'NO'
            row[prefix + "processor_type"] = "DIRECT_DEBIT"
            row[prefix + "is_default"] = is_default
            row[prefix + "bsb_number"] = f"{random.randint(100000, 999999)}"
            row[prefix + "account_name"] = account_name
            row[prefix + "account_number"] = f"{random.randint(100000000, 999999999)}"
            row[prefix + "processor"] = dd_processor
            row[prefix + "reference"] = f"{account_id}-DD{idx}"

        # Add OTHER payment methods
        for idx in range(1, ot_count + 1):
            prefix = f"payment_method_ot_{idx}_"
            is_default = 'YES' if idx == 1 else 'NO'
            row[prefix + "processor_type"] = "OTHER"
            row[prefix + "is_default"] = is_default
            # Choose processor: specific list if provided, else single value
            if ot_processors:
                if idx <= len(ot_processors):
                    proc = ot_processors[idx - 1]
                else:
                    proc = ot_processors[-1]
            else:
                proc = ot_processor
            row[prefix + "processor"] = proc
            row[prefix + "reference"] = f"{account_id}-OT{idx}"

        # Assign account group if configured for this row
        if group_names and i in group_indices:
            row["account_group"] = random.choice(group_names)

        # Assign account_custom_form if configured for this row
        if form_names and i in custom_form_indices:
            row["account_custom_form"] = random.choice(form_names)

        # Assign account_user_team if configured (each account gets one team)
        if team_names:
            row["account_user_team"] = random.choice(team_names)

        # Apply custom attributes
        for attr in custom_attributes:
            attr_type = attr['type']
            options = attr.get('options') or []
            if attr['constant']:
                value = attr['value']
            else:
                if attr_type == 'bool':
                    value = random.choice([True, False])
                elif attr_type == 'quantity':
                    qmin = attr.get('quantity_min')
                    qmax = attr.get('quantity_max')
                    if qmin is None or qmax is None:
                        qmin, qmax = 1, 50
                    qmin = int(qmin)
                    qmax = int(qmax)
                    if qmin > qmax:
                        qmin, qmax = qmax, qmin
                    value = random.randint(qmin, qmax)
                elif attr_type == 'number':
                    value = random.randint(0, 1000)
                elif attr_type == 'money':
                    value = round(random.uniform(1, 10000), 2)
                elif attr_type == 'date':
                    # Random date in current year.
                    # If <=30 rows: current month only; else previous months too.
                    today = datetime.now()
                    year = today.year
                    if num_rows <= 30 or today.month == 1:
                        month = today.month
                    else:
                        month = random.randint(1, today.month)
                    import calendar
                    days_in_month = calendar.monthrange(year, month)[1]
                    day = random.randint(1, days_in_month)
                    value = datetime(year, month, day).strftime("%Y-%m-%d")
                elif attr_type == 'text':
                    value = fake.sentence(nb_words=10)
                elif attr_type == 'dropdown':
                    value = random.choice(options) if options else ''
                elif attr_type == 'dropdown_multi':
                    if options:
                        k = random.randint(1, len(options))
                        chosen = random.sample(options, k=k)
                        value = ",".join(chosen)
                    else:
                        value = ''
                elif attr_type == 'checkboxes':
                    if options:
                        k = random.randint(1, len(options))
                        chosen = random.sample(options, k=k)
                        value = ",".join(chosen)
                    else:
                        value = ''
                elif attr_type == 'radio':
                    # Single-select, like dropdown
                    value = random.choice(options) if options else ''
                else:
                    # string or any unknown type
                    value = fake.word()

            row[attr['column_name']] = value

        data.append(row)

        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1}/{num_rows} records...")

    # Create DataFrame and normalise empties
    df = pd.DataFrame(data).fillna("")

    # Reorder columns: account info -> account group -> custom attributes -> addresses -> payment methods -> contacts -> others
    all_cols = list(df.columns)

    account_group_cols = [c for c in all_cols if c == "account_group"]
    account_info_cols = [
        c
        for c in all_cols
        if c.startswith("account_") and c not in account_group_cols
    ]
    custom_attr_cols = [c for c in all_cols if c.startswith("ca_account_attr_")]
    address_cols = [c for c in all_cols if c.startswith("address_")]
    payment_cols = [c for c in all_cols if c.startswith("payment_method_")]
    contact_cols = [
        c for c in all_cols if c.startswith("contact_") or c.startswith("ca_contact_")
    ]

    classified = set(
        account_info_cols
        + account_group_cols
        + custom_attr_cols
        + address_cols
        + payment_cols
        + contact_cols
    )
    other_cols = [c for c in all_cols if c not in classified]

    ordered_cols = (
        account_info_cols
        + account_group_cols
        + custom_attr_cols
        + address_cols
        + payment_cols
        + contact_cols
        + other_cols
    )
    df = df[ordered_cols]

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"ACCOUNT_DUMMY_DATA_{num_rows}_{timestamp}.csv"
    filepath = f"C:\\Users\\Rahman\\Downloads\\{filename}"

    # Save to CSV
    df.to_csv(filepath, index=False)

    print(f"\nSuccessfully generated {num_rows} accounts!")
    print(f"File saved to: {filepath}")
    print(f"\nSample data:")
    print(f"  First Account ID: {data[0]['account_id']}")
    print(f"  First Account Name: {data[0]['account_name']}")
    print(f"  All IDs unique: {len(used_account_ids) == num_rows}")
    print(f"  All names unique: {len(used_account_names) == num_rows}")

    if generate_orders:
        print("\nOrder CSV setup requested - generating order file...")
        order_filepath = order_csv_generator.generate_order_csv(
            order_count,
            account_rows=data,
            custom_attributes=order_csv_generator.get_default_order_custom_attributes(),
            item_config=order_csv_generator.default_item_config(),
            line_item_custom_attributes=order_csv_generator.get_default_line_item_custom_attributes(),
        )
        print(f"Order file saved to: {order_filepath}")

    return filepath

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate random account data CSV files')
    parser.add_argument('count', type=int, nargs='?', default=200,
                        help='Number of accounts to generate (default: 200)')
    parser.add_argument('--batch', action='store_true',
                        help='Generate multiple files: 200, 300, 400, and 500 accounts')
    parser.add_argument(
        '--save-config',
        dest='save_config',
        nargs='?',
        const=str(DEFAULT_CONFIG_PATH),
        default=None,
        help=f'Path to save the interactive generation configuration as JSON (default if omitted: {DEFAULT_CONFIG_PATH})',
    )
    parser.add_argument('--load-config', dest='load_config', type=str, default=None,
                        help='Path to load generation configuration from JSON (skips interactive prompts)')

    args = parser.parse_args()

    if args.batch:
        print("=== BATCH MODE: Generating multiple files ===\n")
        counts = [200, 300, 400, 500]
        files = []

        # In batch mode we skip interactive prompts and use defaults
        for count in counts:
            print(f"\n{'='*60}")
            filepath = generate_account_data(count, custom_attributes=[], contact_count=5)
            files.append(filepath)
            print(f"{'='*60}\n")

        print("\n=== BATCH GENERATION COMPLETE ===")
        print(f"Generated {len(files)} files:")
        for f in files:
            print(f"  - {f}")
    else:
        # Single file generation
        if args.load_config:
            # Load config from JSON and reuse it (no interactive prompts)
            try:
                cfg = load_generation_config(args.load_config)
            except OSError as exc:
                print(f"ERROR: Could not load config from {args.load_config}: {exc}")
                raise SystemExit(1)

            contact_count = int(cfg.get("contact_count", 5))
            custom_attrs = cfg.get("custom_attributes", [])
            account_address_cfg = cfg.get("account_address_config", None)
            # Backward compatibility: older configs may not have address settings
            if account_address_cfg is None:
                account_address_cfg = prompt_account_address_config()
            payment_cfg = cfg.get("payment_config", None)
            tax_cfg = cfg.get("tax_config", None)
            accounting_cfg = cfg.get("accounting_config", None)
            group_cfg = cfg.get("group_config", None)
            custom_form_cfg = cfg.get("custom_form_config", None)
            user_team_cfg = cfg.get("user_team_config", None)
            order_cfg = cfg.get("order_config", None)

            generate_account_data(
                args.count,
                custom_attributes=custom_attrs,
                contact_count=contact_count,
                account_address_config=account_address_cfg,
                payment_config=payment_cfg,
                tax_config=tax_cfg,
                accounting_config=accounting_cfg,
                group_config=group_cfg,
                custom_form_config=custom_form_cfg,
                user_team_config=user_team_cfg,
                order_config=order_cfg,
            )
        else:
            # Interactive prompts, with optional config saving
            print("Account address setup:")
            account_address_cfg = prompt_account_address_config()
            print("Contact setup:")
            contact_count = prompt_contact_count()
            print("Custom attribute setup:")
            custom_attrs = prompt_custom_attributes()
            print("Payment method setup:")
            payment_cfg = prompt_payment_methods()
            print("Tax setup:")
            tax_cfg = prompt_tax_config()
            print("Accounting code setup:")
            accounting_cfg = prompt_accounting_config()
            print("Account group setup:")
            group_cfg = prompt_account_group_config(args.count)
            print("Account custom form setup:")
            custom_form_cfg = prompt_account_custom_form_config(args.count)
            print("Account user team setup:")
            user_team_cfg = prompt_account_user_team_config()
            print("Order setup:")
            order_cfg = prompt_order_generation_config(args.count)

            # Optionally save configuration
            if args.save_config:
                cfg = {
                    "contact_count": contact_count,
                    "custom_attributes": custom_attrs,
                    "account_address_config": account_address_cfg,
                    "payment_config": payment_cfg,
                    "tax_config": tax_cfg,
                    "accounting_config": accounting_cfg,
                    "group_config": group_cfg,
                    "custom_form_config": custom_form_cfg,
                    "user_team_config": user_team_cfg,
                    "order_config": order_cfg,
                }
                save_generation_config(args.save_config, cfg)

            generate_account_data(
                args.count,
                custom_attributes=custom_attrs,
                contact_count=contact_count,
                account_address_config=account_address_cfg,
                payment_config=payment_cfg,
                tax_config=tax_cfg,
                accounting_config=accounting_cfg,
                group_config=group_cfg,
                custom_form_config=custom_form_cfg,
                user_team_config=user_team_cfg,
                order_config=order_cfg,
            )
