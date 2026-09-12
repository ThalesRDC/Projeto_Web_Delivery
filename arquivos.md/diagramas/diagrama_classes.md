# Diagrama de Classes

## Visão do Diagrama de Classes

O diagrama abaixo extrai as classes candidatas dos substantivos dos casos de uso e requisitos, definindo atributos, métodos, visibilidade e multiplicidade nas associações.

```mermaid
classDiagram
    class Usuario {
        -id: UUID
        -nome: String
        -email: String
        -cpf_cnpj: String
        +getNomeCompleto(): String
        +autenticar(senha: String): Boolean
    }
    class Administrador
    class Cliente
    Cliente --|> Usuario : "é um"
    class Pedido {
        -id: UUID
        -usuario_id: UUID
        -restaurante_id: UUID
        -status: StatusPedido
        -valor_total: Decimal
        -data_criacao: DateTime
        +calcularTotal(): Decimal
        +finalizar(): void
        +cancelar(): void
    }
    class ItemPedido {
        -id: UUID
        -pedido_id: UUID
        -cardapio_item_id: UUID
        -quantidade: int
        -preco_unitario: Decimal
        -subtotal: Decimal
        +calcularSubtotal(): Decimal
    }
    class CardapioItem {
        -id: UUID
        -restaurante_id: UUID
        -nome: String
        -descricao: String
        -preco: Decimal
        -categoria: String
    }
    class Pagamento {
        -id: UUID
        -pedido_id: UUID
        -metodo: String "PIX | CARTAO_CREDITO | DINHEIRO"
        -valor_bruto: Decimal
        -taxa_gateway: Decimal
        -split_restaurante: Decimal
        -split_entregador: Decimal
        -status_transacao: String
        +autorizar(): void
        +refund(): void
    }
    class FiscalDocumento {
        -id: UUID
        -pedido_id: UUID
        -chave_acesso: String
        -numero_nf: String
        -status: String "AUTORIZADA | CONTINGENCIA | CANCELADA"
        -xml_storage_url: String
        +gerarXML(): String
    }
    class CashRegister {
        -id: UUID
        -restaurante_id: UUID
        -operador_id: UUID
        -saldo_inicial: Decimal
        -total_entradas: Decimal
        -divergencias: Decimal
        +abrir(): void
        +fechar(): void
        +registrarSangria(): void
    }
    class Entregador {
        -id: UUID
        -nome: String
        -veiculo: String
        -status: String "DISPONIVEL | EM_ROTA | INDISPONIVEL"
        +atualizarLocalizacao(): void
    }

    %% Relacionamentos
    Administrador --|> Usuario : "é um"
    Usuario "1" -- "0..*" Pedido : "realiza"
    Pedido *-- "1..*" ItemPedido : "composição"
    ItemPedido --> "1" CardapioItem : "referência"
    Pedido "1" o-- "0..1" Pagamento : "associa"
    Pedido "1" o-- "1" FiscalDocumento : "emite" 
    Pedido "1" o-- "1" CashRegister : "gerencia"
    Usuario "1" o-- "1" Entregador : "credenciais"
    Entregador "1" -- "0..*" Despacho : "executa"

    %% Estereótipos de persistência (PK/FK documentados no DER)
    <<entity>> Pedido
    <<entity>> ItemPedido
    <<entity>> Pagamento
    <<entity>> FiscalDocumento
    <<entity>> CashRegister
    <<entity>> Usuario
    <<entity>> Entregador
    <<entity>> CardapioItem
```