# DM ERPNext Utilities

Utilities for ERPNext management and customization.

## Features

### 1. Delete Accounts Recursively

Deletes an account and all its child accounts recursively, with transaction verification.

**Command:**
```bash
bench --site erpnext.example.com delete-account-recursive "ACCOUNT NAME" "COMPANY" [--dry-run]
```

**Examples:**
```bash
# Simulation (does not delete)
bench --site erpnext.example.com delete-account-recursive "CUSTOS DE PRODUÇÃO - D-CASA" "DM-CASA" --dry-run

# Real execution
bench --site erpnext.example.com delete-account-recursive "CUSTOS DE PRODUÇÃO - D-CASA" "DM-CASA"
```

**Features:**
- ✅ Recursive search of all child accounts
- ✅ Transaction verification (GL Entry, Journal Entry, Payment Entry)
- ✅ Dry-run mode for safe simulation
- ✅ Deletion in correct order (leaves → root)

### 2. Import Chart of Accounts from CSV

Imports chart of accounts from one or more CSV files in hierarchical order.

**Command:**
```bash
bench --site erpnext.example.com import-chart-of-accounts [files...] "COMPANY" [options]
```

**Options:**
- `--skip-root`: Skips root accounts (already exist from company creation)
- `--reset`: Deletes existing accounts before importing (except root)

**Examples:**
```bash
# Import multiple levels (skipping root)
bench --site erpnext.example.com import-chart-of-accounts \
    nivel2.csv nivel3.csv nivel4.csv "DM-CASA" --skip-root

# Reset and import everything
bench --site erpnext.example.com import-chart-of-accounts \
    *.csv "DM-CASA" --reset --skip-root

# Import only one file
bench --site erpnext.example.com import-chart-of-accounts \
    /path/to/plano_contas.csv "DM-CASA"
```

**Expected CSV Format:**
```csv
Account Name,Parent Account,Account Type,Account Number,Company
Ativo Circulante,ATIVO - D-CASA,Current Asset,,DM-CASA
Caixa e Equivalentes,Ativo Circulante,Cash,,DM-CASA
```

**Fields:**
- `Account Name`: Account name (required)
- `Parent Account`: Parent account (empty for root accounts)
- `Account Type`: Account type (Asset, Liability, Income, Expense, etc.)
- `Account Number`: Account number (optional)
- `Company`: Company name (required)

**Features:**
- ✅ Hierarchical import of multiple files
- ✅ Parent account validation
- ✅ Reset option for re-import
- ✅ Skip root accounts
- ✅ Detailed import report

## Installation in Docker Container

### Via Docker Exec (Installation in Existing Container)

```bash
# 1. Copy the app into the container
docker cp apps/dm_erpnext_utilities erpnext_backend:/home/frappe/frappe-bench/apps/

# 2. Install the app in bench
docker exec erpnext_backend bash -c "
    cd /home/frappe/frappe-bench
    bench get-app dm_erpnext_utilities --skip-assets
    bench --site erpnext.example.com install-app dm_erpnext_utilities
"

# 3. Restart the container
docker restart erpnext_backend
```

### Verify Installation

```bash
# Check if the app is installed
docker exec erpnext_backend bash -c "
    cd /home/frappe/frappe-bench
    bench --site erpnext.example.com list-apps
"

# Test commands
docker exec erpnext_backend bash -c "
    cd /home/frappe/frappe-bench
    bench --help | grep delete-account
"
```

## Usage in Docker

Since the app is installed in the container, all commands must be executed via `docker exec`:

```bash
# General format
docker exec erpnext_backend bash -c "
    cd /home/frappe/frappe-bench
    bench --site erpnext.example.com [command] [arguments]
"

# Practical examples

# 1. Delete account (dry-run)
docker exec erpnext_backend bash -c "
    cd /home/frappe/frappe-bench
    bench --site erpnext.example.com delete-account-recursive \
        'CUSTOS DE PRODUÇÃO - D-CASA' 'DM-CASA' --dry-run
"

# 2. Import chart of accounts
docker exec erpnext_backend bash -c "
    cd /home/frappe/frappe-bench/sites/erpnext.example.com
    bench --site erpnext.example.com import-chart-of-accounts \
        plano_de_contas_nivel_*.csv 'DM-CASA' --skip-root
"
```

### Create Aliases for Convenience

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Alias for bench in container
alias bench-dmla='docker exec erpnext_backend bash -c "cd /home/frappe/frappe-bench && bench --site erpnext.example.com"'

# Usage:
# bench-dmla delete-account-recursive "ACCOUNT" "COMPANY" --dry-run
# bench-dmla import-chart-of-accounts *.csv "COMPANY"
```

## Project Structure

```
dm_erpnext_utilities/
├── dm_erpnext_utilities/
│   ├── __init__.py
│   ├── hooks.py                    # App configuration and command registration
│   └── commands/
│       ├── __init__.py             # CLI command registration
│       ├── account_manager.py      # Account deletion functions
│       └── account_importer.py     # CSV import functions
├── pyproject.toml                  # Project metadata
└── README.md                       # This file
```

## Development

To add new commands:

1. Create the function in a module within `dm_erpnext_utilities/commands/`
2. Register the command in `dm_erpnext_utilities/commands/__init__.py`
3. Test in container

```python
# Example of new command
@click.command('my-command')
@click.argument('arg1')
@pass_context
def my_command(context, arg1):
    """Command description."""
    import frappe
    frappe.init(site=context.sites[0])
    frappe.connect()
    try:
        # Your code here
        pass
    finally:
        frappe.destroy()

# Add to commands list
commands = [
    delete_account_recursive,
    import_chart_of_accounts,
    my_command,  # New command
]
```

## Troubleshooting

### Command not found

If the command is not found after installation:

```bash
# Check if the app is installed
docker exec erpnext_backend bench --site erpnext.example.com list-apps

# Reinstall the app
docker exec erpnext_backend bash -c "
    cd /home/frappe/frappe-bench
    bench --site erpnext.example.com uninstall-app dm_erpnext_utilities --yes
    bench --site erpnext.example.com install-app dm_erpnext_utilities
"

# Rebuild if necessary
docker exec erpnext_backend bench build
```

### Import errors

```bash
# Check CSV format
head -5 arquivo.csv

# Check encoding (should be UTF-8)
file -i arquivo.csv

# Test with dry-run first
bench --site erpnext.example.com import-chart-of-accounts arquivo.csv "COMPANY" --skip-root
```

## License

MIT License

## Author

DM-CASA - admin@dmla.tech
