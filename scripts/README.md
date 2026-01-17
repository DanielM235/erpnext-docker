# Scripts ERPNext - Casa DMLA

Scripts utilitários para gerenciar a instalação ERPNext.

## delete_account_recursive.py

Deleta uma conta (Account) e todos seus filhos recursivamente.

### Uso

**Dentro do container ERPNext:**

```bash
# 1. Copiar script para dentro do container
docker cp scripts/delete_account_recursive.py erpnext-backend:/workspace/

# 2. Executar no container (DRY RUN primeiro - recomendado)
docker exec -it erpnext-backend python3 /workspace/delete_account_recursive.py \
  "Nome da Conta - SIGLA" "EMPRESA" --dry-run

# 3. Executar deleção real (se dry-run OK)
docker exec -it erpnext-backend python3 /workspace/delete_account_recursive.py \
  "Nome da Conta - SIGLA" "EMPRESA"
```

### Exemplos

#### 1. Dry Run (Simulação - recomendado primeiro)

```bash
docker cp scripts/delete_account_recursive.py erpnext-backend:/workspace/

docker exec -it erpnext-backend python3 /workspace/delete_account_recursive.py \
  "Ativo Circulante - D-CASA" "DM-CASA" --dry-run
```

Saída:
```
============================================================
Deletando conta: Ativo Circulante - D-CASA
Empresa: DM-CASA
Modo: DRY RUN (simulação)
============================================================

📋 Conta principal:
   Nome: Ativo Circulante
   Número: 1100
   Tipo: N/A
   É grupo: Sim
   Root Type: Asset

🔍 Verificando transações na conta principal...
✅ Conta principal não tem transações.

🔍 Buscando contas filhas recursivamente...
📊 Encontradas 15 conta(s) filha(s):

   ✅ Caixa - 1111 - Caixa - D-CASA
   ✅ Banco - Conta Corrente - 1112 - Banco - Conta Corrente - D-CASA
   ...

📝 Total de contas a deletar: 16

============================================================
🔍 DRY RUN - Nenhuma conta foi deletada
============================================================
```

#### 2. Deleção Real

```bash
docker exec -it erpnext-backend python3 /workspace/delete_account_recursive.py \
  "Despesas Fixas - D-CASA" "DM-CASA"
```

O script pedirá confirmação antes de deletar.

#### 3. Deletar conta com transações

```bash
docker exec -it erpnext-backend python3 /workspace/delete_account_recursive.py \
  "5211 - Supermercado - D-CASA" "DM-CASA" --dry-run
```

Se houver transações, o script vai avisar e pedir confirmação adicional.

### Opções

- `account_name`: Nome completo da conta incluindo sufixo (ex: "Ativo Circulante - D-CASA")
- `company`: Nome da empresa (ex: "DM-CASA")
- `--dry-run`: Simular sem deletar nada (RECOMENDADO testar primeiro)
- `--site`: Nome do site ERPNext (default: erpnext.teste)

### Avisos Importantes

⚠️ **Este script deleta dados permanentemente!**

1. **SEMPRE execute com `--dry-run` primeiro** para ver o que será deletado
2. **Faça backup** antes de executar a deleção real:
   ```bash
   docker exec -it erpnext-backend bench --site erpnext.teste backup
   ```
3. Se houver **transações** nas contas, você será avisado e precisará confirmar
4. A deleção é **recursiva** - deleta a conta e TODOS os filhos/netos/etc.

### Casos de Uso

**1. Limpar import parcial que deu errado:**
```bash
# Ver o que será deletado
docker exec -it erpnext-backend python3 /workspace/delete_account_recursive.py \
  "Ativo Circulante - D-CASA" "DM-CASA" --dry-run

# Se OK, deletar
docker exec -it erpnext-backend python3 /workspace/delete_account_recursive.py \
  "Ativo Circulante - D-CASA" "DM-CASA"
```

**2. Remover categorias inteiras:**
```bash
# Deletar todas despesas fixas
docker exec -it erpnext-backend python3 /workspace/delete_account_recursive.py \
  "5100 - Despesas Fixas - D-CASA" "DM-CASA"
```

**3. Limpar plano de contas completo (exceto root):**
```bash
# Deletar cada categoria de segundo nível
for conta in "Ativo Circulante" "Ativo Não Circulante" "Passivo Circulante" "Passivo Não Circulante"; do
  docker exec -it erpnext-backend python3 /workspace/delete_account_recursive.py \
    "${conta} - D-CASA" "DM-CASA"
done
```

### Troubleshooting

**Erro: "Módulo 'frappe' não encontrado"**
- O script deve ser executado DENTRO do container ERPNext
- Use `docker exec -it erpnext-backend ...`

**Erro: "Conta não existe"**
- Verifique o nome exato da conta no Chart of Accounts
- O nome deve incluir o sufixo da empresa (ex: " - D-CASA")
- Exemplo correto: "Ativo Circulante - D-CASA"
- Exemplo errado: "Ativo Circulante"

**Erro: "Cannot delete Account with child accounts"**
- Este erro não deveria acontecer com este script
- Se acontecer, pode ser que haja um problema de permissões
- Tente executar como root: `docker exec -u root -it erpnext-backend ...`

### Segurança

Este script:
- ✅ Verifica se a conta existe antes de deletar
- ✅ Lista todos os filhos que serão deletados
- ✅ Detecta contas com transações
- ✅ Pede confirmação antes de deletar
- ✅ Suporta modo dry-run para testar
- ✅ Deleta na ordem correta (folhas primeiro)
- ✅ Usa `force=1` para bypass de validações ERPNext

## Outros Scripts

(Adicionar outros scripts aqui conforme necessário)

---

*Atualizado em: 16/01/2026*
