"""
Chart of Accounts importer from CSV files.
"""
import frappe
import csv
import os


def import_accounts_from_csv(csv_files, company, reset=False, skip_root=False):
    """
    Import chart of accounts from one or more CSV files.
    
    Args:
        csv_files: List of paths to CSV files
        company: Company name
        reset: If True, delete existing accounts before importing
        skip_root: If True, skip importing root accounts (already exist)
    
    Returns:
        True if success, False if failure
    """
    
    print(f"\n{'='*60}")
    print(f"Importing Chart of Accounts")
    print(f"{'='*60}\n")
    
    # Check if company exists
    if not frappe.db.exists('Company', company):
        print(f"❌ ERROR: Company '{company}' does not exist!")
        return False
    
    # Reset: delete existing non-root accounts
    if reset:
        print("🗑️  RESET: Deleting existing accounts (except root)...\n")
        existing_accounts = frappe.get_all('Account',
            filters={
                'company': company,
                'parent_account': ['!=', '']
            },
            fields=['name', 'account_name']
        )
        
        print(f"   Found {len(existing_accounts)} accounts to delete...")
        deleted = 0
        for acc in existing_accounts:
            try:
                frappe.delete_doc('Account', acc.name, force=1, ignore_permissions=True)
                deleted += 1
            except Exception as e:
                print(f"   ⚠️  Error deleting {acc.name}: {e}")
        
        frappe.db.commit()
        print(f"   ✅ Deleted {deleted} accounts\n")
    
    # Process each CSV file
    total_imported = 0
    total_skipped = 0
    total_errors = 0
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"❌ File not found: {csv_file}")
            continue
        
        print(f"📄 Processing file: {csv_file}")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                account_name = row.get('Account Name', '').strip()
                parent_account = row.get('Parent Account', '').strip()
                account_type = row.get('Account Type', '').strip()
                account_number = row.get('Account Number', '').strip()
                
                if not account_name:
                    continue
                
                # Skip root accounts if skip_root=True
                if skip_root and not parent_account:
                    print(f"   ⏭️  Skipping (root): {account_name}")
                    total_skipped += 1
                    continue
                
                # Check if account already exists
                full_account_name = f"{account_name}"
                if frappe.db.exists('Account', full_account_name):
                    print(f"   ⏭️  Already exists: {account_name}")
                    total_skipped += 1
                    continue
                
                # Check if parent exists (if specified)
                if parent_account and not frappe.db.exists('Account', parent_account):
                    print(f"   ❌ Parent does not exist: {parent_account} (for {account_name})")
                    total_errors += 1
                    continue
                
                # Create account
                try:
                    account_doc = frappe.get_doc({
                        'doctype': 'Account',
                        'account_name': account_name,
                        'company': company,
                        'parent_account': parent_account or None,
                        'account_type': account_type or None,
                        'account_number': account_number or None,
                        'is_group': 0  # By default, not a group
                    })
                    
                    # If has potential children, mark as group
                    # (this will be adjusted automatically by ERPNext when children are added)
                    
                    account_doc.insert(ignore_permissions=True)
                    print(f"   ✅ Imported: {account_name}")
                    total_imported += 1
                    
                except Exception as e:
                    print(f"   ❌ Error importing {account_name}: {e}")
                    total_errors += 1
        
        # Commit after each file
        frappe.db.commit()
        print(f"   💾 Saved changes from {csv_file}\n")
    
    # Final summary
    print(f"{'='*60}")
    print(f"📊 Import Summary:")
    print(f"   ✅ Imported: {total_imported}")
    print(f"   ⏭️  Skipped: {total_skipped}")
    print(f"   ❌ Errors: {total_errors}")
    print(f"{'='*60}\n")
    
    return total_errors == 0


def get_root_accounts(company):
    """Return the company's root accounts."""
    return frappe.get_all('Account',
        filters={
            'company': company,
            'parent_account': ''
        },
        fields=['name', 'account_name', 'root_type']
    )
