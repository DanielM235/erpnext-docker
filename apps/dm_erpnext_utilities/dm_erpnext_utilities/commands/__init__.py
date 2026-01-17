import click
from frappe.commands import pass_context


@click.command('delete-account-recursive')
@click.argument('account_name')
@click.argument('company')
@click.option('--dry-run', is_flag=True, default=False, help='Simulate without deleting')
@pass_context
def delete_account_recursive(context, account_name, company, dry_run):
    """
    Delete an ERPNext account recursively, including all child accounts.
    
    Example:
        bench --site erpnext.example.com delete-account-recursive "PRODUCTION COSTS - D-CASA" "DM-CASA"
        bench --site erpnext.example.com delete-account-recursive "PRODUCTION COSTS - D-CASA" "DM-CASA" --dry-run
    """
    import frappe
    from dm_erpnext_utilities.commands.account_manager import delete_account_and_children
    
    frappe.init(site=context.sites[0])
    frappe.connect()
    
    try:
        print(f"\n📊 Configuration:")
        print(f"   Account: {account_name}")
        print(f"   Company: {company}")
        print(f"   Mode: {'DRY-RUN (simulation)' if dry_run else 'REAL EXECUTION'}")
        print()
        
        result = delete_account_and_children(account_name, company, dry_run)
        
        if result:
            print("\n✅ Operation completed successfully!")
        else:
            print("\n❌ Operation failed.")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    finally:
        frappe.destroy()


@click.command('import-chart-of-accounts')
@click.argument('csv_files', nargs=-1, required=True)
@click.argument('company')
@click.option('--reset', is_flag=True, default=False, help='Delete existing accounts before importing')
@click.option('--skip-root', is_flag=True, default=False, help='Skip root accounts (already exist)')
@pass_context
def import_chart_of_accounts(context, csv_files, company, reset, skip_root):
    """
    Import chart of accounts from one or more CSV files.
    
    Files must be in hierarchical order (level 1, level 2, etc.)
    
    Expected CSV format:
    Account Name,Parent Account,Account Type,Company
    
    Example:
        bench --site erpnext.example.com import-chart-of-accounts level2.csv level3.csv level4.csv "DM-CASA"
        bench --site erpnext.example.com import-chart-of-accounts *.csv "DM-CASA" --skip-root
        bench --site erpnext.example.com import-chart-of-accounts *.csv "DM-CASA" --reset
    """
    import frappe
    from dm_erpnext_utilities.commands.account_importer import import_accounts_from_csv
    
    frappe.init(site=context.sites[0])
    frappe.connect()
    
    try:
        print(f"\n📊 Configuration:")
        print(f"   Company: {company}")
        print(f"   Files: {', '.join(csv_files)}")
        print(f"   Reset: {'YES (delete existing accounts)' if reset else 'NO'}")
        print(f"   Skip Root: {'YES' if skip_root else 'NO'}")
        print()
        
        result = import_accounts_from_csv(
            csv_files=csv_files,
            company=company,
            reset=reset,
            skip_root=skip_root
        )
        
        if result:
            print("\n✅ Import completed successfully!")
        else:
            print("\n❌ Import failed.")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    finally:
        frappe.destroy()


commands = [
    delete_account_recursive,
    import_chart_of_accounts,
]
