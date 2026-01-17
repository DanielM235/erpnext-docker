"""
Account management functions for ERPNext.
"""
import frappe


def find_children_recursive(account_name, company):
    """Find all children of an account recursively."""
    children = []
    
    # Find direct children
    direct_children = frappe.get_all('Account',
        filters={
            'parent_account': account_name,
            'company': company
        },
        fields=['name', 'account_name', 'is_group']
    )
    
    for child in direct_children:
        # First add grandchildren (recursion)
        grandchildren = find_children_recursive(child.name, company)
        children.extend(grandchildren)
        # Then add the child
        children.append(child)
    
    return children


def check_account_has_transactions(account_name):
    """Check if account has transactions."""
    # Check General Ledger Entries
    gl_entries = frappe.db.count('GL Entry', filters={'account': account_name})
    
    # Check other relevant tables
    journal_entries = frappe.db.count('Journal Entry Account', filters={'account': account_name})
    payment_entries = frappe.db.count('Payment Entry', filters={
        'paid_from': account_name
    }) + frappe.db.count('Payment Entry', filters={
        'paid_to': account_name
    })
    
    return {
        'gl_entries': gl_entries,
        'journal_entries': journal_entries,
        'payment_entries': payment_entries,
        'total': gl_entries + journal_entries + payment_entries
    }


def delete_account_and_children(account_name, company, dry_run=False):
    """Delete an account and all its children."""
    
    print(f"\n{'='*60}")
    print(f"Deleting account: {account_name}")
    print(f"Company: {company}")
    print(f"Mode: {'DRY RUN (simulation)' if dry_run else 'REAL DELETE'}")
    print(f"{'='*60}\n")
    
    # Check if account exists
    if not frappe.db.exists('Account', account_name):
        print(f"❌ ERROR: Account '{account_name}' does not exist!")
        return False
    
    # Get main account information
    main_account = frappe.get_doc('Account', account_name)
    
    print(f"📋 Main account:")
    print(f"   Name: {main_account.account_name}")
    print(f"   Number: {main_account.account_number or 'N/A'}")
    print(f"   Type: {main_account.account_type or 'N/A'}")
    print(f"   Is group: {'Yes' if main_account.is_group else 'No'}")
    print(f"   Root Type: {main_account.root_type}")
    
    # Check transactions in main account
    print(f"\n🔍 Checking transactions in main account...")
    main_transactions = check_account_has_transactions(account_name)
    if main_transactions['total'] > 0:
        print(f"⚠️  WARNING: Main account has {main_transactions['total']} transaction(s):")
        print(f"   - GL Entries: {main_transactions['gl_entries']}")
        print(f"   - Journal Entries: {main_transactions['journal_entries']}")
        print(f"   - Payment Entries: {main_transactions['payment_entries']}")
        
        if not dry_run:
            print("\n⚠️  Account has transactions! Use --dry-run first to review.")
            return False
    else:
        print("✅ Main account has no transactions.")
    
    # Find all children recursively
    print(f"\n🔍 Finding child accounts recursively...")
    children = find_children_recursive(account_name, company)
    
    if not children:
        print("ℹ️  No child accounts found.")
    else:
        print(f"📊 Found {len(children)} child account(s):\n")
        
        # Check transactions in each child
        children_with_transactions = []
        for child in children:
            trans = check_account_has_transactions(child.name)
            status = "✅" if trans['total'] == 0 else "⚠️"
            trans_info = f" ({trans['total']} transactions)" if trans['total'] > 0 else ""
            print(f"   {status} {child.account_name} - {child.name}{trans_info}")
            if trans['total'] > 0:
                children_with_transactions.append((child, trans))
        
        if children_with_transactions:
            print(f"\n⚠️  WARNING: {len(children_with_transactions)} child account(s) with transactions!")
            if not dry_run:
                print("\n⚠️  Some accounts have transactions! Use --dry-run first to review.")
                return False
    
    # Complete list to delete (children + parent)
    to_delete = children + [main_account]
    
    print(f"\n📝 Total accounts to delete: {len(to_delete)}")
    
    if dry_run:
        print(f"\n{'='*60}")
        print("🔍 DRY RUN - No accounts were deleted")
        print(f"{'='*60}")
        print("\nTo delete for real, execute without --dry-run:")
        print(f'  bench --site erpnext.example.com delete-account-recursive "{account_name}" "{company}"')
        return True
    
    # REAL DELETE - execute directly
    print(f"\n🗑️  Deleting {len(to_delete)} account(s)...\n")
    deleted_count = 0
    
    for account in to_delete:
        try:
            frappe.delete_doc('Account', account.name, force=1, ignore_permissions=True)
            deleted_count += 1
            print(f"   ✅ Deleted: {account.account_name} - {account.name}")
        except Exception as e:
            print(f"   ❌ Error deleting {account.name}: {str(e)}")
    
    frappe.db.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ Operation completed!")
    print(f"   Accounts deleted: {deleted_count}/{len(to_delete)}")
    print(f"{'='*60}\n")
    
    return True
