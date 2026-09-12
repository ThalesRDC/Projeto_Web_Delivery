# Documento de Especificação de Software: Plataforma Unificada de Gestão de Delivery

## 8. Modelagem Visual do Sistema (Diagramas Técnicos)

### 8.1 Diagrama de Casos de Uso Geral

```mermaid
flowchart LR
    Cliente((Cliente Final))
    Atendente((Atendente PDV))
    Cozinheiro((Cozinheiro))
    Entregador((Entregador))
    Admin((Administrador))
    Sefaz((SEFAZ Fiscal))
    Ifood((iFood API))

    subgraph Ingestao["Contexto de Ingestão"]
        UC01[Consultar Cardápio Digital]
        UC02[Realizar Pedido Web]
        UC03[Lançar Pedido Rápido PDV]
        UC04[Ingerir Webhook Integrador]
    end

    subgraph Fulfillment["Contexto de Cozinha"]
        UC05[Visualizar Fila no KDS]
        UC06[Avançar Etapa de Preparo]
        UC07[Sincronizar Ações Offline]
    end

    subgraph Logistica["Contexto de Despacho"]
        UC08[Alocar Pedido a Entregador]
        UC09[Registrar Confirmação de Entrega]
    end

    subgraph FinanceiroFiscal["Contexto Backoffice & Fiscal"]
        UC10[Efetuar Fechamento de Caixa]
        UC11[Emitir NFC-e Eletrônica]
        UC12[Consultar Relatórios e Curva ABC]
    end

    Cliente --> UC01
    Cliente --> UC02
    Atendente --> UC03
    Ifood --> UC04
    Cozinheiro --> UC05
    Cozinheiro --> UC06
    Cozinheiro --> UC07
    Atendente --> UC08
    Entregador --> UC09
    Atendente --> UC10
    Admin --> UC12
    Sefaz --> UC11
    UC02 -.->|include| UC11
    UC03 -.->|include| UC11
    UC11 --> Sefaz
```

---

### 8.2 Diagrama de Estados do Pedido (Ciclo de Vida Completo)

```mermaid
stateDiagram-v2
    [*] --> Criado : Pedido submetido (Web / PDV / iFood)
    Criado --> EmPreparo : Cozinha aceita no KDS
    Criado --> Cancelado : Loja recusa ou timeout de aceite
    
    EmPreparo --> Pronto : Cozinheiro conclui preparo
    EmPreparo --> Cancelado : Falta de insumo / Cancelamento emergencial

    Pronto --> Despachado : Atribuído a motoboy e saiu para entrega
    Pronto --> Entregue : Retirada no balcão presencial
    
    Despachado --> Entregue : Código de entrega validado
    Despachado --> EmDisputa : Cliente relata extravio ("Não Recebi")
    
    EmDisputa --> ResolvidoReenvio : Reenvio de novo pedido
    EmDisputa --> ResolvidoEstorno : Reembolso aprovado ao cliente
    
    Entregue --> [*]
    Cancelado --> [*]
    ResolvidoReenvio --> [*]
    ResolvidoEstorno --> [*]
```

---

### 8.3 Diagrama de Classes e Entidade-Relacionamento (DER Lógico)

```mermaid
erDiagram
    RESTAURANTE ||--|{ CARDAPIO_ITEM : possui
    RESTAURANTE ||--o{ PEDIDO : recebe
    RESTAURANTE ||--o{ CAIXA_SESSAO : gerencia

    CLIENTE ||--o{ PEDIDO : realiza
    
    PEDIDO ||--|{ PEDIDO_ITEM : contem
    CARDAPIO_ITEM ||--o{ PEDIDO_ITEM : referencia
    
    PEDIDO ||--|| PAGAMENTO : liquida
    PEDIDO ||--o| DOCUMENTO_FISCAL : emite
    PEDIDO ||--o| DESPACHO_ENTREGA : encaminha
    
    ENTREGADOR ||--o{ DESPACHO_ENTREGA : executa

    RESTAURANTE {
        uuid id PK
        string cnpj UK
        string razao_social
        string nome_fantasia
        string timezone
    }

    CLIENTE {
        uuid id PK
        string nome
        string telefone UK
        string cpf
    }

    PEDIDO {
        uuid id PK
        uuid restaurante_id FK
        uuid cliente_id FK
        string codigo_diario
        string origem_canal "WEB_PROPRIO | IFOOD | PDV_LANCADOR"
        string status "CRIADO | PREPARO | PRONTO | DESPACHADO | ENTREGUE | CANCELADO"
        decimal valor_produtos
        decimal taxa_entrega
        decimal valor_total
        timestamp criado_em
    }

    PEDIDO_ITEM {
        uuid id PK
        uuid pedido_id FK
        uuid cardapio_item_id FK
        string nome_snapshot
        int quantidade
        decimal preco_unitario
        string observacoes
    }

    PAGAMENTO {
        uuid id PK
        uuid pedido_id FK
        string metodo "PIX | CARTAO_CREDITO | DINHEIRO"
        decimal valor_bruto
        decimal taxa_gateway
        decimal split_restaurante
        decimal split_entregador
        string status_transacao
    }

    DOCUMENTO_FISCAL {
        uuid id PK
        uuid pedido_id FK
        string chave_acesso UK
        string numero_nf
        string status "AUTORIZADA | CONTINGENCIA | CANCELADA"
        string xml_storage_url
        timestamp autorizado_em
    }

    DESPACHO_ENTREGA {
        uuid id PK
        uuid pedido_id FK
        uuid entregador_id FK
        string status "ALOCADO | EM_ROTA | ENTREGUE | EXTRAVIADO"
        string codigo_confirmacao
        timestamp saida_em
        timestamp entrega_em
    }

    CAIXA_SESSAO {
        uuid id PK
        uuid restaurante_id FK
        uuid operador_id
        timestamp abertura_em
        timestamp fechamento_em
        decimal saldo_inicial
        decimal total_entradas_declaradas
        decimal total_entradas_sistema
        decimal diferenca_apurada
    }
```

---

### 8.4 Diagrama de Sequência: Ingestão, Preparo e Emissão Fiscal

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as Cliente (Cardápio Web)
    participant Gateway as Order Gateway (FastAPI)
    participant DB as PostgreSQL (ACID)
    participant KDS as Terminal KDS (Cozinha)
    participant Fiscal as Worker Fiscal
    participant SEFAZ as Webservice SEFAZ

    Cliente ->> Gateway: Submeter Pedido (POST /orders com X-Idempotency-Key)
    Gateway ->> DB: Verificar Idempotência e Salvar Pedido (Status: CRIADO)
    DB -->> Gateway: Pedido Persistido com Sucesso
    Gateway -->> Cliente: HTTP 201 Created (Código do Pedido)
    
    Gateway -) KDS: Disparo de Evento via SSE (OrderCreatedEvent)
    Note over KDS: Cozinha recebe o pedido instantaneamente (< 500ms)
    
    Gateway -) Fiscal: Enfileira Tarefa de Faturamento Assíncrono
    
    Cozinheiro ->> KDS: Toca na tela: Iniciar Preparo
    KDS ->> Gateway: PATCH /orders/{id}/status (IN_PREPARATION)
    
    par Faturamento Assíncrono com SEFAZ
        Fiscal ->> SEFAZ: Transmitir Lote NFC-e
        alt SEFAZ Responde com Sucesso
            SEFAZ -->> Fiscal: Protocolo de Autorização
            Fiscal ->> DB: Atualizar Nota Fiscal (AUTORIZADA + Chave de Acesso)
        else SEFAZ Inacessível (Timeout 3s)
            Fiscal ->> DB: Gerar Registro em CONTINGÊNCIA OFFLINE
            Note over Fiscal: XML enfileirado para envio posterior
        end
    and Finalização do Prato na Cozinha
        Cozinheiro ->> KDS: Toca na tela: Pedido Pronto
        KDS ->> Gateway: PATCH /orders/{id}/status (READY)
        Gateway -) DB: Atualiza Status e Notifica Despacho
    end
```

---

### 8.5 Diagrama de Atividades: Fluxo de Caixa e Fechamento Cego

```mermaid
flowchart TD
    Start((Início do Turno)) --> Abertura[Operador Abre o Caixa informando Fundo de Troco]
    Abertura --> Operacao[Registro de Vendas, Sangrias e Suprimentos ao longo do Turno]
    
    Operacao --> SolicitacaoFechamento[Fim do Turno: Operador Solicita Fechamento]
    SolicitacaoFechamento --> ContagemCega[Operador realiza contagem física e digita valores por modalidade: Dinheiro, Pix, Cartões]
    
    ContagemCega --> Apuracao{Sistema compara declarado vs. computado}
    
    Apuracao -- Divergência == 0 --> Aprovado[Fechamento Homologado com Sucesso]
    Apuracao -- Divergência != 0 --> Justificativa[Sistema solicita justificativa obrigatória do operador]
    
    Justificativa --> AlertaGerente[Gera Notificação de Divergência para o Gerente]
    AlertaGerente --> Aprovado
    
    Aprovado --> EmissaoRelatorio[Gera Relatório de Turno e Consolida no Backoffice]
    EmissaoRelatorio --> End((Fim do Turno))
```

---

### 8.6 Diagrama de Componentes: Clean Architecture no Monolito Modular

```mermaid
flowchart TB
    subgraph Drivers["Camada 4: Frameworks & Drivers (Infraestrutura Externa)"]
        Web[FastAPI Web Server / Routers]
        NextApp[Next.js Client Applications]
        Postgres[(PostgreSQL Database)]
        SefazGateway[Provedor de Emissão Fiscal]
        RedisCache[Redis Cache / Idempotência]
    end
    
    subgraph Adapters["Camada 3: Interface Adapters (Controladores e Repositórios)"]
        OrderController[OrderHttpController]
        KdsController[KdsSseController]
        OrderRepoImpl[OrderRepositoryPostgres]
        FiscalAdapterImpl[SefazFiscalAdapter]
    end
    
    subgraph Application["Camada 2: Application (Casos de Uso)"]
        CreateOrderUC[CreateOrderUseCase]
        AdvanceKdsStatusUC[AdvanceKdsStatusUseCase]
        CloseCashRegisterUC[CloseCashRegisterUseCase]
        EmitFiscalDocUC[EmitFiscalDocumentUseCase]
    end
    
    subgraph Domain["Camada 1: Domain (Núcleo Puro de Domínio)"]
        OrderEntity[Order Aggregate Root]
        CashRegisterEntity[CashRegister Aggregate]
        OrderRepoPort[[OrderRepository Interface]]
        FiscalServicePort[[FiscalService Interface]]
        DomainEvents[Domain Events: OrderPaid, OrderReady]
    end
    
    NextApp --> Web
    Web --> OrderController
    Web --> KdsController
    
    OrderController --> CreateOrderUC
    KdsController --> AdvanceKdsStatusUC
    
    CreateOrderUC --> OrderEntity
    CreateOrderUC --> OrderRepoPort
    CreateOrderUC --> DomainEvents
    
    AdvanceKdsStatusUC --> OrderEntity
    
    OrderRepoImpl -.implements.-> OrderRepoPort
    FiscalAdapterImpl -.implements.-> FiscalServicePort
    
    OrderRepoImpl --> Postgres
    FiscalAdapterImpl --> SefazGateway
    OrderController --> RedisCache
```