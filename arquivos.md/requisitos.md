# Documento de Especificação de Software: Plataforma Unificada de Gestão de Delivery

## 2. Engenharia de Requisitos (RF e RNF)

### 2.1 Requisitos Funcionais (RF)

| ID | Descrição | Prioridade | Contexto / Ator |
| :--- | :--- | :--- | :--- |
| **RF01** | O sistema deve permitir ao cliente consultar o cardápio digital web categorizado, adicionar itens, personalizar adicionais/observações e submeter o pedido. | Alta | Ingestão / Cliente |
| **RF02** | O sistema deve disponibilizar interface de Lançador Rápido com atalhos de teclado para registro de pedidos presenciais e telefônicos em menos de 10 segundos. | Alta | Ingestão / Atendente |
| **RF03** | O sistema deve receber e consolidar webhooks de plataformas terceiras (iFood, Uber Eats) em uma fila padronizada única. | Alta | Ingestão / Sistema Externo |
| **RF04** | O sistema deve rejeitar requisições de criação de pedidos com chaves de idempotência repetidas, retornando o registro original sem duplicar produção. | Alta | Ingestão / Sistema |
| **RF05** | O KDS deve exibir os pedidos recebidos ordenados por ordem cronológica e criticidade de tempo, permitindo avançar status ("Em Preparo", "Pronto"). | Alta | Fulfillment / Cozinheiro |
| **RF06** | O KDS deve manter operação contínua mesmo sem conexão com a internet, persistindo ações localmente e reconciliando ao restabelecer rede. | Alta | Fulfillment / Cozinheiro |
| **RF07** | O sistema deve permitir ao despachante alocar um ou múltiplos pedidos prontos para um entregador credenciado. | Alta | Logística / Despachante |
| **RF08** | O sistema deve registrar a confirmação de entrega através de código de validação fornecido pelo cliente ou geolocalização do entregador. | Alta | Logística / Entregador |
| **RF09** | O sistema deve gerenciar o fluxo de caixa diário por operador, suportando abertura, sangrias, suprimentos e fechamento cego com cálculo de divergências. | Alta | Financeiro / Caixa |
| **RF10** | O sistema deve emitir documento fiscal eletrônico (NFC-e/NF-e) perante a SEFAZ de forma assíncrona a cada pedido faturado. | Alta | Fiscal / Sistema SEFAZ |
| **RF11** | O sistema deve emitir documento fiscal em contingência offline caso o webservice da SEFAZ esteja inacessível, transmitindo os lotes automaticamente após normalização. | Alta | Fiscal / Sistema |
| **RF12** | O sistema deve calcular automaticamente o split financeiro de cada pedido (líquido do lojista, comissão da plataforma, taxa de entrega e desconto de MDR). | Alta | Financeiro / Sistema |
| **RF13** | O sistema deve prover fluxo de contestação e disputa para pedidos não entregues ou itens incorretos, permitindo estorno total, parcial ou reenvio. | Média | Operação / Suporte |
| **RF14** | O sistema deve exibir painel analítico gerencial com faturamento diário/mensal, ticket médio, horários de pico e curva ABC de produtos. | Média | Backoffice / Gestor |
| **RF15** | O sistema deve fornecer ferramenta de importação e validação de cardápios legados a partir de planilhas Excel/CSV. | Média | Backoffice / Administrador |

### 2.2 Requisitos Não Funcionais (RNF)

| ID | Categoria | Critério Mensurável e Especificação Técnica |
| :--- | :--- | :--- |
| **RNF01** | **Performance** | Latência de resposta de API no Lançador e Cardápio inferior a 250ms sob percentil 95 (p95). |
| **RNF02** | **Disponibilidade** | Disponibilidade de 99.99% para a tela do KDS na cozinha e 99.9% para a API central de pedidos. |
| **RNF03** | **Tempo Real** | Propagação de eventos de novos pedidos e atualizações de status para KDS em menos de 500ms via SSE ou WebSockets. |
| **RNF04** | **Confiabilidade (RPO)** | Ponto de Recuperação Objetivo (RPO) inferior a 5 minutos através de replicação contínua WAL no PostgreSQL. |
| **RNF05** | **Recuperação (RTO)** | Tempo de Recuperação Objetivo (RTO) inferior a 30 minutos em caso de queda do nó primário de banco de dados. |
| **RNF06** | **Compliance Legal** | Armazenamento de arquivos XML de notas fiscais autorizadas e canceladas por no mínimo 5 anos em storage seguro com criptografia AES-256. |
| **RNF07** | **Portabilidade / Vendor Lock-in** | Uso estrito do padrão Adapter para todas as integrações de terceiros (gateways, SMS, mapas e emissão fiscal), permitindo substituição rápida e transparente sem impacto no domínio. |
| **RNF08** | **Usabilidade em Cozinha** | Interface KDS adaptada a condições industriais: botões com área de toque mínima de 48x48dp, contraste de cores superior a 4.5:1 e suporte a feedback sonoro/vibratório. |
| **RNF09** | **Segurança** | Criptografia em trânsito (TLS 1.3) para todas as comunicações e aderência à LGPD para mascaramento de dados sensíveis de clientes. |
| **RNF10** | **Integridade Contábil** | Livro razão financeiro modelado estritamente por partidas dobradas e registros imutáveis (append-only ledger). |