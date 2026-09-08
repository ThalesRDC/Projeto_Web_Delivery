# Documento de Especificação de Software: Plataforma Unificada de Gestão de Delivery

## 10. Roadmap de Execução, Fases e Matriz de Riscos

### 10.1 Fases do Projeto

#### Fase 1: MVP Essencial - Foco em Estabilidade Operacional
*Objetivo Central:* Eliminar os tablets de balcão e garantir que a cozinha opere com 100% de confiabilidade.
- [ ] Arquitetura de Monolito Modular e configuração de schemas de banco de dados.
- [ ] Interface do Lançador Rápido de pedidos para balcão com atalhos de teclado.
- [ ] Cardápio Digital Web (PWA responsivo para autoatendimento).
- [ ] KDS de Cozinha com WebSockets/SSE e suporte a persistência local em IndexedDB.
- [ ] Controle de Caixa básico com abertura, sangrias e fechamento cego.
- [ ] Emissão de NFC-e com contingência offline integrada via parceiro fiscal.

#### Fase 2: Expansão Operacional e Logística
*Objetivo Central:* Centralizar frotas de entrega e aprofundar a inteligência do negócio.
- [ ] Módulo completo de Despacho com rastreamento de entregadores e validação por código.
- [ ] Ingestor de webhooks unificado para iFood e canais terceiros em fila única de preparo.
- [ ] Painel de relatórios analíticos: Curva ABC de produtos e Ticket Médio por canal.
- [ ] Workflow automatizado para disputas de clientes ("Não recebi meu pedido").
- [ ] Testes do Lançador Assistido com IA para pedidos de WhatsApp em ambiente controlado.

#### Fase 3: Escala e Robustez Avançada
*Objetivo Central:* Amadurecimento arquitetural para suportar alto volume com isolamento operacional.
- [ ] Avaliação de desacoplamento de microsserviços orientados a eventos via Outbox Pattern.
- [ ] Split de pagamento automatizado com adquirentes e repasse a entregadores.
- [ ] Preparação de esteira Cell-Based para isolamento operacional em cenários de alta demanda.
- [ ] Auditoria de conformidade contínua e rotinas avançadas de observabilidade.

---

### 10.2 Trilha Sequencial de Marcos e Entregas Técnicas

```
MARCO 1: FUNDAÇÕES LEGAIS, ARQUITETURA E CORE OPERACIONAL
├─ Modelagem do banco relacional, entidades de domínio e testes de transição de estado.
├─ Implementação do Order Gateway (FastAPI) com suporte estrito a idempotência.
├─ Desenvolvimento do KDS (Next.js) com SSE e sincronização local via IndexedDB.
└─ Integração com provedor fiscal (NFC-e) e implementação da contingência offline.

MARCO 2: FLUXOS TRANSVERSAIS, INTEGRAÇÕES E LOGÍSTICA
├─ Construção do módulo de Despacho e interface responsiva para entregadores.
├─ Adaptador de webhooks para captura unificada de iFood e canais terceiros.
├─ Implementação do motor de split financeiro e partidas dobradas no caixa.
└─ Esteira de migração de catálogos via planilha e validação na operação do próprio negócio.

MARCO 3: VALIDAÇÃO OPERACIONAL, POLIMENTO DE UX E CONSOLIDAÇÃO
├─ Teste de carga e simulação de blackout de rede durante horário de pico da cozinha.
├─ Ajustes ergonômicos de UX no KDS e Lançador com base no uso real da equipe de operação.
├─ Ativação dos dashboards analíticos (Curva ABC e faturamento comparativo).
└─ Homologação final, documentação de suporte e operação plena no ambiente de produção.
```

---

### 10.3 Matriz de Riscos e Planos de Mitigação

| Risco Identificado | Severidade | Probabilidade | Plano de Mitigação Preventivo |
| :--- | :--- | :--- | :--- |
| **Queda de Internet em Horário de Pico** | Crítica | Alta | Arquitetura offline-first completa no KDS com persistência em IndexedDB e sincronização automática por Vector Clocks. |
| **Rejeição do Sistema pela Cozinha** | Alta | Média | Interface industrial com alvos de toque de 56dp, alto contraste (4.5:1), feedback visual/sonoro e zero necessidade de digitação. |
| **Indisponibilidade dos Serviços da SEFAZ** | Crítica | Alta | Emissão assíncrona automática em modo de Contingência Offline com geração local de QR-Code e transmissão posterior em lote. |
| **Duplicação de Pedidos por Retentativas Externas** | Alta | Alta | Filtro de idempotência obrigatório com chave única e trava atômica em memória (Redis) antes da gravação no banco. |
| **Over-Engineering Precoce no MVP** | Média | Média | Adoção estrita de Monolito Modular na Fase 1; microsserviços apenas após validação de escala e maturidade de testes. |
| **Aumento de Custos ou Descontinuidade de Fornecedor** | Alta | Baixa | Isolamento de 100% das integrações externas através do padrão Adapter com factory configurável por variáveis de ambiente. |