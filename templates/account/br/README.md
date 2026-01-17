# Brazilian Chart of Accounts Templates for ERPNext v16

This directory contains Chart of Accounts templates ready for use in ERPNext version 16, adapted for the Brazilian context.

## 🎯 Objective

**Make templates appear in the dropdown list when creating a company in ERPNext.**

When you create a new company (`New Company`), your custom templates will appear in the "Chart of Accounts Based On" selection list alongside the default templates.

## 📋 Available Templates

### 1. Minimal Chart of Accounts (`br_minimo.json`)

Minimalist template containing only the **5 root accounts** of the accounting plan:

- **1000 - Ativos** (Asset)
- **2000 - Passivos** (Liability)
- **3000 - Patrimônio Líquido** (Equity)
- **4000 - Receitas** (Income)
- **5000 - Despesas** (Expense)

**When to use:** Ideal for starting an accounting plan completely from scratch, allowing total customization of the accounting structure according to your specific needs.

### 2. Complete Personal Finance Chart of Accounts (`br_pessoal.json`)

Complete and detailed template for **personal finance** and **household management**, containing more than 150 accounts organized hierarchically.

**Main groups included:**
- **Assets:** Bank accounts, investments, real estate, vehicles
- **Liabilities:** Debts, financing, accounts payable
- **Equity:** Own capital, accumulated profits
- **Income:** Salaries, investments, rents, own business
- **Expenses:** Housing, food, transportation, health, education, leisure

**When to use:** Perfect for creating a company with "Residential/Domestic" profile or for complete personal financial management from day one.

## 🚀 How to Add Custom Templates to ERPNext List

### Definitive Method: Install Templates in the Correct Directory

ERPNext searches for Chart of Accounts templates in a specific directory. To make your templates appear in the dropdown list when creating a company, follow these steps:

#### Step 1: Understand ERPNext Structure

Templates are located in:
```
/home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified/
```

Each country has its JSON file with the format: `{country_code}_{template_name}.json`

#### Step 2: Copy Templates to the Correct Directory

```bash
# Copy minimal template
docker cp templates/account/br/br_minimo.json \
  erpnext_backend:/home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified/br_minimo.json

# Copy complete personal template
docker cp templates/account/br/br_pessoal.json \
  erpnext_backend:/home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified/br_pessoal.json
```

**Important:** The file name must follow the pattern `br_{name}.json` where:
- `br` = country code (Brazil)
- `{name}` = unique template identifier

#### Step 3: Verify and Adjust JSON Format

The JSON must have this exact structure for ERPNext v16:

```json
{
  "name": "Template Name",
  "country_code": "br",
  "tree": {
    "1000 - Account Name": {
      "root_type": "Asset",
      "is_group": 1,
      "account_type": "Cash",
      "1100 - Sub Account": {
        "root_type": "Asset",
        "account_type": "Bank"
      }
    }
  }
}
```

#### Step 4: Clear Cache and Restart

```bash
# Clear site cache
docker exec --user frappe erpnext_backend bash -c "
  cd /home/frappe/frappe-bench
  bench --site erpnext.example.com clear-cache
  bench --site erpnext.example.com clear-website-cache
"

# Restart backend
docker restart erpnext_backend

# Wait for initialization
sleep 15
```

#### Step 5: Create New Company

1. **Access:** `Ctrl+K` → `New Company`

2. **In the "Chart of Accounts Based On" field:**
   - You will see the default templates
   - **YOUR TEMPLATES** should appear:
     - `Plano de Contas Mínimo - Brasil`
     - `Plano de Contas Pessoal - Brasil`

3. **Select the desired template** and complete company creation

4. **Result:** The company will be created with YOUR custom chart of accounts!

### 🔍 Verification: Templates Installed Correctly?

```bash
# List installed templates
docker exec erpnext_backend ls -la \
  /home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified/ | grep br_

# Check template content
docker exec erpnext_backend cat \
  /home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified/br_pessoal.json | head -20
```

You should see your files `br_minimo.json` and `br_pessoal.json` listed.

## 📝 Template JSON Structure

Templates follow the standard ERPNext v16 tree format:

```json
{
  "name": "Template Name",
  "country_code": "br",
  "tree": {
    "1000 - Account Name": {
      "root_type": "Asset",
      "is_group": 1,
      "account_type": "Cash",
      "1100 - Sub Account": {
        "root_type": "Asset",
        "account_type": "Bank"
      }
    }
  }
}
```

### Field Explanations:

- **name:** Template name that will appear in the list
- **country_code:** Country code (br for Brazil)
- **tree:** Nested object structure representing account hierarchy
- **root_type:** Required root type (Asset, Liability, Equity, Income, Expense)
- **is_group:** Set to 1 for accounts that contain sub-accounts
- **account_type:** Specific type like `Cash`, `Bank`, `Payable`, etc. (optional for groups)

## 🔧 Customization

You can customize templates by editing the JSON files:

1. **To add an account:** Copy an existing account block and adjust the fields
2. **To remove an account:** Delete the corresponding JSON block
3. **Hierarchy:** Use nested structure to define the tree hierarchy
4. **Numbering:** Maintain logical sequence (ex: 5100, 5110, 5111...)

## ⚠️ Important Notes

1. **Root Accounts:** The 5 root accounts (Asset, Liability, Equity, Income, Expense) are mandatory
2. **Currency:** Make sure to set `BRL` as default currency
3. **Account Types:** Respect valid ERPNext types (Cash, Bank, Tax, Payable, Receivable, etc.)
4. **Groups vs Leaves:** Group accounts (`is_group: 1`) cannot receive direct entries
5. **Backup:** Always backup before importing a chart of accounts

## 📚 References

- [Official ERPNext Documentation - Chart of Accounts](https://docs.erpnext.com/docs/user/manual/en/accounts/chart-of-accounts)
- [ERPNext v16 Release Notes](https://github.com/frappe/erpnext/releases)

## 🔗 Useful Links

- [ERPNext Documentation - Chart of Accounts](https://docs.erpnext.com/docs/user/manual/en/accounts/chart-of-accounts)
- [ERPNext Forum](https://discuss.erpnext.com)
- [ERPNext GitHub](https://github.com/frappe/erpnext)

---

**Last update:** January 2026
**Compatibility:** ERPNext v16+
**Language:** Portuguese (Brazil)
