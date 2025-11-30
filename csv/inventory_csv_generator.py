import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import argparse
import json
from pathlib import Path

fake = Faker('en_AU')
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "inventory_generator_config.json"

def save_generation_config(path, config):
    """Save generation configuration to JSON."""
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

def generate_inventory_data(num_rows=200):
    """
    Generate random inventory data CSV file

    Args:
        num_rows: Number of rows to generate (default 200)
    """
    print(f"Generating {num_rows} inventory records...")

    data = []

    for i in range(num_rows):
        # Create row data with empty values for now
        row = {
            'inventory_item_uuid': '',
            'inventory_item_warehouse': '',
            'inventory_quantity': '',
            'inventory_accounting_code': '',
            'inventory_expiry_date': '',
        }

        data.append(row)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"INVENTORY_DUMMY_DATA_{num_rows}_{timestamp}.csv"
    filepath = f"C:\\Users\\Rahman\\Downloads\\{filename}"

    # Save to CSV
    df.to_csv(filepath, index=False)

    print(f"\nSuccessfully generated {num_rows} inventory records with headers!")
    print(f"File saved to: {filepath}")

    return filepath

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Generate random inventory data CSV files')
        parser.add_argument('count', type=int, nargs='?', default=200,
                            help='Number of inventory records to generate (default: 200)')
        parser.add_argument('--batch', action='store_true',
                            help='Generate multiple files: 200, 300, 400, and 500 records')
        parser.add_argument(
            '--save-config',
            dest='save_config',
            nargs='?',
            const=str(DEFAULT_CONFIG_PATH),
            default=None,
            help=f'Path to save the generation configuration as JSON (default if omitted: {DEFAULT_CONFIG_PATH})',
        )
        parser.add_argument('--load-config', dest='load_config', type=str, default=None,
                            help='Path to load generation configuration from JSON')

        args = parser.parse_args()

        if args.batch:
            print("=== BATCH MODE: Generating multiple files ===\n")
            counts = [200, 300, 400, 500]
            files = []

            for count in counts:
                print(f"\n{'='*60}")
                filepath = generate_inventory_data(count)
                files.append(filepath)
                print(f"{'='*60}\n")

            print("\n=== BATCH GENERATION COMPLETE ===")
            print(f"Generated {len(files)} files:")
            for f in files:
                print(f"  - {f}")
        else:
            if args.load_config:
                try:
                    cfg = load_generation_config(args.load_config)
                except OSError as exc:
                    print(f"ERROR: Could not load config from {args.load_config}: {exc}")
                    raise SystemExit(1)

                # Load configuration (for future expansion)
                # Currently minimal config, but structure is in place
                row_count = int(cfg.get("row_count", args.count))

                generate_inventory_data(row_count)
            else:
                # For now, no interactive prompts needed, but structure is ready
                if args.save_config:
                    cfg = {
                        "row_count": args.count,
                    }
                    save_generation_config(args.save_config, cfg)

                generate_inventory_data(args.count)
    except KeyboardInterrupt:
        print("\nInventory generation cancelled by user.")
