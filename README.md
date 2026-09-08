# 🍕 Plataforma Unificada de Gestão de Delivery (PUGD)

> Sistema integrado de alta performance e resiliência operacional para delivery de alimentação: do autoatendimento ao KDS offline-first, despacho dinâmico e compliance fiscal.

---

## 📌 Status do Projeto & Realidade Atual

O projeto encontra-se atualmente na fase de **Especificação Técnica Completa, Modelagem de Domínio (DDD) e Definição Arquitetural** (conclusão da Fase 0 / Preparação para o Marco 1 de Implementação).

Todo o levantamento de requisitos de negócio, matriz de riscos operacionais, arquitetura de software, diagramas UML/Mermaid e especificações de contingência foram exaustivamente detalhados e estruturados no repositório.

* **Fase Atual**: Preparação para o **Marco 1: Core de Domínio e MVP Operacional**.
* **Paradigma Arquitetural**: Monolito Modular baseado em **Clean Architecture**, **Domain-Driven Design (DDD)** e esteira orientada a **TDD**.

---

## 🎯 Proposta de Valor e Problema Operacional

A operação tradicional de restaurantes e dark kitchens enfrenta quatro gargalos crônicos:
1. **Proliferação de Tablets e Telas**: Aluguel de equipamentos de marketplaces consumindo de R$ 300 a R$ 600/mês.
2. **Dupla Digitação e Erro Humano**: Atendentes transcrevendo pedidos manuais, gerando taxas de cancelamento/erro entre 3% e 7%.
3. **Cegueira Operacional**: Falta de visibilidade em tempo real do tempo de preparo na cozinha e sobrecarga nos horários de pico.
4. **Vulnerabilidade Fiscal e de Caixa**: Fechamentos de caixa demorados e falhas na emissão de NFC-e quando a SEFAZ oscila.

### Os 4 Pilares da Solução:
* **🚀 Ingestão Unificada (Order Gateway)**: Cardápio digital web próprio (autoatendimento), lançador ultrarrápido para balcão/telefone (<10s com atalhos de teclado) e ingestão centralizada de marketplaces com controle estrito de idempotência.
* **🍳 Fulfillment Resiliente (KDS Offline-First)**: Tela de cozinha de baixa latência via **Server-Sent Events (SSE)**, com persistência local via IndexedDB para continuar operando mesmo em blackouts de internet.
* **🛵 Logística & Despacho**: Gestão dinâmica de frota de entregadores com validação segura de entrega por código único.
* **💼 Backoffice & Compliance Fiscal**: Fechamento cego de caixa por operador, livro razão em partidas dobradas e emissão assíncrona de NFC-e com contingência offline automática.
* **🤖 IA Pragmática**: Lançador assistido para extração estruturada de pedidos informais de WhatsApp via LLM com *guardrails* e confirmação humana.

---

## 🏛️ Arquitetura e Stack Tecnológica

A arquitetura foi planejada para evoluir pragmaticamente em três estágios:

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

### Tecnologias Oficiais

| Componente | Tecnologia | Papel no Sistema |
| :--- | :--- | :--- |
| **Domain Core** | **Python 3.12+** | Regras de negócio puras, entidades e agregados (zero dependência de frameworks) |
| **API & Delivery** | **FastAPI** | APIs REST assíncronas, OpenAPI automático e streaming SSE |
| **Frontend Web / KDS** | **Next.js 14+ / React / TS** | Interface do Cardápio, KDS offline-first e Lançador Rápido |
| **Estilização & UI** | **Tailwind CSS + shadcn/ui** | Design system acessível, de alto contraste e ergonômico para cozinha |
| **Banco Relacional** | **PostgreSQL 16+** | Schemas isolados por bounded context e transações ACID |
| **Cache & Idempotência** | **Redis 7+** | Travas distribuídas (`X-Idempotency-Key`), rate limiting e filas voláteis |
| **IA & Parsers** | **LLMs Leves (Gemini / OpenRouter)** | Extração semântica de pedidos de WhatsApp com limiar de confiança (>95%) |
| **Testes & Qualidade** | **Pytest + Testcontainers** | TDD estrito com pirâmide de testes e linters de arquitetura |

---

## 📂 Índice da Documentação do Projeto

Todo o projeto possui documentação aprofundada organizada no diretório [`arquivos.md/`](./arquivos.md/):

| Documento | Descrição |
| :--- | :--- |
| 📖 **[Proposta Final Consolidada](./arquivos.md/proposta_final.md)** | **Documento mestre completo** unificando todas as seções e decisões do software |
| 📋 **[1. Introdução e Visão Geral](./arquivos.md/introducao_e_visao_geral.md)** | Dores de mercado, proposta de valor e métricas de ROI |
| 📝 **[2. Engenharia de Requisitos](./arquivos.md/requisitos.md)** | Requisitos Funcionais (RF01 a RF15) e Não Funcionais (RNF01 a RNF10) |
| 📊 **[3. Diagramas Técnicos](./arquivos.md/diagramas_tecnicos.md)** | Casos de Uso, Diagrama de Classes, DER, FSM de Estados e Sequência |
| 🏗️ **[4. Arquitetura de Software](./arquivos.md/arquitetura_software.md)** | Comparativo Monolito vs Microsserviços vs Cell-Based e especificações técnicas |
| ⚙️ **[5. Decisões Críticas de Engenharia](./arquivos.md/decisoes_criticas.md)** | Idempotência, SSE vs Polling, relógios lógicos na FSM e observabilidade |
| 🛡️ **[6. Resolução de Lacunas Operacionais](./arquivos.md/resolucao_lacunas.md)** | KDS Offline (IndexedDB), Fechamento Cego, Contingência NFC-e e Despacho |
| 💡 **[7. Inovação e IA Pragmática](./arquivos.md/inovacao_ia.md)** | Parser inteligente de pedidos de WhatsApp e Co-pilot de catálogo |
| 🧪 **[9. Implementação, Clean Arch & TDD](./arquivos.md/implementacao_ddd_clean_arch_tdd.md)** | Árvore de diretórios Clean Architecture e metodologia de testes |
| 🗺️ **[10. Roadmap de Execução & Riscos](./arquivos.md/roadmap_execucao_riscos.md)** | Fases de entrega, marcos técnicos e matriz de mitigação de riscos |

---

## 🧭 Estrutura de Pastas do Código (Padrão Clean Architecture)

Quando o desenvolvimento do código-fonte iniciar, a estrutura de diretórios seguirá:

```
src/
├── domain/                  # Camada 1: Entidades puras, Value Objects e Ports (Zero libs externas)
│   ├── entities/            # Order, OrderItem, CashRegister, Customer
│   ├── value_objects/       # Money, CpfCnpj, Address
│   ├── ports/               # OrderRepositoryPort, FiscalPort, PaymentPort
│   └── exceptions/          # DomainExceptions (ex: InvalidStateTransitionError)
│
├── application/             # Camada 2: Casos de Uso e Orquestração
│   ├── use_cases/           # CreateOrderUseCase, AdvanceKdsUseCase, ProcessFiscalDocUseCase
│   └── dtos/                # Data Transfer Objects de entrada e saída
│
├── adapters/                # Camada 3: Interface Adapters
│   ├── controllers/         # Endpoints FastAPI, Handlers SSE
│   ├── repositories/        # Implementações PostgreSQL com SQLAlchemy / SQL nativo
│   └── gateways/            # Provedores fiscais, adquirentes e serviços externos
│
└── infra/                   # Camada 4: Frameworks, Drivers e Configuração
    ├── config/              # Variáveis de ambiente e Settings
    ├── database/            # Conexões e migrações Alembic
    └── workers/             # Processamento assíncrono em segundo plano
```

---

## 🛣️ Próximos Passos (Marco 1)

O próximo ciclo de trabalho foca no início do desenvolvimento do MVP:

1. **Configuração do Repositório e Tooling**:
   - Ambiente virtual Python 3.12+, Poetry/uv, linter (`ruff`), formatador e `pytest`.
   - Setup do `docker-compose.yml` para serviços locais (PostgreSQL 16 e Redis 7).
2. **Núcleo de Domínio**:
   - Modelagem de entidades `Order`, `OrderItem`, `Payment` e Máquina de Estados Finita (FSM).
   - Suíte de testes unitários isolados para transições de estado de pedidos e regras de cálculo.
3. **Order Gateway & Idempotência**:
   - Endpoints de submissão de pedidos com FastAPI e validação de chaves idempotentes no Redis.
4. **KDS Core**:
   - Canal de streaming SSE e protótipo de tela de cozinha receptora.
