# Diagrama de Casos de Uso

## Visão Geral

O diagrama abaixo modela os casos de uso principais da Plataforma Unificada de Gestão de Delivery, incluindo atores, herança de ator, e relações `<<include>>` e `<<extend>>`.

```mermaid
flowchart LR
    Cliente((Cliente Final))
    Atendente((Atendente PDV))
    Cozinheiro((Cozinheiro))
    Despachante((Despachante))
    Entregador((Entregador))
    Admin((Administrador / Gestor))
    Sefaz((SEFAZ Fiscal))
    Ifood((iFood API))
    UberEats((Uber Eats API))

    %% Atores com herança
    Admin -.->|herda de| Cliente

    %% Casos de uso do contexto de Ingestão
    subgraph Ingestao["Contexto de Ingestão & Catálogo"]
        UC01[Consultar Cardápio Digital]
        UC02[Realizar Pedido Web]
        UC03[Lançar Pedido Rápido PDV]
        UC04[Ingerir Webhook Integrador]
    end

    %% Casos de uso do contexto de Fulfillment
    subgraph Fulfillment["Contexto de Fulfillment (KDS)"]
        UC05[Visualizar Fila no KDS]
        UC06[Avançar Etapa de Preparo]
        UC07[Sincronizar Ações Offline]
    end

    %% Casos de uso do contexto de Logística
    subgraph Logistica["Contexto de Logística & Despacho"]
        UC08[Alocar Pedido a Entregador]
        UC09[Registrar Confirmação de Entrega]
    end

    %% Casos de uso do contexto de Backoffice & Fiscal
    subgraph FinanceiroFiscal["Contexto Backoffice & Fiscal"]
        UC10[Efetuar Fechamento de Caixa]
        UC11[Emitir NFC-e Eletrônica]
        UC12[Consultar Relatórios e Curva ABC]
    end

    %% Relacionamentos de atores
    Cliente --> UC01
    Cliente --> UC02
    Atendente --> UC03
    Ifood --> UC04
    UberEats -.->|extend| UC04
    Cozinheiro --> UC05
    Cozinheiro --> UC06
    Cozinheiro --> UC07
    Atendente --> UC08
    Entregador --> UC09
    Admin --> UC12
    Sefaz -.->|include| UC11
    Sefaz -.->|include| UC10
```

## PlantUML Style (Notação Textual)

```
Ator: Cliente
Ator: Atendente
Ator: Cozinheiro
Ator: Despachante
Ator: Entregador
Ator: Administrador (herda de Cliente)

UC01 Consultar Cardápio Digital
UC02 Realizar Pedido Web
  <<include>> UC03 Validar Pagamento
  <<extend>> UC04 Aplicar Cupom (ponto de extensão: antes de finalizar pedido)
UC03 Lançar Pedido Rápido PDV
UC04 Ingerir Webhook Integrador
UC05 Visualizar Fila no KDS
UC06 Avançar Etapa de Preparo
UC07 Sincronizar Ações Offline
UC08 Alocar Pedido a Entregador
UC09 Registrar Confirmação de Entrega
UC10 Efetuar Fechamento de Caixa
  <<include>> UC11 Emitir NFC-e Eletrônica
UC12 Consultar Relatórios e Curva ABC
```