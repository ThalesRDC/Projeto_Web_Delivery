# Documento de Especificação de Software: Plataforma Unificada de Gestão de Delivery

## 5. Decisões Críticas de Engenharia

### 5.1 Idempotência Rigorosa no Order Gateway
Agregadores externos (como iFood e Uber Eats) utilizam políticas agressivas de retentativa de envio de webhooks caso não recebam um `HTTP 200 OK` em menos de 2 a 3 segundos. Se o sistema não implementar idempotência estrita, haverá cobrança duplicada e dois preparos simultâneos na cozinha.
- **Mecanismo:** Toda requisição de criação de pedido exige a chave `X-Idempotency-Key` no cabeçalho (ou o ID original da plataforma externa no payload).
- **Fluxo:** Ao receber o payload, o sistema tenta registrar uma trava atômica no Redis com tempo de expiração (TTL de 60 segundos). Caso a chave já exista, o sistema aguarda a conclusão ou retorna imediatamente a representação do pedido já criado, sem reprocessar a lógica de domínio.

### 5.2 Resiliência de Comunicação do KDS: Zero Polling HTTP
Cozinhas industriais são ambientes de extrema hostilidade eletromagnética (paredes de azulejo, fornos combinados, micro-ondas e superfícies espelhadas em aço inoxidável).
- **Proibição:** É estritamente proibido o uso de *HTTP Polling* (consultas periódicas a cada 5 segundos), pois satura o servidor, aumenta a latência de entrega dos tickets e consome banda desnecessariamente.
- **Solução:** Uso de **Server-Sent Events (SSE)** como protocolo primário para envio unidirecional do servidor para as telas da cozinha, com fallback para **WebSockets**.
- **Heartbeat & Reconexão Agressiva:** O cliente KDS dispara mensagens de heartbeat a cada 15 segundos. Caso 2 heartbeats consecutivos falhem, o cliente entra imediatamente em modo de reconexão exponencial com jitter, mantendo a interface interativa através dos dados locais.

### 5.3 Relógios Lógicos e Ordenação Temporal de Eventos
Em ambientes distribuídos e redes móveis 3G/4G utilizadas por motoboys, a ordem cronológica de chegada dos pacotes HTTP ao servidor é instável:
- **Cenário:** O evento "Motoboy Chegou ao Destino" pode bater no servidor antes do evento "Motoboy Aceitou a Corrida" devido à instabilidade de sinal.
- **Diretriz:** O sistema **não confia nos relógios de parede das máquinas clientes**. O avanço do pedido é controlado rigidamente por uma **Máquina de Estados Finita (FSM)**. Eventos que desrespeitem a pré-condição de estado são enfileirados em buffer temporário ou rejeitados para reprocessamento ordenado.

### 5.4 Observabilidade Orientada ao Negócio
Métricas genéricas de CPU e uso de memória RAM são insuficientes para detectar falhas de negócio em operações de delivery. A instrumentação (OpenTelemetry / Prometheus) emite métricas orientadas a SLAs operacionais:
- `delivery_order_acceptance_latency_seconds`: Tempo decorrido entre a chegada do pedido no gateway e a confirmação do restaurante. Alerta crítico se ultrapassar 120 segundos.
- `kds_order_queue_depth`: Quantidade de pratos em espera na fila da cozinha.
- `aggregator_webhook_lag_seconds`: Diferença temporal entre a emissão do webhook pelo iFood e o recebimento pelo gateway.