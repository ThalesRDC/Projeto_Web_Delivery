# Documento de Especificação de Software: Plataforma Unificada de Gestão de Delivery

## 9. Estratégia de Implementação e Qualidade (Clean Arch & TDD)

### 9.1 Estrutura de Diretórios Recomendada
O código-fonte segue estritamente a separação da Clean Architecture:

```
src/
├── domain/                  # Camada 1: Entidades puras, Value Objects e Interfaces de Repositório (Zero libs externas)
│   ├── entities/            # Order, OrderItem, CashRegister, Customer
│   ├── value_objects/       # Money, CpfCnpj, Address, VectorClock
│   ├── ports/               # OrderRepositoryPort, FiscalPort, PaymentPort
│   └── exceptions/          # DomainExceptions (ex: InvalidStateTransitionError)
│
├── application/             # Camada 2: Casos de Uso (Orquestração das regras de negócio)
│   ├── use_cases/           # CreateOrderUseCase, AdvanceKdsUseCase, ProcessFiscalDocUseCase
│   └── dtos/                # Data Transfer Objects de entrada e saída
│
├── adapters/                # Camada 3: Interface Adapters (Controllers, Serializadores e Implementações)
│   ├── controllers/         # Routers HTTP do FastAPI, Handlers de SSE/WebSocket
│   ├── repositories/        # OrderRepositoryPostgres (Implementação usando SQL / ORM)
│   └── gateways/            # TecSpeedFiscalAdapter, TwilioSmsAdapter, PagarmePaymentAdapter
│
└── infra/                   # Camada 4: Configurações de infraestrutura, Migrações e Inicialização
    ├── config/              # Variáveis de ambiente e Settings
    ├── database/            # Conexão de banco e migrações Alembic
    └── workers/             # Tarefas de background assíncronas (Celery / ARQ)
```

### 9.2 Disciplina de Testes Orientada pelo TDD (Test-Driven Development)
A implementação é orientada pela **Pirâmide de Testes**, com ciclo estrito de *Red-Green-Refactor*:

1. **Testes Unitários de Domínio (Rápidos e Isolados)**:
   - Validam regras intrínsecas das entidades (cálculo de descontos, validação de transições de status da FSM, cálculos de split de pagamentos).
   - Não tocam banco de dados, rede ou arquivos. Execução de centenas de testes em milissegundos usando `pytest`.

2. **Testes de Casos de Uso (Application)**:
   - Testam a orquestração utilizando *In-Memory Repositories* ou fakes simples para portas de saída, garantindo que o caso de uso coordene entidades e salve o resultado correto.

3. **Testes de Integração (Adapters e Banco de Dados)**:
   - Executados contra instâncias de teste do PostgreSQL (via `testcontainers` ou banco efêmero de CI).
   - Validam queries complexas de agregação de relatórios, precisão de fechamento de caixa e integridade de restrições relacionais.

4. **Testes E2E Críticos**:
   - Fluxo completo automatizado: criação de pedido via API -> chegada no SSE do KDS -> mudança para "Pronto" -> registro fiscal gerado.

**Pirâmide de Testes Esperada:** Muitos testes unitários de domínio/use case, poucos de integração, pouquíssimos e2e.

**Rastreabilidade:** Cada RF da seção de requisitos deve ter pelo menos um teste que comprove aceitação (RF → caso de uso → teste).