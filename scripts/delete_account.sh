#!/bin/bash
#
# Script para deletar conta ERPNext recursivamente
#
set -e

ACCOUNT_NAME="$1"
COMPANY="$2"
MODE="${3:---dry-run}"
SITE="${4:-erpnext.example.com}"

if [ -z "$ACCOUNT_NAME" ] || [ -z "$COMPANY" ]; then
    echo "Usage: $0 \"ACCOUNT-NAME\" \"COMPANY\" [--dry-run|--confirm] [SITE]"
    echo ""
    echo "Examples:"
    echo "  $0 \"CUSTOS DE PRODUÇÃO - D-CASA\" \"DM-CASA\" --dry-run"
    echo "  $0 \"CUSTOS DE PRODUÇÃO - D-CASA\" \"DM-CASA\" --confirm"
    exit 1
fi

echo "📋 Configuration:"
echo "   Conta: $ACCOUNT_NAME"
echo "   Empresa: $COMPANY"
echo "   Modo: $MODE"
echo "   Site: $SITE"
echo ""

DRY_RUN_FLAG="True"
if [ "$MODE" = "--confirm" ]; then
    DRY_RUN_FLAG="False"
fi

# Copier le script core
echo "📦 Preparando script..."
docker cp "$(dirname "$0")/delete_account_core.py" erpnext_backend:/tmp/

# Créer le wrapper
echo "🔧 Criando wrapper..."
docker exec erpnext_backend bash -c "cat > /tmp/delete_wrapper.py << 'WRAPEOF'
import sys
sys.path.insert(0, '/tmp')
from delete_account_core import delete_account_and_children

def run_delete(account_name, company, dry_run):
    print('📊 Configuração:')
    print(f'   Conta: {account_name}')
    print(f'   Empresa: {company}')
    print(f'   Dry Run: {dry_run}')
    print()
    
    try:
        result = delete_account_and_children(account_name, company, dry_run)
        print('✅ Sucesso!' if result else '❌ Falhou')
        return result
    except Exception as e:
        print(f'❌ ERRO: {e}')
        import traceback
        traceback.print_exc()
        return False
WRAPEOF
"

# Exécuter via bench execute
echo "🚀 Executando..."
docker exec erpnext_backend bash -c "
cd /home/frappe/frappe-bench
bench --site $SITE execute 'import sys; sys.path.insert(0, \"/tmp\"); from delete_wrapper import run_delete; run_delete(\"$ACCOUNT_NAME\", \"$COMPANY\", $DRY_RUN_FLAG)'
"

echo ""
echo "✅ Concluído!"
