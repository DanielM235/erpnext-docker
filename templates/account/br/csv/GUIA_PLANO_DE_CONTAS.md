# Guia de Importação do Plano de Contas Pessoal para ERPNext

## 📋 Sobre o Plano de Contas

Este plano de contas foi desenvolvido especificamente para **gestão financeira pessoal/doméstica** no Brasil, com categorias detalhadas para rastreamento completo de receitas e despesas.

### Estrutura do Plano de Contas

#### 🏦 **1. ATIVOS (1000-1999)**
- **Ativo Circulante**: Caixa, bancos, investimentos de curto prazo
- **Ativo Não Circulante**: Investimentos de longo prazo, imóveis, veículos

#### 💳 **2. PASSIVOS (2000-2999)**
- **Passivo Circulante**: Cartões de crédito, contas a pagar, empréstimos curto prazo
- **Passivo Não Circulante**: Financiamentos imobiliários, veículos

#### 💰 **3. PATRIMÔNIO LÍQUIDO (3000-3999)**
- Capital e lucros acumulados

#### 💵 **4. RECEITAS (4000-4999)**
- Salário e benefícios trabalhistas
- Rendimentos de investimentos
- Receitas extras

#### 🛒 **5. DESPESAS (5000-5999)**
- **Despesas Fixas**: Moradia, transporte, utilidades, seguros
- **Despesas Variáveis**: Alimentação, saúde, educação, vestuário
- **Lazer e Entretenimento**: Cultura, hobbies, viagens
- **Despesas Financeiras**: Juros, tarifas bancárias, impostos
- **Outras Despesas**: Presentes, pets, crianças

---

## ❓ Devo Substituir ou Manter o Plano de Contas Atual?

### 🎯 Recomendação: **CRIAR NOVA EMPRESA**

**Por quê?**
- ✅ Mantém a empresa teste intacta
- ✅ Começa limpo com o plano de contas correto
- ✅ Sem risco de conflitos ou duplicação
- ✅ Você pode ter múltiplas empresas no mesmo ERPNext

### Opções:

#### **Opção A: Criar Nova Empresa com Plano de Contas Personalizado** ⭐ RECOMENDADO
```
Ideal para: Começar do zero com o plano de contas correto
Risco: Nenhum
Tempo: 5 minutos
```

#### **Opção B: Manter Plano Existente e Adicionar Contas**
```
Ideal para: Você já tem transações e quer adicionar subcategorias
Risco: Possíveis duplicações
Tempo: 10 minutos + limpeza manual
```

#### **Opção C: Deletar Plano Atual e Importar Novo**
```
Ideal para: Empresa sem transações, quer substituir completamente
Risco: ALTO - só fazer se não houver transações
Tempo: 15 minutos
```

---

## 🚀 Como Importar para o ERPNext v16

### ⚠️ IMPORTANTE: DocType Correto para v16

Na versão 16 do ERPNext, você deve usar:
- **DocType**: `Account` (não "Chart of Accounts")
- "Chart of Accounts" é apenas a visualização em árvore, não um DocType importável

---

### Método 1: Criar Nova Empresa com Plano Personalizado ⭐ RECOMENDADO

#### Passo 1: Criar Nova Empresa
```
1. Faça login como Administrator
2. Vá para: Accounting > Company > New
   (ou use a busca: Ctrl+K e digite "New Company")
```

#### Passo 2: Preencha os Dados
```
Company Name: Finanças Pessoais
   (ou: Casa [Seu Nome], Família [Sobrenome])

Abbr: FP
   (abreviação usada em códigos - use 2-3 letras)

Country: Brazil

Default Currency: BRL

Chart Of Accounts Based On: Standard Template
   ⚠️ IMPORTANTE: Depois vamos substituir este plano

Domain: Services

✅ Clique em "Save"
```

#### Passo 3: Importar o Plano de Contas Personalizado

Após criar a empresa, você tem duas opções:

**Opção 3A: Via Chart of Accounts Importer** (Mais Simples)
```
1. Vá para: Accounting > Chart of Accounts Importer
   (ou busque: Ctrl+K > "Chart of Accounts Importer")

2. Clique em "New"

3. Preencha:
   - Company: Selecione "Finanças Pessoais" (a empresa que acabou de criar)
   - Import File Type: "CSV"
   - Parent Account: Deixe vazio (vai importar a hierarquia completa)

4. Anexe o arquivo:
   - Clique em "Attach"
   - Selecione: plano_de_contas_pessoal_br.csv

5. ✅ Clique em "Save"
6. ✅ Clique em "Import" (botão aparece após salvar)

7. Aguarde a mensagem de confirmação (30-60 segundos)
```

**Opção 3B: Via Data Import Tool**
```
1. Vá para: Setup > Data > Data Import
   (ou busque: Ctrl+K > "Data Import")

2. Clique em "New"

3. Configure:
   - Reference DocType: "Account"  ⚠️ IMPORTANTE: Use "Account", não "Chart of Accounts"
   - Import Type: "Insert New Records"
   - Submit After Import: ✅ (marque)

4. Anexe o arquivo:
   - Import File: plano_de_contas_pessoal_br.csv

5. Mapeie os campos (deve mapear automaticamente):
   - Account Name → account_name
   - Parent Account → parent_account
   - Account Number → account_number
   - Account Type → account_type
   - Is Group → is_group
   - Root Type → root_type
   - Company → company (fixo: "Finanças Pessoais")

6. ✅ Clique em "Save"
7. ✅ Clique em "Start Import"

8. Monitore o progresso na parte inferior da tela
```

---

### Método 2: Adicionar Contas à Empresa Existente (Se Já Tem Transações)

### Método 2: Adicionar Contas à Empresa Existente (Se Já Tem Transações)

⚠️ **ATENÇÃO**: Este método vai **ADICIONAR** contas, não substituir. Você terá contas duplicadas se já existirem.

```
1. Vá para: Setup > Data > Data Import

2. Configure:
   - Reference DocType: "Account"
   - Import Type: "Insert New Records"
   - Company: Selecione sua empresa existente

3. Anexe: plano_de_contas_pessoal_br.csv

4. ANTES DE IMPORTAR:
   - Edite o CSV e remova contas que já existem
   - Exemplo: Se já tem "Ativos", remova esta linha
   - Mantenha apenas as subcategorias que deseja adicionar

5. Start Import
```

**Resultado**: Suas contas existentes permanecem + novas contas são adicionadas

---

### Método 3: Substituir Plano de Contas Completamente (SEM Transações)

⚠️ **PERIGO**: Só faça isso se:
- ✅ A empresa NÃO tem nenhuma transação lançada
- ✅ Você fez backup do banco de dados
- ✅ Você tem certeza absoluta

#### Passo 1: Backup (OBRIGATÓRIO)
```bash
docker compose exec backend bench --site erp.dmla.bi backup --with-files
```

#### Passo 2: Verificar Se Há Transações
```
1. Vá para: Accounting > General Ledger
2. Filtre por sua empresa
3. Se aparecer QUALQUER lançamento: NÃO delete o plano de contas!
```

#### Passo 3: Deletar Contas Antigas (Se 0 transações)
```bash
# Conecte ao container
docker compose exec backend bash

# Acesse o console
bench --site erp.dmla.bi console

# No console Python:
import frappe

# Substitua pelo nome correto da sua empresa
company_name = "DM-CASA"  # ⚠️ ALTERE AQUI

# Verificar se há transações
count = frappe.db.count('GL Entry', {'company': company_name})
print(f"Transações encontradas: {count}")

# SE count = 0, pode deletar:
if count == 0:
    frappe.db.sql("""
        DELETE FROM `tabAccount` 
        WHERE company = %s
        AND name NOT IN (
            SELECT DISTINCT account FROM `tabGL Entry` WHERE company = %s
        )
    """, (company_name, company_name))
    frappe.db.commit()
    print("Contas deletadas com sucesso")
else:
    print("ERRO: Empresa tem transações! NÃO pode deletar contas.")

# Saia: Ctrl+D
```

#### Passo 4: Importar Novo Plano
Use o Método 1 acima para importar o novo plano.

---

## 🔧 Ajustes Necessários no CSV para v16

O CSV fornecido já está correto para ERPNext v16, mas você precisa adicionar a coluna **Company**:

### Opção A: Adicionar Company Durante a Importação
Durante o Data Import, na etapa de mapeamento:
```
- Company: Defina um valor fixo = "Finanças Pessoais"
  (ou o nome da sua empresa)
```

### Opção B: Editar o CSV Manualmente (Não Necessário)
O ERPNext v16 permite definir a empresa durante a importação, então não precisa editar o CSV.

---

## 📋 Formato Correto do CSV para v16

O CSV atual está usando o formato correto:
```csv
"Account Name","Parent Account","Account Number","Account Type","Is Group","Root Type"
"Ativos","","1000","Asset",1,"Asset"
"Ativo Circulante","Ativos","1100","Asset",1,"Asset"
...
```

### Campos Obrigatórios para v16:
1. ✅ **Account Name** - Nome da conta (obrigatório)
2. ✅ **Root Type** - Tipo raiz: Asset, Liability, Equity, Income, Expense
3. ⚠️ **Company** - Nome da empresa (definido durante importação)
4. ✅ **Parent Account** - Conta pai (vazio para contas raiz)
5. **Is Group** - 1 para grupos, vazio/0 para contas finais
6. **Account Number** - Número da conta (opcional mas recomendado)
7. **Account Type** - Tipo específico (Bank, Cash, Payable, etc.)

### Campos Opcionais Úteis:
- **Account Currency** - Moeda (padrão: BRL)
- **Disabled** - 0/1 para desabilitar conta
- **Balance Must Be** - "Debit" ou "Credit" para validação

---

## 🎯 Procedimento Recomendado FINAL

### Para Você (Situação Atual):

1. ✅ **Criar Nova Empresa "Finanças Pessoais"**
   - Vá para: Accounting > Company > New
   - Nome: "Finanças Pessoais" ou "Casa [Seu Nome]"
   - Abbr: "FP"
   - Country: Brazil
   - Save

2. ✅ **Importar Plano de Contas**
   - Vá para: Accounting > Chart of Accounts Importer
   - Company: Finanças Pessoais
   - Anexe: plano_de_contas_pessoal_br.csv
   - Import

3. ✅ **Configurar como Empresa Padrão**
   - Vá para: Setup > My Settings
   - Default Company: Finanças Pessoais
   - Save

4. ✅ **Desabilitar Empresa Antiga** (Opcional)
   - Vá para: Accounting > Company > [Empresa Antiga]
   - Marque: "Disabled"
   - Save

---

## 🐛 Solução de Problemas v16

### Erro: "Account Name already exists"
```
Causa: Conta já existe na empresa
Solução:
1. Vá para: Accounting > Chart of Accounts
2. Procure a conta duplicada
3. Renomeie ou delete a antiga
4. Tente importar novamente
```

### Erro: "Parent Account not found"
```
Causa: A conta pai ainda não foi importada
Solução: 
- O CSV já está na ordem correta (pais antes de filhos)
- Se o erro persistir, importe em duas etapas:
  1. Primeiro: Apenas contas raiz (Ativos, Passivos, etc.)
  2. Depois: Restante das contas
```

### Erro: "Company is mandatory"
```
Causa: Campo Company não foi definido
Solução:
1. Durante o Data Import, no mapeamento de campos
2. Adicione: Company = "Finanças Pessoais" (valor fixo)
```

### Não vejo "Chart of Accounts Importer"
```
Solução:
1. Use a busca: Ctrl+K
2. Digite: "Chart of Accounts Importer"
3. Se não encontrar: Use "Data Import" com DocType "Account"
```

### Import muito lento ou trava
```
Causa: Muitas contas sendo importadas de uma vez
Solução:
1. Divida o CSV em partes menores (50-100 contas por vez)
2. Importe grupos principais primeiro
3. Depois importe subcontas
```

---

## ✅ Checklist Atualizado para v16

### Antes de Começar:
- [ ] Backup realizado
- [ ] Decidiu: Nova empresa ou adicionar à existente?
- [ ] Verificou que não há transações (se vai deletar contas)

### Durante Importação:
- [ ] Usou DocType: **"Account"** (não "Chart of Accounts")
- [ ] Definiu Company corretamente
- [ ] CSV tem todas as colunas necessárias
- [ ] Validou dados antes de importar

### Após Importação:
- [ ] Verificou hierarquia no Chart of Accounts
- [ ] Testou criar uma transação
- [ ] Conferiu Balance Sheet
- [ ] Conferiu Profit and Loss
- [ ] Adicionou contas bancárias específicas

---

**Atualizado para**: ERPNext v16.0.1  
**Data**: Janeiro 2026  
**Status**: Verificado e testado

---

## 📝 Validação Pós-Importação

### Verificações Essenciais:

#### 1. Verifique Hierarquia
```
Vá para: Accounting > Chart of Accounts
- Expanda a árvore
- Confirme que todas as contas estão nos lugares corretos
- Verifique se contas-pai estão marcadas como "Is Group"
```

#### 2. Teste uma Transação
```
1. Crie um lançamento de teste:
   - Accounting > Journal Entry > New
   - Débito: Banco - Conta Corrente
   - Crédito: Salário
   - Valor: R$ 100,00
2. Salve e submeta
3. Verifique se aparece corretamente nos relatórios
```

#### 3. Verifique Relatórios
```
- Vá para: Accounting > Financial Statements > Balance Sheet
- Vá para: Accounting > Financial Statements > Profit and Loss
- Confirme que as contas aparecem nas seções corretas
```

---

## 🎯 Uso Prático do Plano de Contas

### Exemplos de Lançamentos Comuns:

#### Recebimento de Salário:
```
Débito: Banco - Conta Corrente (1112)
Crédito: Salário (4101)
```

#### Pagamento de Aluguel:
```
Débito: Aluguel (5111)
Crédito: Banco - Conta Corrente (1112)
```

#### Compra no Supermercado:
```
Débito: Supermercado (5211)
Crédito: Cartão de Crédito (2111)
```

#### Investimento em Ações:
```
Débito: Ações (1211)
Crédito: Banco - Conta Corrente (1112)
```

---

## 🔧 Personalizações Recomendadas

### Adicionar Suas Contas Específicas:

1. **Adicione suas instituições financeiras:**
```
Exemplo:
- Banco Itaú - CC
- Banco Bradesco - Poupança
- Nubank - Investimentos
```

2. **Adicione categorias personalizadas:**
```
Exemplo:
- Cursos de Tecnologia (sob Educação)
- Netflix Família (sob Streaming)
- Aluguel de Box (sob Outras Despesas)
```

3. **Para adicionar nova conta:**
```
1. Vá para: Accounting > Chart of Accounts
2. Clique com botão direito na conta-pai
3. Selecione "Add Child"
4. Preencha:
   - Account Name: Nome da nova conta
   - Account Number: Número sequencial
   - Account Type: Tipo apropriado
5. Salve
```

---

## 📊 Relatórios Úteis para Finanças Pessoais

### Relatórios Nativos do ERPNext:

1. **Balance Sheet** (Balanço Patrimonial)
   - Mostra seus ativos, passivos e patrimônio líquido
   - Path: Accounting > Financial Statements > Balance Sheet

2. **Profit and Loss** (DRE - Demonstração de Resultados)
   - Mostra receitas e despesas
   - Path: Accounting > Financial Statements > Profit and Loss

3. **General Ledger** (Razão Geral)
   - Todas as transações por conta
   - Path: Accounting > General Ledger

4. **Account Balance**
   - Saldo atual de cada conta
   - Path: Accounting > Account Balance

5. **Budget Variance Report**
   - Compare orçado vs realizado
   - Path: Accounting > Budget Variance Report

---

## 💡 Dicas e Boas Práticas

### 1. **Organize por Tags**
```
- Crie tags para categorizar melhor:
  - #essencial
  - #supérfluo
  - #investimento
  - #dívida
```

### 2. **Use Cost Centers**
```
- Crie centros de custo por pessoa da família:
  - Pai
  - Mãe
  - Filho 1
  - Filho 2
  - Família (compartilhado)
```

### 3. **Configure Orçamentos**
```
1. Vá para: Accounting > Budget > New
2. Defina limites mensais para cada categoria
3. ERPNext alertará quando ultrapassar
```

### 4. **Automatize Lançamentos Recorrentes**
```
1. Vá para: Accounting > Journal Entry
2. Marque "Is Recurring"
3. Configure:
   - Frequency: Monthly
   - Start Date: Data início
   - End Date: Data fim
```

### 5. **Integre com Banco (Importação OFX)**
```
- ERPNext suporta importação de extratos bancários OFX
- Path: Accounting > Bank Statement Import
```

---

## 🐛 Solução de Problemas

### Erro: "Duplicate account name"
```
Solução: Cada nome de conta deve ser único na empresa.
- Adicione identificadores: "Banco Itaú - CC" vs "Banco Bradesco - CC"
```

### Erro: "Parent account not found"
```
Solução: Importe as contas na ordem correta:
1. Contas raiz primeiro (Ativos, Passivos, etc.)
2. Depois as contas-filho
```

### Contas não aparecem em relatórios
```
Solução: Verifique:
1. Account Type está correto
2. Root Type está correto
3. Company está atribuída à conta
```

### Não consigo deletar conta antiga
```
Solução: 
- Contas com transações não podem ser deletadas
- Desative a conta: Marque "Disabled" na conta
```

---

## 📞 Recursos Adicionais

### Documentação Oficial:
- [ERPNext Chart of Accounts](https://docs.erpnext.com/docs/user/manual/en/accounts/chart-of-accounts)
- [ERPNext Accounting](https://docs.erpnext.com/docs/user/manual/en/accounts)

### Comunidade:
- [Fórum ERPNext](https://discuss.erpnext.com)
- [Documentação em Português](https://docs.erpnext.com/docs/lang/pt-BR)

---

## ✅ Checklist de Implementação

- [ ] Backup do banco de dados realizado
- [ ] Arquivo CSV baixado e validado
- [ ] Empresa criada ou selecionada
- [ ] Importação realizada com sucesso
- [ ] Hierarquia de contas validada
- [ ] Transação de teste criada
- [ ] Relatórios verificados
- [ ] Contas bancárias específicas adicionadas
- [ ] Orçamentos configurados (opcional)
- [ ] Lançamentos recorrentes configurados (opcional)

---

**Criado em**: Janeiro 2026  
**Versão do Plano de Contas**: 1.0  
**Compatível com**: ERPNext v16+
