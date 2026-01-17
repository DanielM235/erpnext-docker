# Plano de Contas vs Centros de Custo no ERPNext

## Resumo Executivo

**Plano de Contas** e **Centros de Custo** são duas dimensões complementares de análise financeira no ERPNext:

- **Plano de Contas**: responde à pergunta **"O QUÊ?"** - qual é a natureza da receita ou despesa
- **Centros de Custo**: responde à pergunta **"QUEM/ONDE?"** - quem é responsável ou onde foi gasto

**Exemplo prático:**
- Despesa de R$ 150 no supermercado:
  - **Conta**: 5211 - Supermercado (Alimentação)
  - **Centro de Custo**: Casa Geral

## 1. Plano de Contas (Chart of Accounts)

### O que é?

Estrutura hierárquica que classifica as transações financeiras pela **natureza** da operação.

### Estrutura

```
Despesas (5000)
└── Despesas Variáveis (5200)
    └── Alimentação (5210)
        ├── Supermercado (5211)
        ├── Feira (5212)
        ├── Padaria (5213)
        └── Restaurantes (5215)
```

### Características

- **Obrigatório**: toda transação DEVE ter uma conta contábil
- **Único**: cada transação tem uma única conta principal
- **Permanente**: estrutura estável ao longo do tempo
- **Regulamentado**: segue padrões contábeis (CPC, IFRS)
- **Hierárquico**: permite agregação de valores

### Quando usar?

✅ Análise por tipo de gasto (quanto gastei em alimentação?)  
✅ Demonstrações financeiras (DRE, Balanço)  
✅ Comparação com orçamentos por categoria  
✅ Análise de tendências (alimentação cresceu 15% vs ano anterior)

### Exemplo para Finanças Pessoais

```csv
Código  | Conta                  | Tipo
--------|------------------------|------------
5211    | Supermercado          | Despesa
5215    | Restaurantes          | Despesa
5221    | Combustível           | Despesa
5232    | Consultas Médicas     | Despesa
```

**Transação:**
- Data: 15/01/2026
- Conta: 5211 - Supermercado
- Valor: R$ 450,00
- Centro de Custo: (opcional)

---

## 2. Centros de Custo (Cost Centers)

### O que é?

Estrutura que divide a organização em **unidades de responsabilidade** ou **áreas de atividade**.

### Estrutura Empresarial

```
Empresa (Principal)
├── Vendas
├── Marketing
├── Produção
├── Administrativo
└── TI
```

### Estrutura Pessoal/Familiar

```
DM-CASA (Principal)
├── Pai
├── Mãe
├── Filho 1
├── Filho 2
├── Casa Geral
│   ├── Cozinha
│   ├── Manutenção
│   └── Utilidades
├── Veículos
│   ├── Carro 1
│   └── Carro 2
├── Educação Filhos
└── Lazer Família
```

### Características

- **Opcional**: pode ser usado ou não
- **Múltiplo**: mesma transação pode ter vários centros de custo
- **Flexível**: pode ser alterado conforme necessidade
- **Analítico**: ferramenta de gestão, não contábil
- **Percentual**: permite divisão proporcional (30% pai, 70% mãe)

### Quando usar?

✅ Análise por responsável (quanto o filho 1 gastou?)  
✅ Controle de orçamento por pessoa/projeto  
✅ Rateio de despesas compartilhadas  
✅ Prestação de contas (quanto gastei no carro?)

### Exemplo para Finanças Pessoais

**Transação simples:**
- Data: 15/01/2026
- Conta: 5211 - Supermercado
- Valor: R$ 450,00
- Centro de Custo: **Casa Geral** (100%)

**Transação com rateio:**
- Data: 16/01/2026
- Conta: 5215 - Restaurantes
- Valor: R$ 200,00
- Centros de Custo:
  - **Pai**: 50% (R$ 100)
  - **Mãe**: 50% (R$ 100)

**Transação de veículo:**
- Data: 17/01/2026
- Conta: 5221 - Combustível
- Valor: R$ 250,00
- Centro de Custo: **Carro 1** (100%)

---

## 3. Comparação Detalhada

| Aspecto | Plano de Contas | Centros de Custo |
|---------|-----------------|------------------|
| **Pergunta** | O QUÊ foi gasto? | QUEM/ONDE gastou? |
| **Obrigatoriedade** | Obrigatório | Opcional |
| **Unicidade** | Uma conta por linha | Múltiplos centros possíveis |
| **Finalidade** | Demonstrações contábeis | Análise gerencial |
| **Estabilidade** | Alta (estrutura permanente) | Média (pode mudar) |
| **Regulamentação** | Segue normas contábeis | Livre definição |
| **Rateio** | Não permite | Permite rateio proporcional |
| **Hierarquia** | Fixa e regulamentada | Flexível |

---

## 4. Casos de Uso Práticos

### Caso 1: Família sem Centros de Custo

**Vantagens:**
- Configuração simples e rápida
- Menos trabalho no lançamento de transações
- Foco na natureza dos gastos

**Análises possíveis:**
- Quanto gastamos em alimentação? ✅
- Quanto gastamos em saúde? ✅
- Evolução mensal por categoria ✅

**Limitações:**
- Não consegue identificar quem gastou ❌
- Difícil ratear despesas compartilhadas ❌
- Sem controle por projeto/atividade ❌

### Caso 2: Família com Centros de Custo

**Vantagens:**
- Controle detalhado por pessoa/atividade
- Rateio preciso de despesas compartilhadas
- Orçamento individual por membro
- Prestação de contas facilitada

**Análises possíveis:**
- Quanto gastamos em alimentação? ✅
- Quanto o filho 1 gastou no mês? ✅
- Quanto gastamos no Carro 1? ✅
- Despesas da viagem para a praia? ✅

**Complexidade:**
- Mais campos para preencher
- Necessita planejamento da estrutura
- Requer disciplina no lançamento

---

## 5. Recomendações de Uso

### Para Finanças Pessoais Simples

```
Estrutura Mínima:
├── Plano de Contas: SIM (detalhado)
└── Centros de Custo: NÃO ou estrutura simples
```

**Centros de Custo simples:**
```
DM-CASA (Principal)
├── Pessoal
└── Casa
```

### Para Finanças Familiares Complexas

```
Estrutura Completa:
├── Plano de Contas: SIM (detalhado)
└── Centros de Custo: SIM (por pessoa/projeto)
```

**Centros de Custo detalhados:**
```
DM-CASA (Principal)
├── Pai
├── Mãe
├── Filho 1
├── Filho 2
├── Casa Geral
├── Carro 1
├── Carro 2
├── Viagens
└── Investimentos
```

---

## 6. Exemplos de Transações

### Exemplo 1: Conta de Luz (despesa compartilhada)

**Sem Centro de Custo:**
```
Data: 20/01/2026
Conta Débito: 5131 - Energia Elétrica
Conta Crédito: 1112 - Banco - Conta Corrente
Valor: R$ 180,00
```

**Com Centro de Custo:**
```
Data: 20/01/2026
Conta Débito: 5131 - Energia Elétrica
Conta Crédito: 1112 - Banco - Conta Corrente
Valor: R$ 180,00
Centro de Custo: Casa Geral (100%)
```

### Exemplo 2: Jantar em Restaurante (rateado)

**Com Rateio por Centro de Custo:**
```
Data: 21/01/2026
Conta Débito: 5215 - Restaurantes
Conta Crédito: 2111 - Cartão de Crédito
Valor: R$ 280,00

Rateio Centro de Custo:
- Pai: 40% (R$ 112,00)
- Mãe: 40% (R$ 112,00)
- Filho 1: 20% (R$ 56,00)
```

### Exemplo 3: Abastecimento do Veículo

**Com Centro de Custo por Veículo:**
```
Data: 22/01/2026
Conta Débito: 5221 - Combustível
Conta Crédito: 2111 - Cartão de Crédito
Valor: R$ 320,00
Centro de Custo: Carro 1 (100%)
```

---

## 7. Configuração no ERPNext v16

### 7.1 Criar Plano de Contas

**Passo 1:** Importar plano de contas
```
Menu: Data Import
DocType: Account
File: plano_de_contas_pessoal_br_v16.csv
```

**Passo 2:** Verificar estrutura
```
Menu: Chart of Accounts
Company: Finanças Pessoais
```

### 7.2 Criar Centros de Custo

**Método 1: Manual**
```
1. Ctrl+K → "New Cost Center"
2. Cost Center Name: Casa Geral
3. Parent Cost Center: DM-CASA - FP (principal)
4. Save
```

**Método 2: Importação CSV**

```csv
"Cost Center Name","Parent Cost Center","Company"
"DM-CASA - FP","","Finanças Pessoais"
"Pai - FP","DM-CASA - FP","Finanças Pessoais"
"Mãe - FP","DM-CASA - FP","Finanças Pessoais"
"Filho 1 - FP","DM-CASA - FP","Finanças Pessoais"
"Casa Geral - FP","DM-CASA - FP","Finanças Pessoais"
"Carro 1 - FP","DM-CASA - FP","Finanças Pessoais"
```

**Observação:** ERPNext adiciona automaticamente " - SIGLA" no final (FP = Finanças Pessoais)

### 7.3 Usar em Transações

**Journal Entry com Centro de Custo:**
```
Menu: Journal Entry
Accounts:
  Linha 1:
    - Account: 5211 - Supermercado
    - Debit: R$ 450,00
    - Cost Center: Casa Geral - FP
  
  Linha 2:
    - Account: 1112 - Banco - Conta Corrente
    - Credit: R$ 450,00
```

---

## 8. Relatórios Comparativos

### Relatório por Conta (sem Centro de Custo)

```
Profit and Loss Statement
Janeiro 2026

Receitas                           R$ 15.000,00
  Salário                          R$ 12.000,00
  Investimentos                    R$ 3.000,00

Despesas                           R$ 10.500,00
  Alimentação                      R$ 2.800,00
    - Supermercado                 R$ 1.800,00
    - Restaurantes                 R$ 1.000,00
  Transporte                       R$ 1.500,00
  Moradia                          R$ 3.200,00
  Saúde                            R$ 1.800,00
  Outras                           R$ 1.200,00

Resultado                          R$ 4.500,00
```

### Relatório por Centro de Custo

```
Budget vs Actual - Cost Center
Janeiro 2026

Centro de Custo          Orçamento    Real         Diferença
Pai                      R$ 3.000     R$ 3.450     -R$ 450 ❌
Mãe                      R$ 2.500     R$ 2.200     +R$ 300 ✅
Filho 1                  R$ 1.500     R$ 1.650     -R$ 150 ❌
Casa Geral               R$ 4.000     R$ 3.800     +R$ 200 ✅
Carro 1                  R$ 1.200     R$ 1.400     -R$ 200 ❌

TOTAL                    R$ 12.200    R$ 12.500    -R$ 300 ❌
```

### Relatório Cruzado (Conta × Centro de Custo)

```
Análise Detalhada - Janeiro 2026

Conta: 5211 - Supermercado         Total: R$ 1.800,00
  Casa Geral                       R$ 1.800,00    (100%)

Conta: 5215 - Restaurantes         Total: R$ 1.000,00
  Pai                              R$ 400,00      (40%)
  Mãe                              R$ 400,00      (40%)
  Filho 1                          R$ 200,00      (20%)

Conta: 5221 - Combustível          Total: R$ 900,00
  Carro 1                          R$ 600,00      (67%)
  Pai                              R$ 300,00      (33%)
```

---

## 9. Quando Usar Cada Abordagem

### Use APENAS Plano de Contas se:

- [ ] Você mora sozinho
- [ ] Quer apenas controlar categorias de gastos
- [ ] Busca simplicidade máxima
- [ ] Não precisa atribuir gastos a pessoas/projetos
- [ ] Não precisa ratear despesas

### Use Plano de Contas + Centros de Custo se:

- [x] Família com múltiplas pessoas
- [x] Precisa controlar gastos por pessoa
- [x] Tem múltiplos veículos ou imóveis
- [x] Quer orçamento individual por membro
- [x] Precisa ratear despesas compartilhadas
- [x] Tem projetos específicos (reforma, viagem)
- [x] Quer prestação de contas detalhada

---

## 10. Migração Gradual

Você pode começar simples e evoluir:

### Fase 1: Básico (Mês 1-3)
```
✅ Plano de Contas completo
❌ Sem Centros de Custo
```

### Fase 2: Intermediário (Mês 4-6)
```
✅ Plano de Contas completo
✅ Centros de Custo simples: Pessoal, Casa, Carro
```

### Fase 3: Avançado (Mês 7+)
```
✅ Plano de Contas completo
✅ Centros de Custo detalhados por pessoa/projeto
✅ Orçamentos por centro de custo
✅ Rateios automáticos
```

---

## 11. Dicas Importantes

### ✅ Boas Práticas

1. **Plano de Contas**: mantenha estável, não altere frequentemente
2. **Centros de Custo**: ajuste conforme necessidade evolui
3. **Nomenclatura**: seja consistente ("Pai - FP", "Mãe - FP")
4. **Hierarquia**: não exagere nos níveis (máximo 3 níveis)
5. **Documentação**: registre o objetivo de cada centro de custo

### ❌ Erros Comuns

1. **Confundir as duas estruturas** - são complementares, não alternativas
2. **Centro de custo muito detalhado** - começa simples
3. **Esquecer de atribuir centro de custo** - cria inconsistências nos relatórios
4. **Mudar estrutura frequentemente** - dificulta análises históricas
5. **Não usar hierarquia** - perde capacidade de agregação

---

## 12. Conclusão

**Plano de Contas** e **Centros de Custo** são ferramentas **complementares**:

| Para saber... | Use... |
|---------------|--------|
| Quanto gastei em alimentação? | **Plano de Contas** |
| Quanto o filho gastou? | **Centros de Custo** |
| Qual categoria mais cresceu? | **Plano de Contas** |
| Qual pessoa mais gastou? | **Centros de Custo** |
| Demonstração financeira? | **Plano de Contas** |
| Orçamento por pessoa? | **Centros de Custo** |

**Recomendação Final:**
1. **Sempre use Plano de Contas** (obrigatório e essencial)
2. **Adicione Centros de Custo** quando precisar controlar "quem/onde"
3. **Comece simples** e evolua conforme necessidade

---

## Referências

- ERPNext v16 Documentation: Accounting
- ERPNext v16 Documentation: Cost Center
- Manual de Contabilidade Pessoal
- Estrutura do Plano de Contas Brasileiro

---

*Documento criado em: 16/01/2026*  
*Versão: 1.0*  
*ERPNext: v16.0.1*
