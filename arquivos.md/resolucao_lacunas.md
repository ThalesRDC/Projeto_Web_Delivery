# Documento de Especificação de Software: Plataforma Unificada de Gestão de Delivery

## 6. Resolução das 10 Lacunas Críticas de Operação & Negócio

### 6.1 Lacuna 1: Compliance Fiscal Brasileiro (NF-e / NFC-e)
A legislação tributária brasileira impõe a emissão obrigatória de documento fiscal eletrônico (NFC-e para consumidor final e NF-e para entregas intermunicipais ou vendas B2B). O não cumprimento sujeita o estabelecimento a pesadas sanções fiscais e fechamento imediato.

#### Arquitetura de Emissão e Contingência

```
┌─────────────────┐       ┌──────────────────────┐       ┌─────────────────────┐
│  Order Service  │──────▶│  Fiscal Orchestrator │──────▶│ Gateway Fiscal API  │
│ (Pedido Pago)   │       │  (Fila de Mensagens) │       │ (TecSpeed / Senior) │
└─────────────────┘       └──────────────────────┘       └─────────────────────┘
                                      │                                  │
                                      ▼ (Falha SEFAZ)                    ▼
                           ┌──────────────────────┐       ┌─────────────────────┐
                           │  Contingência Offline│       │   SEFAZ Estadual    │
                           │  (Emissão NFC-e com  │       │ (Autorização Normal)│
                           │   QR-Code Offline)   │       └─────────────────────┘
                           └──────────────────────┘                      │
                                      │                                  ▼
                                      │ Sincronização             ┌─────────────────────┐
                                      └──────────────────────────▶│ Storage Seguro XML  │
                                                                  │ (Retenção 5 Anos)   │
                                                                  └─────────────────────┘
```

1. **Emissão Assíncrona Desacoplada:** A aprovação do pedido na cozinha e a impressão do cupom de produção jamais aguardam a resposta da SEFAZ. O pedido é salvo e um evento `OrderPaid` despacha a emissão fiscal para uma fila assíncrona.
2. **Tratamento de Indisponibilidade (Contingência Offline):** Se a SEFAZ do estado estiver fora do ar ou com latência superior a 5 segundos, o componente fiscal chaveia automaticamente para emissão em Contingência Offline (NFC-e gerada localmente com assinatura digital e QR-Code de contingência). O cupom é entregue ao motoboy e o XML é transmitido automaticamente à SEFAZ em lote quando o canal de comunicação for reestabelecido.
3. **Guarda Regulamentar:** Todos os arquivos XML e protocolos de autorização/cancelamento são salvos em bucket de armazenamento imutável (Object Storage) com criptografia AES-256 e política de ciclo de vida configurada para retenção legal de 5 anos.

```python
class FiscalOrchestrator:
    def __init__(self, fiscal_provider_adapter, secure_storage_service):
        self.provider = fiscal_provider_adapter
        self.storage = secure_storage_service

    async def process_order_fiscal(self, order: "Order") -> "FiscalDocumentResult":
        xml_payload = self._build_sefaz_xml(order)
        try:
            result = await self.provider.transmit_with_timeout(xml_payload, timeout_sec=3.0)
            if result.is_authorized:
                await self.storage.save_xml(order.id, result.authorized_xml, retention_years=5)
                return FiscalDocumentResult(status="AUTHORIZED", chave_acesso=result.chave)
        except SefazUnavailableException:
            pass

        offline_result = await self.provider.generate_offline_contingency(xml_payload)
        await self.storage.queue_for_sync(order.id, offline_result.contingency_xml)
        return FiscalDocumentResult(status="CONTINGENCY_OFFLINE", danfe_print=offline_result.danfe_data)
```

---

### 6.2 Lacuna 2: Resolução de Conflitos Offline no KDS
Em operações de alta rotatividade com redes sem fio instáveis, múltiplos terminais podem registrar ações simultâneas e conflitantes sobre o mesmo pedido enquanto desconectados.

#### Estratégia de Resolução: Vector Clocks & Máquina de Estados Finita
- **Conflito Clássico:** Terminal A (offline) marca pedido #101 como "Pronto". Terminal B (offline) marca pedido #101 como "Cancelado pelo Cliente".
- **Solução:** Cada terminal mantém um vetor de versão (*Vector Clock*). A máquina de estados do backend avalia se a transição é semanticamente legal:
  - Se um pedido já foi marcado como "Cancelado", a marcação de "Pronto" é rejeitada, notificando o terminal A com alerta sonoro e visual de conciliação.
  - Para transições de avanço de praça não conflitantes, as atualizações são aplicadas cumulativamente.

```python
class OrderAggregate:
    VALID_TRANSITIONS = {
        "CREATED": ["IN_PREPARATION", "CANCELLED"],
        "IN_PREPARATION": ["READY", "CANCELLED"],
        "READY": ["DISPATCHED", "CANCELLED"],
        "DISPATCHED": ["DELIVERED", "DISPUTED"],
        "DELIVERED": ["DISPUTED"],
        "CANCELLED": [],  # Estado terminal
        "DISPUTED": ["RESOLVED_REFUNDED", "RESOLVED_REJECTED"]
    }

    def apply_offline_sync(self, action: str, device_id: str, client_clock: dict) -> "SyncResult":
        if action not in self.VALID_TRANSITIONS.get(self.current_status, []):
            return SyncResult(accepted=False, current_status=self.current_status, reason=f"Transição inválida: {self.current_status} -> {action}")
        self.current_status = action
        self.vector_clock[device_id] = client_clock.get(device_id, 0) + 1
        return SyncResult(accepted=True, current_status=self.current_status)
```

---

### 6.3 Lacuna 3: Antifraude e Split de Pagamentos em Partidas Dobradas
O processamento de valores no delivery envolve múltiplos beneficiários na mesma transação: o restaurante (valor dos itens), a plataforma (comissão de intermediação), o entregador (taxa de deslocamento) e a credenciadora de cartão (taxa MDR).

#### Modelagem Contábil de Partidas Dobradas (Double-Entry Ledger)
Qualquer movimentação financeira é expressa por um par balanceado de Débito e Crédito em contas analíticas, assegurando auditoria matemática absoluta:

```
Exemplo: Pedido de R$ 100,00 pago via Cartão de Crédito Online
- Taxa de Intermediação da Plataforma: 15% (R$ 15,00)
- Taxa de Entrega repassada ao Motoboy: R$ 8,00
- Taxa MDR da Adquirente: 2% (R$ 2,00)
- Valor Líquido devido ao Restaurante: R$ 75,00

Lançamentos Contábeis do Pedido:
  Débito:  Conta a Receber (Adquirente Cartão)         R$ 100,00
  Crédito: Receita de Intermediação (Plataforma)       R$  15,00
  Crédito: Conta a Pagar (Entregador Parceiro)         R$   8,00
  Crédito: Despesa Operacional MDR (Adquirente)        R$   2,00
  Crédito: Conta a Pagar (Restaurante Parceiro)        R$  75,00
  -------------------------------------------------------------
  Balanço: Soma Débitos (R$ 100,00) == Soma Créditos (R$ 100,00)
```

#### Motor Antifraude Integrado
Antes da confirmação de pagamento para pedidos de alto valor com cartão online, o sistema submete a transação a uma checagem de score de risco:
1. **Verificação de Velocidade (Velocity Check):** Alerta se o mesmo CPF ou cartão realizou mais de 3 pedidos em menos de 15 minutos em estabelecimentos diferentes.
2. **Geolocalização de IP vs. Endereço de Entrega:** Discrepância extrema de distância eleva o score de suspeição.
3. **Histórico de Chargebacks:** Bloqueio cautelar imediato caso o cliente possua histórico de contestações não resolvidas.

---

### 6.4 Lacuna 4: Prevenção contra Vendor Lock-in (Arquitetura de Adapters)
Depender rigidamente de APIs proprietárias cria vulnerabilidade contratual e operacional.

#### Padrão de Projeto Adapter com Factory Dinâmica

```python
from typing import Protocol

class SMSNotificationService(Protocol):
    async def send_sms(self, destination_phone: str, message: str) -> str: ...
    async def check_delivery_status(self, provider_message_id: str) -> bool: ...

class TwilioAdapter:
    def __init__(self, account_sid: str, token: str): ...
    async def send_sms(self, destination_phone: str, message: str) -> str:
        return "twilio_msg_123"

class ZenviaAdapter:
    def __init__(self, api_key: str): ...
    async def send_sms(self, destination_phone: str, message: str) -> str:
        return "zenvia_msg_456"

class SMSProviderFactory:
    @staticmethod
    def get_provider(provider_type: str = "zenvia") -> SMSNotificationService:
        providers = {"twilio": TwilioAdapter, "zenvia": ZenviaAdapter}
        return providers[provider_type]()
```

*Benefício:* A substituição de um fornecedor que aumente tarifas ou enfrente instabilidade pode ser realizada em minutos alterando uma variável de ambiente, sem modificar uma única linha do domínio.

---

### 6.5 Lacuna 5: Plano Rigoroso de Disaster Recovery (RTO & RPO)
A disponibilidade de um sistema de delivery é crítica: ficar fora do ar em uma noite de sexta-feira destrói o faturamento de centenas de famílias e parceiros.

#### Metas de Resiliência

| Cenário de Falha | RPO Alvo (Perda Máxima de Dados) | RTO Alvo (Tempo Máximo de Retorno) | Mecanismo de Recuperação |
| :--- | :--- | :--- | :--- |
| **Queda do Nó Primário de BD** | < 1 minuto | < 15 minutos | Promoção de Standby via replicação síncrona PostgreSQL WAL. |
| **Corrupção de Tabelas / Erro Humano** | < 15 minutos | < 1 hora | Point-in-Time Recovery (PITR) utilizando snapshots + arquivos WAL arquivados. |
| **Indisponibilidade de Datacenter** | < 5 minutos | < 30 minutos | Failover de DNS para região secundária com banco de réplica ativa. |

#### Política de Backup e Archiving
- Snapshots diários completos executados durante a madrugada (03:00 AM).
- Arquivamento contínuo dos arquivos de log de transação do PostgreSQL (`archive_command` transmitindo segmentos WAL para bucket em região distinta a cada 5 minutos).
- Teste trimestral obrigatório de restauração de backup em ambiente isolado (Sandbox).

---

### 6.6 Lacuna 6: UX Acessível para Ambientes de Alta Rotatividade
Cozinhas industriais e balcões de delivery apresentam rotatividade frequente na equipe operacional. O software deve exigir treinamento zero:
- **Alvos de Toque Sobredimensionados:** Botões de ação na tela de cozinha possuem dimensões mínimas de 56x56dp, facilitando o acionamento por operadores usando luvas ou telas engorduradas.
- **Alto Contraste e Codificação por Formas:** Contraste superior a 4.5:1 (WCAG AA). O status do pedido utiliza não apenas cores, mas símbolos universais (`✓` para Pronto, `!` para Atrasado, `⏱` para Em Preparo), atendendo a operadores com daltonismo.
- **Alternativa Visual para Ambientes Barulhentos:** Cozinhas possuem ruído ambiente contínuo de coifas, fritadeiras e conversas. Alertas sonoros são complementados por flash visual de borda da tela na cor âmbar quando um pedido ultrapassa o tempo limite de tolerância.

---

### 6.7 Lacuna 7: Matriz e Comunicação da Proposta de Valor
O sistema consolida seu valor no dia a dia da operação através de métricas financeiras e estratégicas transparentes:
1. **Visibilidade da Economia de Taxas:** Acompanhamento contínuo da economia gerada pela migração gradual de pedidos para o cardápio próprio sem comissões abusivas de intermediadores.
2. **Retenção e Inteligência da Base Própria:** O estabelecimento constrói e mantém o controle direto sobre sua base de clientes (histórico de consumo, frequência e contato WhatsApp), eliminando a dependência cega de dados mascarados por marketplaces.

---

### 6.8 Lacuna 8: Workflows Transversais (Disputas e "Não Recebi meu Pedido")
Casos de insatisfação ou extravio representam até 5% das entregas em cidades grandes. A resolução automatizada evita desgaste com o cliente e atrito com o entregador.

#### Fluxograma de Decisão de Disputa

```
       Cliente aciona "Não Recebi meu Pedido" no Cardápio Web
                                 │
                                 ▼
              Sistema coleta evidências em tempo real da entrega:
              - Traçado do GPS do entregador nos últimos 10 minutos
              - Proximidade com o endereço (Raio < 50 metros)
              - Foto da fachada / assinatura coletada no app de entrega
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
        [Evidências Consistentes]       [Evidências Inconsistentes /
      (Entregador esteve no local)          Ausência de Prova]
                 │                               │
                 ▼                               ▼
    Oferece mediação imediata:             Estorno automático imediato
    - Ligação direta ao motoboy            para o meio de pagamento
    - Validação de interfone               (Pix / Estorno de Cartão)
    - Reenvio express prioritário          + Notificação para auditoria
```

---

### 6.9 Lacuna 9: Estratégia de Migração Gradual de Dados Legados
Restaurantes estabelecidos possuem milhares de itens cadastrados e histórico em sistemas legados. A substituição ocorre sem interrupção de vendas:
1. **Fase 1 (Ingestão do Catálogo):** Upload de planilha Excel/CSV do cardápio legado através de assistente com parser automático e tela de homologação visual antes da ativação.
2. **Fase 2 (Deduplicação de Clientes):** Importação de histórico de clientes utilizando o CPF/CNPJ como chave mestra única de consolidação cadastral.
3. **Fase 3 (Operação Paralela):** Transição assistida com operação em paralelo até a equipe operacional consolidar total domínio e confiança no novo lançador e KDS.

---

### 6.10 Lacuna 10: Governança e Monitoramento de SLAs de Agregadores
O descumprimento de SLAs de resposta a pedidos integrados de iFood ou Uber Eats gera rebaixamento algorítmico do restaurante nas listas dos aplicativos ou cancelamento automático.

| Integração | SLA Máximo de Recepção | SLA Máximo de Confirmação | Ação Automática em caso de Degradação |
| :--- | :--- | :--- | :--- |
| **iFood Webhook** | < 1.000 ms | < 30 segundos | Alerta crítico no painel e fallback para polling de emergência. |
| **Uber Eats API** | < 2.000 ms | < 45 segundos | Enfileiramento com alta prioridade no cluster de ingestão. |
| **WhatsApp Parser** | < 5.000 ms | < 60 segundos | Notificação do atendente para confirmação manual no Lançador. |