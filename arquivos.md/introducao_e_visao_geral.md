# Documento de Especificação de Software: Plataforma Unificada de Gestão de Delivery

## 1. Introdução e Visão Geral

This document serves as the definitive specification for the **Plataforma Unificada de Gestão de Delivery** (PUGD). It defines the software architecture, requirements, and technical design following Domain-Driven Design (DDD) principles and Clean Architecture patterns.

**Propósito:** Fornecer uma base única e rastreável para o desenvolvimento, implementação e manutenção do sistema de gestão de delivery.

**Escopo:** Integração de catálogo, captura de pedidos, fulfillment (preparo e entrega), gestão de caixa, emissão fiscal (NFC-e/NF-e) e monitoramento de operações.

**Premissa Fundamental:**
> *"A operação física do restaurante é soberana: a cozinha não pode parar, o caixa não pode aceitar inconsistências, o fisco não pode ser negligenciado e a simplicidade de uso no calor da operação sobrepõe qualquer preciosismo técnico."*

---

### 1.1 Visão Geral & Proposta de Valor

#### 1.1.1 O Problema Operacional Real
A operação diária de um delivery de alimentação enfrenta:
- **Proliferação de Telas e Tablets:** Múltiplos dispositivos gerando aluguel e poluição física no ponto de venda (R$ 150 a R$ 300/tablet/mês).
- **Dupla Digitação e Retrabalho Humano:** Atendentes transcrevem manualmente pedidos causando erros em horários de pico (taxa de retrabalho entre 3% e 7%).
- **Falta de Visibilidade em Tempo Real:** Cozinha desconhece carga real de trabalho; equipe de despacho distribui entregadores sem visibilidade de rota.
- **Cegueira Gerencial e Fisco:** Fechamentos de caixa demorados, perda de conciliação entre repasses e realidade contábil, além de vulnerabilidade legal por falhas em NFC-e/NF-e sob contingência.

#### 1.1.2 A Solução: Ecossistema Unificado
Um ecossistema digital integrado sustentado por três pilares:
1. **Captura (Order Gateway):** Cardápio digital web + agregador de pedidos externos + Lançador de alta velocidade.
2. **Operação (Fulfillment & Logistics):** KDS resiliente com suporte offline-first e módulo de Despacho dinâmico.
3. **Reconciliação (Backoffice & Fiscal):** Fechamento cego de caixa, conciliação de taxas, split de pagamentos e compliance fiscal automático.

#### 1.1.3 Framework de Retorno Sobre o Investimento (ROI)
| Alavanca de Valor | Métrica de Impacto | Impacto Estimado |
| :--- | :--- | :--- |
| **Eliminação de Tablets** | Redução de custo fixo | Economia de R$ 300 a R$ 600 / mês |
| **Deduplicação e Zero Retrabalho** | Queda de cancelamentos e perdas | Economia de R$ 1.200 a R$ 2.500 / mês |
| **Cardápio Próprio (Autoatendimento)** | Economia de comissão (12% a 27%) | Retenção de margem líquida no faturamento |
| **Otimização de Despacho** | Redução de tempo ocioso de motoboys | Aumento na capacidade e agilidade |

---

### 1.2 Framework de Retorno sobre o Investimento (ROI)

| Alavanca de Valor | Métrica de Impacto | Fonte de Dados | Impacto Estimado na Operação |
| :--- | :--- | :--- | :--- |
| **Eliminação de Tablets** | Redução de custo fixo | Contratos de locação/equipamento | Economia de R$ 300 a R$ 600 / mês |
| **Deduplicação e Zero Retrabalho** | Queda de cancelamentos e perdas | Histórico de refações e estornos | Economia de R$ 1.200 a R$ 2.500 / mês em insumos |
| **Cardápio Próprio (Autoatendimento)** | Economia de comissão (12% a 27%) | Relatório de vendas marketplace | Retenção de margem líquida direta no faturamento |
| **Otimização de Despacho** | Redução de tempo ocioso de motoboys | Relatório de corridas por turno | Aumento na capacidade e agilidade de entregas |