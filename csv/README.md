# CSV Data Generator Suite

A comprehensive suite of Python scripts for generating realistic dummy CSV data for accounts, orders, invoices, purchase orders, payments, and purchase invoices. Perfect for testing, development, and demonstration purposes.

## Table of Contents

- [Installation](#installation)
- [Command-Line Options](#command-line-options)
- [Output Location](#output-location)
- [Examples](#examples)


## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Navigate to the csv directory**

```bash
cd Scripts/csv
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

This will install:
- `pandas` - Data manipulation and CSV generation
- `Faker` - Realistic dummy data generation

## Command-Line Options

### Common Options (All Generators)

```bash
# Specify record count
python <generator>.py <count>

# Batch mode (200, 300, 400, 500 records)
python <generator>.py --batch

# Save configuration
python <generator>.py <count> --save-config [path]
# Default path if omitted: <generator>_config.json

# Load configuration
python <generator>.py <count> --load-config <path>

# Help
python <generator>.py --help
```

### Examples

```bash
# Generate 150 accounts
python account_csv_generator.py 150

# Generate orders in batch mode
python order_csv_generator.py --batch

# Generate 75 invoices and save config
python invoice_csv_generator.py 75 --save-config my_invoice_config.json

# Generate 500 accounts from saved config
python account_csv_generator.py 500 --load-config my_account_config.json
```

## Configuration Files

Configuration files are JSON formatted and store all interactive settings for reuse.

### Example: Save and Load Configuration

**Save configuration:**
```bash
python account_csv_generator.py 300 --save-config
```

This creates `account_generator_config.json` in the current directory.

**Load configuration:**
```bash
python account_csv_generator.py 300 --load-config account_generator_config.json
```

Or with full path:
```bash
python account_csv_generator.py 300 --load-config C:\Users\{userName}\Scripts\csv\account_generator_config.json
```

### Benefits of Configuration Files

- **Consistency**: Use the same settings across multiple runs
- **Efficiency**: Skip interactive prompts for repeated generations
- **Documentation**: Configuration files serve as documentation of your data structure
- **Version Control**: Track configuration changes over time

### Recommended Default: 10 Custom Attributes

When prompted for custom attributes, choose **10** and use the **default set**:

1. **CA_BOOL** - Boolean (True/False)
2. **CA_CHECKBOX** - Multiple checkboxes (A, B, C, D)
3. **CA_DATE** - Date in YYYY-MM-DD format
4. **CA_DROPDOWN** - Single dropdown selection (A, B, C, D)
5. **CA_DROPDOWN_WITH_MULTISELECT** - Multiple dropdown selections (A, B, C, D)
6. **CA_MONEY** - Currency value (1.00 - 10,000.00)
7. **CA_QUANTITY** - Integer quantity (1-50)
8. **CA_NUMBER** - Integer number (0-1000)
9. **CA_RADIO** - Single radio selection (A, B, C, D)
10. **CA_TEXT** - Text sentence (6 words)

### Recommended Default: 3 warehouses
1. **W-1**
2. **W-2**
3. **W-3**

## Output Location

All generated CSV files are saved to:
```
C:\Users\{userName}\Downloads\
```

### File Naming Convention

Files are timestamped to prevent overwrites:

```
ACCOUNT_DUMMY_DATA_<count>_<timestamp>.csv
ORDER_DUMMY_DATA_<count>_<timestamp>.csv
INVOICE_DUMMY_DATA_<count>_<timestamp>.csv
```

**Examples:**
```
ACCOUNT_DUMMY_DATA_200_2025-12-01_07-12-22.csv
ORDER_DUMMY_DATA_500_2025-12-01_15-30-45.csv
INVOICE_DUMMY_DATA_300_2025-12-01_09-45-10.csv
```

## Examples

### Example 1: Generate Test Accounts (Recommended Workflow)

```bash
python account_csv_generator.py 100
```

**Interactive Prompts:**
```
How many address lines should each account have? (1-5, default 1): 2
How many contacts per account? (1-5, default 5): 3
How many custom attributes do you want to add? (0 for none): 10
Use the default set of 10 custom attributes? (y/N, default n): y
Do you want payment methods? (y/n, default n): n
Do you want tax config/columns? (y/n, default n): n
Do you want account accounting code column? (y/n, default n): n
Do you want account group column? (y/n, default n): n
Do you want account_custom_form column? (y/n, default n): n
Do you want account_user_team column? (y/n, default n): n
Do you also want to generate an order CSV? (y/n, default n): n
```

**Output:** 100 accounts with 2 address lines, 3 contacts each, and 10 default custom attributes.

### Example 2: Generate Purchase Invoices

```bash
python purchase_invoice_csv_generator.py 50
```

**Interactive Prompts:**
```
Enter supplier account IDs (comma-separated): SUP-001,SUP-002,SUP-003
Do you want to use a custom form template? (y/N, default n): n
Do you want tax configuration? (y/N, default n): y
Enter tax UUID (or press Enter to finish): TAX-UUID-001
Add another tax UUID? (y/N, default n): y
Enter tax UUID (or press Enter to finish): TAX-UUID-002
Add another tax UUID? (y/N, default n): n
Do you want purchase invoice custom attributes? (y/N, default n): y
How many purchase invoice custom attributes? (>=1, default 10): 10
Use default 10 purchase invoice custom attributes? (y/N, default n): y
Which items should be generated?
  1) System items only
  2) Line items only
  3) Both (default)
Enter choice (1-3, default 3): 1
Enter system item IDs (comma-separated, e.g., ITEM-1001,ITEM-1002): ITEM-1001,ITEM-1002,ITEM-1003
Maximum items per purchase invoice (default 5): 5
Do you want line item custom attributes? (y/N, default n): y
How many line item custom attributes? (>=1, default 10): 10
Use default 10 line item custom attributes? (y/N, default n): y
```

**Output:** 50 purchase invoices with system items, tax configuration, and 10 default custom attributes.

----

**Version:** 1.0.0

**Last Updated:** December 2025

**Author:** Rahman Mizanur

Made with ❤️ for efficient testing and development
