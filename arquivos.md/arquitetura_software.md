# Documento de Especificação de Software: Plataforma Unificada de Gestão de Delivery

## 4. Arquitetura de Software & Evolução de Paradigmas

### 4.1 Análise Comparativa de Abordagens Arquiteturais

```
  [ Fase 1: MVP ]                      [ Fase 2: Escala ]                    [ Fase 3: Alta Escala ]
┌─────────────────────────┐          ┌─────────────────────────┐          ┌─────────────────────────┐
│     MONOLITO MODULAR    │          │     MICROSSERVIÇOS      │          │       CELL-BASED        │
│   (Clean Architecture)  │   ───▶   │  (Orientado a Eventos)  │   ───▶   │     (ALTA ROBUSTEZ)     │
│ - Transações ACID       │          │ - Bounded Contexts      │          │ - Clusters por Região   │
│ - Banco Único (Schemas) │          │ - Kafka / RabbitMQ      │          │ - Isolamento de Falhas  │
│ - Simplicidade de Deploy│          │ - Outbox Pattern & Sagas│          │ - Bulkhead Pattern      │
└─────────────────────────┘          └─────────────────────────┘          └─────────────────────────┘
```

#### Abordagem 1: O Monolito Modular (Fase 1 - Escolha Inicial Pragmática)
Para a ampla maioria das operações de delivery, um Monolito Modular bem estruturado com Clean Architecture é a melhor decisão de engenharia.
- **Estrutura:** Um único binário executável e um banco relacional PostgreSQL, porém com isolamento rígido por domínios no código-fonte. O módulo de Logística jamais faz JOIN na tabela do módulo de Pedidos; a comunicação ocorre estritamente via interfaces e contratos de domínio interno.
- **Vantagem Vital (Transações ACID):** Operações críticas como cancelamento de pedido (estorno financeiro + reposição de estoque + cancelamento de despacho) são executadas em uma única transação atômica de banco de dados (`BEGIN ... COMMIT`). Se houver falha, o rollback é instantâneo.
- **Mitigação de Riscos:** Implementação de testes de arquitetura (usando linters de dependência em Python, como `import-linter` ou regras pytest) para impedir acoplamento indevido entre módulos.

#### Abordagem 2: Microsserviços Orientados a Eventos (Fase 2 - Escala e Alta Carga)
Aplicada quando o volume de requisições de leitura (dashboards e catálogo) ameaça a estabilidade dos módulos de escrita operacional de baixa latência (KDS e Ingestão).
- **Estrutura:** Separação física dos contextos delimitados em serviços independentes com bancos próprios, comunicando-se via mensageria assíncrona (RabbitMQ ou Apache Kafka).
- **Trade-off Crítico (Consistência Eventual):** Atrasos no processamento de filas de estoque podem resultar na venda de produtos esgotados. Torna-se obrigatório o desenvolvimento de rotinas automáticas de compensação (estorno e comunicação proativa ao cliente).
- **Padrão Obrigatório (Transactional Outbox Pattern):** Para resolver o problema da dupla escrita (salvar no banco e publicar na fila), o evento de domínio é registrado na mesma transação local do banco de dados na tabela `outbox_events` e publicado de forma assíncrona e confiável por um worker dedicado.

#### Abordagem 3: Arquitetura Baseada em Células (Cell-Based - Fase 3)
Padrão de referência para cenários futuros de grande expansão territorial e altíssimo volume operacional.
- **Estrutura:** Divisão da infraestrutura em células estanques e autossuficientes por polo de atendimento. Cada célula contém seu próprio cluster de aplicação e banco de dados.
- **Vantagem Crucial (Isolamento de Falhas / Bulkhead):** Picos sazonais extremos em uma praça operacional ficam confinados à sua própria célula, preservando a estabilidade e a responsividade de outras unidades do ecossistema.
- **Trade-off:** Maior complexidade de roteamento global de tráfego e exigência de automação de infraestrutura.

### 4.2 Stack Tecnológica Oficial
- **Backend Core:** Python 3.12+ puro para o núcleo de domínio (Zero dependências de framework no coração das regras de negócio).
- **Mecanismo de Entrega de Dados / API:** FastAPI (alta performance assíncrona, documentação OpenAPI automática, validação e injeção de dependência nativa).
- **Frontend / Client:** Next.js 14+ (App Router), TypeScript, Tailwind CSS e componentes acessíveis baseados em Radix UI / shadcn/ui.
- **Banco de Dados Principal:** PostgreSQL 16+ com particionamento de tabelas por data/tenant e schemas separados por contexto de domínio.
- **Cache & Fila de Curto Prazo:** Redis 7+ para controle de idempotência, rate-limiting e sessões de WebSocket/SSE.
- **Validação e Tipagem de Dados:** Pydantic v2 garantindo validação estrita entre camadas.