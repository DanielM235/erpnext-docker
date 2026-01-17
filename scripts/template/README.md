# ERPNext Custom Templates Deployment

This directory contains scripts for deploying custom templates to ERPNext containers.

## Overview

ERPNext allows custom Chart of Accounts templates to be added to the system by placing them in the verified templates directory within the container. This script automates the deployment process.

## Directory Structure

```
templates/
└── account/
    ├── br/                          # Brazilian templates
    │   ├── br_minimo.json          # Minimal chart (5 root accounts)
    │   └── br_pessoal.json         # Personal finance chart (150+ accounts)
    └── [other-countries]/           # Other country templates (future)
```

## Template File Naming Convention

Templates must follow the naming pattern: `{country_code}_{identifier}.json`

- **country_code**: Two-letter ISO country code (e.g., `br`, `us`, `fr`)
- **identifier**: Unique identifier for the template (e.g., `minimo`, `pessoal`, `business`)

**Examples:**
- `br_minimo.json` - Brazilian minimal chart
- `br_pessoal.json` - Brazilian personal finance chart
- `us_standard.json` - US standard chart (future)

## Template Structure

Templates must follow the ERPNext tree structure format:

```json
{
  "name": "Display Name of Template",
  "country_code": "br",
  "tree": {
    "1000 - Account Name": {
      "root_type": "Asset",
      "is_group": 1,
      "account_type": "Bank",
      "1100 - Sub Account": {
        "root_type": "Asset",
        "account_type": "Cash"
      }
    }
  }
}
```

**Key Fields:**
- `name`: Template name shown in ERPNext dropdown
- `country_code`: Two-letter country code
- `tree`: Nested object structure representing account hierarchy
- `root_type`: Required for root accounts (Asset, Liability, Equity, Income, Expense)
- `is_group`: Set to 1 for accounts that contain sub-accounts
- `account_type`: Optional type (Cash, Bank, Payable, Receivable, etc.)

## Scripts

### copy_templates_to_container.sh

Copies custom templates from the local workspace to the ERPNext container.

**Usage:**
```bash
./copy_templates_to_container.sh [CONTAINER_NAME] [--clear-cache]
```

**Arguments:**
- `CONTAINER_NAME` (optional): Name of the ERPNext backend container
  - Default: `erpnext_backend`
- `--clear-cache` (optional): Clear ERPNext cache and restart container after deployment

**Examples:**

1. **Deploy templates to default container:**
   ```bash
   ./copy_templates_to_container.sh
   ```

2. **Deploy to a specific container:**
   ```bash
   ./copy_templates_to_container.sh my-erpnext-backend
   ```

3. **Deploy and clear cache:**
   ```bash
   ./copy_templates_to_container.sh erpnext_backend --clear-cache
   ```

4. **Quick deployment with cache clear:**
   ```bash
   ./copy_templates_to_container.sh --clear-cache
   ```

## How It Works

1. **Validation**: Script checks if the specified container exists and is running
2. **Template Discovery**: Scans `templates/account/` for country-specific directories
3. **File Filtering**: Only copies files matching the `{country_code}_*.json` pattern
4. **Deployment**: Copies templates to container's verified directory:
   ```
   /home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified/
   ```
5. **Permissions**: Sets correct ownership (`frappe:frappe`) and permissions (`644`)
6. **Cache Clearing** (optional): Clears ERPNext cache and restarts container

## Deployment Target

Templates are deployed to:
```
Container: /home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified/
```

This is ERPNext's verified templates directory where custom Chart of Accounts templates are recognized by the system.

## After Deployment

Once templates are deployed:

1. **Access ERPNext**: Navigate to your ERPNext instance
2. **Create Company**: Go to Company creation form
3. **Select Template**: In the "Chart of Accounts Based On" dropdown, your custom templates will appear
4. **Create Company**: Select your template and create the company

## Troubleshooting

### Templates don't appear in dropdown

**Solution 1: Clear cache**
```bash
./copy_templates_to_container.sh --clear-cache
```

**Solution 2: Manual cache clear**
```bash
docker exec --user frappe erpnext_backend \
  bash -c "cd /home/frappe/frappe-bench && bench --site erpnext.example.com clear-cache"
docker restart erpnext_backend
```

### Container not found

**Check running containers:**
```bash
docker ps
```

**Check all containers (including stopped):**
```bash
docker ps -a
```

**Start stopped container:**
```bash
docker start erpnext_backend
```

### Permission errors

The script automatically sets correct permissions, but if you encounter issues:
```bash
docker exec --user root erpnext_backend \
  chown -R frappe:frappe /home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified/
```

### Template validation errors

Validate JSON syntax:
```bash
python3 -m json.tool templates/account/br/br_pessoal.json
```

Check template structure matches the format described above.

## Adding New Templates

To add a new template:

1. **Create the template file** in the appropriate country directory:
   ```bash
   templates/account/{country_code}/{country_code}_{identifier}.json
   ```

2. **Follow the naming convention**: `{country_code}_{identifier}.json`

3. **Use the correct structure**: Nested tree format with required fields

4. **Deploy the template**:
   ```bash
   ./copy_templates_to_container.sh --clear-cache
   ```

## Future Extensions

This script is designed to be extensible for other types of templates:

- **Document templates**: Forms, reports, etc.
- **Email templates**: Notification templates
- **Print formats**: Invoice, quotation formats
- **Workflows**: Custom workflow definitions

To add support for new template types:
1. Add new template directories (e.g., `templates/document/`)
2. Update the script to include new copy functions
3. Update this README with new documentation

## Reference

- [ERPNext Documentation - Chart of Accounts](https://docs.erpnext.com/docs/user/manual/en/accounts/chart-of-accounts)
- [Frappe Framework - Docker Deployment](https://github.com/frappe/frappe_docker)
- [ERPNext v16 Release Notes](https://github.com/frappe/erpnext/releases)
