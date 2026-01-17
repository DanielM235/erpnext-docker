#!/usr/bin/env python3
"""
Script para deletar uma conta (Account) e todos seus filhos recursivamente no ERPNext.

ATENÇÃO: Este script deleta dados permanentemente. Use com cuidado!

Uso:
    python3 delete_account_recursive.py "Nome da Conta - SIGLA" DM-CASA [--dry-run]

Exemplo:
    python3 delete_account_recursive.py "Ativo Circulante - D-CASA" "DM-CASA" --dry-run
    python3 delete_account_recursive.py "Despesas Fixas - D-CASA" "DM-CASA"
"""

import sys
import os
import argparse

def find_children_recursive(account_name, company):
    """Encontra todos os filhos de uma conta recursivamente."""
    import frappe
    
    children = []
    
    # Buscar filhos diretos
    direct_children = frappe.get_all('Account',
        filters={
            'parent_account': account_name,
            'company': company
        },
        fields=['name', 'account_name', 'is_group']
    )
    
    for child in direct_children:
        # Primeiro adiciona os netos (recursão)
        grandchildren = find_children_recursive(child.name, company)
        children.extend(grandchildren)
        # Depois adiciona o filho
        children.append(child)
    
    return children


def check_account_has_transactions(account_name):
    """Verifica se a conta tem transações."""
    import frappe
    
    # Verificar General Ledger Entries
    gl_entries = frappe.db.count('GL Entry', filters={'account': account_name})
    
    # Verificar outras tabelas relevantes
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
    """Deleta uma conta e todos seus filhos."""
    import frappe
    
    print(f"\n{'='*60}")
    print(f"Deletando conta: {account_name}")
    print(f"Empresa: {company}")
    print(f"Modo: {'DRY RUN (simulação)' if dry_run else 'REAL DELETE'}")
    print(f"{'='*60}\n")
    
    # Verificar se a conta existe
    if not frappe.db.exists('Account', account_name):
        print(f"❌ ERRO: Conta '{account_name}' não existe!")
        return False
    
    # Buscar informações da conta principal
    main_account = frappe.get_doc('Account', account_name)
    
    print(f"📋 Conta principal:")
    print(f"   Nome: {main_account.account_name}")
    print(f"   Número: {main_account.account_number or 'N/A'}")
    print(f"   Tipo: {main_account.account_type or 'N/A'}")
    print(f"   É grupo: {'Sim' if main_account.is_group else 'Não'}")
    print(f"   Root Type: {main_account.root_type}")
    
    # Verificar transações na conta principal
    print(f"\n🔍 Verificando transações na conta principal...")
    main_transactions = check_account_has_transactions(account_name)
    if main_transactions['total'] > 0:
        print(f"⚠️  ATENÇÃO: Conta principal tem {main_transactions['total']} transação(ões):")
        print(f"   - GL Entries: {main_transactions['gl_entries']}")
        print(f"   - Journal Entries: {main_transactions['journal_entries']}")
        print(f"   - Payment Entries: {main_transactions['payment_entries']}")
        
        if not dry_run:
            response = input("\n❓ Deseja continuar mesmo assim? (sim/não): ")
            if response.lower() not in ['sim', 's', 'yes', 'y']:
                print("❌ Operação cancelada pelo usuário.")
                return False
    else:
        print("✅ Conta principal não tem transações.")
    
    # Buscar todos os filhos recursivamente
    print(f"\n🔍 Buscando contas filhas recursivamente...")
    children = find_children_recursive(account_name, company)
    
    if not children:
        print("ℹ️  Nenhuma conta filha encontrada.")
    else:
        print(f"📊 Encontradas {len(children)} conta(s) filha(s):\n")
        
        # Verificar transações em cada filho
        children_with_transactions = []
        for child in children:
            trans = check_account_has_transactions(child.name)
            status = "✅" if trans['total'] == 0 else "⚠️"
            trans_info = f" ({trans['total']} transações)" if trans['total'] > 0 else ""
            print(f"   {status} {child.account_name} - {child.name}{trans_info}")
            if trans['total'] > 0:
                children_with_transactions.append((child, trans))
        
        if children_with_transactions:
            print(f"\n⚠️  ATENÇÃO: {len(children_with_transactions)} conta(s) filha(s) com transações!")
            if not dry_run:
                response = input("\n❓ Deseja continuar mesmo assim? (sim/não): ")
                if response.lower() not in ['sim', 's', 'yes', 'y']:
                    print("❌ Operação cancelada pelo usuário.")
                    return False
    
    # Lista completa para deletar (filhos + pai)
    to_delete = children + [main_account]
    
    print(f"\n📝 Total de contas a deletar: {len(to_delete)}")
    
    if dry_run:
        print(f"\n{'='*60}")
        print("🔍 DRY RUN - Nenhuma conta foi deletada")
        print(f"{'='*60}")
        return True
    
    # Confirmação final
    print(f"\n{'='*60}")
    print("⚠️  ATENÇÃO: Esta operação é IRREVERSÍVEL!")
    print(f"{'='*60}")
    response = input(f"\n❓ Confirma a deleção de {len(to_delete)} conta(s)? (sim/não): ")
    
    if response.lower() not in ['sim', 's', 'yes', 'y']:
        print("❌ Operação cancelada pelo usuário.")
        return False
    
    # Deletar as contas
    print(f"\n🗑️  Deletando contas...\n")
    deleted_count = 0
    
    for account in to_delete:
        try:
            frappe.delete_doc('Account', account.name, force=1)
            deleted_count += 1
            print(f"   ✅ Deletado: {account.account_name} - {account.name}")
        except Exception as e:
            print(f"   ❌ Erro ao deletar {account.name}: {str(e)}")
    
    frappe.db.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ Operação concluída!")
    print(f"   Contas deletadas: {deleted_count}/{len(to_delete)}")
    print(f"{'='*60}\n")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Deletar conta do ERPNext e todos seus filhos recursivamente',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Simulação (dry-run) - não deleta nada
  python3 delete_account_recursive.py "Ativo Circulante - D-CASA" "DM-CASA" --dry-run
  
  # Deleção real
  python3 delete_account_recursive.py "Despesas Fixas - D-CASA" "DM-CASA"
  
  # Com número da conta
  python3 delete_account_recursive.py "5100 - Despesas Fixas - D-CASA" "DM-CASA"
        """
    )
    
    parser.add_argument('account_name', help='Nome completo da conta (ex: "Ativo Circulante - D-CASA")')
    parser.add_argument('company', help='Nome da empresa (ex: "DM-CASA")')
    parser.add_argument('--dry-run', action='store_true', help='Simular sem deletar (recomendado primeiro)')
    parser.add_argument('--site', default='erpnext.teste', help='Nome do site ERPNext (default: erpnext.teste)')
    
    args = parser.parse_args()
    
    # Importar Frappe
    try:
        import frappe
    except ImportError:
        print("❌ ERRO: Módulo 'frappe' não encontrado.")
        print("Este script deve ser executado dentro do container ERPNext:")
        print("\n  docker exec -it erpnext-backend python3 /workspace/scripts/delete_account_recursive.py ...")
        sys.exit(1)
    
    # Inicializar Frappe
    frappe.init(site=args.site)
    frappe.connect()
    
    # Executar deleção
    try:
        success = delete_account_and_children(args.account_name, args.company, args.dry_run)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        frappe.destroy()


if __name__ == '__main__':
    main()
