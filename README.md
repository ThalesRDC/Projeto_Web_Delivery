# 🍔 Plataforma Unificada de Gestão de Delivery (PUGD)

> Sistema de gestão operacional e engenharia de software para delivery de lanchonete familiar: da captura unificada de pedidos à impressão térmica na chapa, fechamento cego de caixa e emissão fiscal desacoplada.

---

## 📌 Resumo Executivo & Contexto Real

Diferente de sistemas genéricos corporativos ou soluções superdimensionadas para grandes redes de franquias, a **PUGD** foi desenhada estritamente para a realidade operacional de uma **lanchonete familiar de hambúrgueres artesanais / dark kitchen**:

* **Equipe Operacional Enxuta**: 5 colaboradores (1 chapeiro/cozinha, 1 montador/embalagem, 1 atendente/caixa e 2 motoboys próprios).
* **Volume Diário**: 20 a 60 pedidos por noite (pico concentrado entre 19h30 e 22h00 às sextas e domingos).
* **Cultura Física Soberana**: O chapeiro trabalha em ambiente com calor, fumaça e gordura. Telas touch na chapa falham; o comando da cozinha é sustentado por **comprovantes térmicos físicos (ESC/POS)** grampeados diretamente na sacola do pedido.
* **Paradigma de Software**: **Monolito Modular** baseado em **Clean Architecture**, **Domain-Driven Design (DDD)** e esteira orientada a **TDD**, eliminando overhead de rede, microsserviços e complexidade desnecessária.

---

## 🎯 Dores do Negócio e Pilares da Solução

### O Problema Operacional Real
1. **Dependência e Perda de Margem em Plataformas Terceiras**: Mensalidades, comissões agressivas, relatórios superficiais e cardápio engessado para complementos.
2. **Ambiguidade e Erro em Pedidos por WhatsApp**: Mensagens informais picadas (*"2 x-tudo, 1 sem tomate"* em duas mensagens gera lanche errado e refação).
3. **Lançamento Manual e Retrabalho**: O atendente copia mensagens do WhatsApp ou telefone para comandas de papel ou sistemas lentos, atrasando a chapa.
4. **Fechamento de Caixa sem Rigor**: Vendas fragmentadas em duas maquinetas físicas, dinheiro e Pix, sem conferência cega, gerando quebras de caixa não rastreadas.
5. **Vulnerabilidade Fiscal**: Sistemas que travam a expedição quando o webservice da SEFAZ oscila.

### Os 4 Pilares da Solução (MVP Realista)
* **🚀 1. Ingestão Unificada de Pedidos**: Cardápio digital web próprio (canal direto para o cliente via smartphone) integrado a um lançador rápido de balcão para pedidos de WhatsApp e balcão em fluxo único.
* **🍳 2. Operação de Cozinha & Chapa**: Fila unificada de pedidos e **impressão térmica automática (ESC/POS)** na chapa assim que o pedido é confirmado (<1s), com terminal visual simplificado de status.
* **💰 3. Fechamento Cego de Caixa**: O operador conta fisicamente gaveta e maquinetas e digita os valores sem viés de confirmação (sem ver os totais do sistema). Divergências exigem justificativa formal obrigatória.
* **⚡ 4. Faturamento Fiscal Assíncrono**: Emissão de NFC-e desacoplada em background worker. A cozinha prepara, o motoboy entrega e a SEFAZ processa sem travar a operação.

---

## 🚫 Fora de Escopo (Combate ao Over-Engineering)

Saber o que **NÃO** construir é a principal evidência de maturidade em engenharia de software. Foram conscientemente descartados do MVP:

| Recurso Descartado | Por que foi descartado? (Trade-off de Engenharia) | Solução Adotada no MVP |
| :--- | :--- | :--- |
| **Microsserviços / Cell-Based** | Complexidade operacional, custo de deploy e latência distribuída desnecessária para 60 ped/dia. | **Monolito Modular** com módulos coesos e transações ACID no PostgreSQL. |
| **KDS Offline / Vector Clocks** | A lanchonete possui internet fixa estável; relógios lógicos são preciosismo acadêmico. | Fila síncrona com idempotência no banco de dados e cupom térmico impresso. |
| **Split de Pagamento Duplo** | Motoboys são da equipe própria e pagos por diária fixa + taxa por entrega simples. | Registro de taxa de entrega e diária no fechamento de turno do caixa. |
| **IA / LLM no Pedido do MVP** | Risco de alucinação de ingredientes e custo desproporcional para a operação atual. | Cardápio web estruturado + lançador manual assistido com atalhos de teclado. |
| **Cluster Redis Dedicado** | Um banco relacional bem indexado resolve idempotência e trava de transação com simplicidade. | Constraint única `chave_idempotencia` no PostgreSQL com rollback automático. |

---

## 🏛️ Arquitetura de Software & Clean Architecture

O sistema adota o padrão **Clean Architecture** dentro de um Monolito Modular em Python/FastAPI e Next.js, isolando as regras de negócio de frameworks e drivers externos:

```
src/
├── domain/                      # Camada 1: Núcleo Puro de Negócio (Zero dependências externas)
│   ├── entities/                # Pedido, ItemPedido, CardapioItem, CaixaSessao, Cliente
│   ├── value_objects/           # Dinheiro, EnderecoEntrega, StatusPedido (FSM)
│   └── ports/                   # Interfaces abstratas: PedidoRepository, ImpressoraPort, FiscalPort
│
├── application/                 # Camada 2: Casos de Uso e Orquestração
│   ├── use_cases/               # CriarPedidoWeb, RegistrarPedidoPdv, FecharCaixaCego, EmitirNfce
│   └── dtos/                    # Contratos de entrada e saída (Schemas puros)
│
├── adapters/                    # Camada 3: Adaptadores de Interface
│   ├── controllers/             # Endpoints HTTP REST (FastAPI)
│   ├── repositories/            # Implementações PostgreSQL com SQLAlchemy
│   ├── thermal_printer/         # Adaptador ESC/POS para impressora de bobina
│   └── fiscal/                  # Adaptador HTTP do provedor fiscal da NFC-e
│
└── infra/                       # Camada 4: Frameworks, Drivers e Configurações
    ├── database/                # Conexões assíncronas de banco e migrações Alembic
    ├── workers/                 # Worker assíncrono para emissão da NFC-e
    └── web/                     # Servidor ASGI Uvicorn e middlewares de segurança
```

---

## 📊 Hub de Engenharia & Modelagem Visual (100% SKILL.md)

Toda a modelagem técnica do sistema está documentada em conformidade estrita com o checklist do [SKILL.md](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/SKILL.md), disponível tanto na pasta [Diagrama/](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama) quanto integrados com zoom e pan:

| Seção | Diagrama / Artefato | Tipo | Destaque Técnico |
| :---: | :--- | :---: | :--- |
| **8.1** | [Casos de Uso Geral](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/8.1_diagrama_de_casos_de_uso_geral.html) | Comportamental | Herança de ator (`Admin -.-> Atendente`), `<<include>>` (NFC-e) e `<<extend>>` (Descontos). |
| **8.2** | [Descrições Textuais dos Casos de Uso](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Arquivos/proposta_final.md#82-descrições-textuais-dos-casos-de-uso-principais) | Especificação | Pré-condições, fluxos principais e alternativos detalhados (UC01 a UC12). |
| **8.3** | [Diagrama de Classes](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/8.3_diagrama_de_classes.html) | Estrutural | Composição (`Pedido *-- ItemPedido`), agregação (`Pedido o-- Pagamento`), visibilidade (`+`, `-`) e métodos. |
| **8.4** | [Tabela de Persistência](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Arquivos/proposta_final.md#84-tabela-de-marcação-de-persistência-das-entidades) | Mapeamento | Estratégia de banco relacional: PKs UUIDs, tabelas e Value Objects embutidos. |
| **8.5** | [DER Lógico Relacional](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/8.5_diagrama_entidade-relacionamento_der_logico.html) | Banco de Dados | Cardinalidades relacionais, chaves estrangeiras e índice único de idempotência. |
| **8.6** | [Diagrama de Objetos](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/8.6_diagrama_de_objetos_snapshot_em_tempo_de_execucao.html) | Snapshot Real | Instância viva em tempo de execução: Pedido #42 (X-Tudo, Coca-Cola e Pix). |
| **8.7** | [Diagrama de Estados (FSM)](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/8.7_diagrama_de_estados_do_pedido_ciclo_de_vida_simplificado.html) | Ciclo de Vida | Transições finitas: `Criado → EmPreparo → Pronto → Entregue / Cancelado`. |
| **8.8** | [Classes BCE / Robustez](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/diagrama_de_robustez_caso_de_uso_realizar_lancar_pedido.html) | Arquitetura | Fronteira (Boundary), Controle (Control) e Entidades (Entity) do caso de uso de pedido. |
| **8.9.1** | [Sequência: Ingestão & Chapa](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/8.9.1_ingestao_e_producao_na_chapa_fluxo_critico_da_cozinha_-_uc02uc03_uc05.html) | Interação | Caminho crítico síncrono: Idempotência, gravação ACID e disparo ESC/POS imediato. |
| **8.9.2** | [Sequência: Faturamento Fiscal](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/8.9.2_faturamento_fiscal_assincrono_worker_sefaz_-_uc11.html) | Interação | Resiliência assíncrona: Worker de NFC-e com política de retry sem travar a chapa. |
| **8.10** | [Atividades do Caixa](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/8.10_diagrama_de_atividades_fluxo_de_caixa_e_fechamento_cego.html) | Processo | Fluxo de fechamento cego de caixa, apuração de diferenças e justificativa de quebra. |
| **8.11** | [Componentes Clean Arch](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Diagrama/8.11_diagrama_de_componentes_clean_architecture_no_monolito_modular.html) | Arquitetura | 4 camadas do Monolito Modular e direção estrita de dependências para o centro. |

> 💡 **Recursos Interativos dos Diagramas:** Todas as páginas HTML possuem **zoom via scroll do mouse**, **arrastar para navegar (pan)**, botões de reset, ajuste automático e atalhos de teclado.

---

## 🖥️ Aplicação de Apresentação Técnica & Simulador Operacional

O projeto conta com uma ferramenta web interativa multifuncional criada no arquivo [apresentacao.html](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/apresentacao.html):

1. **Aba 1: Apresentação de Slides Executiva**:
   - 9 slides profissionais com tipografia moderna, design dark glassmorphism e controle por teclado (`←`, `→`, barra de espaço).
   - Inclui slide dedicado para Engenharia de Requisitos (RF e RNF) e gaveta retrátil com roteiro de fala para o apresentador (tecla `N`).
2. **Aba 2: Simulador Operacional da Lanchonete (Live Demo)**:
   - **Coluna 1 (Cardápio Web do Cliente)**: Adição de lanches e fechamento de pedido com áudio sintetizado.
   - **Coluna 2 (Cozinha & Chapa KDS)**: Fila de pedidos e geração do **Cupom de Produção Térmico** simulado para grampear na sacola.
   - **Coluna 3 (Fechamento Cego de Caixa)**: Teste prático de divergência de caixa com validação de quebra e exigência de justificativa.
3. **Aba 3: Tabela de Requisitos (RF & RNF)**:
   - Visualização interativa e filtrável dos 11 Requisitos Funcionais e 10 Requisitos Não Funcionais, detalhando critérios mensuráveis e casos de uso associados.
4. **Aba 4: Hub de Diagramas Mermaid**:
   - Grid com os 10 diagramas técnicos, modal ampliado (`96vw × 92vh`) com suporte a tela cheia em nova aba e controles de Pan & Zoom.
5. **Aba 5: Matriz de Rastreabilidade TDD**:
   - Tabela conectando RF01 a RF11 a testes unitários, testes de caso de uso e testes de integração de banco.

---

## 🧪 Disciplina de Testes & Rastreabilidade TDD

Todo requisito funcional (RF) do sistema possui rastreabilidade ponta a ponta com casos de teste:

```
[ Requisito Funcional (RF) ] ──▶ [ Caso de Uso (UC) ] ──▶ [ Teste Unitário (Domínio) ] ──▶ [ Teste de Integração (DB) ]
```

| RF | Requisito | Caso de Uso | Teste Unitário (Domain) | Teste de Use Case (Application) |
| :---: | :--- | :---: | :--- | :--- |
| **RF01** | Consultar Cardápio | UC01 | `test_cardapio_item_disponibilidade()` | `test_listar_itens_ativos_use_case()` |
| **RF02** | Registrar Pedido PDV | UC03 | `test_pedido_adicionar_item_calculo_total()` | `test_registrar_pedido_pdv_sucesso()` |
| **RF03** | Unificar Fila Multicanal | UC02/03 | `test_pedido_origem_canal_valida()` | `test_pedidos_multiplos_canais_mesma_fila()` |
| **RF04** | Trava de Idempotência | UC02/03 | `test_chave_idempotencia_obrigatoria()` | `test_rejeitar_pedido_duplicado_mesma_chave()` |
| **RF05** | Fila KDS Cronológica | UC05 | `test_ordenacao_pedidos_por_criado_em()` | `test_obter_pedidos_pendentes_use_case()` |
| **RF06** | Impressão Térmica Chapa | UC05 | `test_formatacao_cupom_chapa_escpos()` | `test_disparo_evento_impressao_pedido()` |
| **RF07** | Fechamento Cego Caixa | UC10 | `test_apuracao_diferenca_caixa_cego()` | `test_fechar_caixa_com_divergencia_use_case()` |
| **RF08** | Registro de Pagamento | UC02/03 | `test_pagamento_valor_bate_com_pedido()` | `test_registrar_pagamento_sucesso_use_case()` |
| **RF09** | Emissão NFC-e Assíncrona | UC11 | `test_documento_fiscal_status_transicao()` | `test_agendamento_emissao_nfce_assincrona()` |
| **RF10** | Relatórios de Turno | UC12 | `test_calculo_ticket_medio()` | `test_gerar_relatorio_periodo_use_case()` |
| **RF11** | Controle de Entregas | UC07 | `test_despacho_transicao_em_rota_entregue()` | `test_atribuir_motoboy_pedido_use_case()` |

---

## 📁 Estrutura do Repositório

```text
Projeto_Web_Delivery/
├── README.md                           # Visão geral, arquitetura e guia do projeto (este arquivo)
├── apresentacao.html                   # Aplicação web 3 em 1: Slides, Simulador e Hub de Diagramas
├── gerar_diagramas.py                  # Script automatizado para extração, renderização PNG/SVG e Zoom/Pan
├── SKILL.md                            # Diretriz metodológica e checklist acadêmico formal de engenharia
│
├── Arquivos/
│   ├── proposta_final.md               # Documento Mestre de especificação técnica e ideação (v2.1)
│   └── proposta_mvp_realista.md        # Documento base de alinhamento com o microuniverso
│
└── Diagrama/
    ├── index.html                      # Painel / Galeria com os 10 diagramas gerados
    ├── 8.1_diagrama_de_casos_de_uso_geral.html (.png, .svg, .mmd)
    ├── 8.3_diagrama_de_classes.html (.png, .svg, .mmd)
    ├── 8.5_diagrama_entidade-relacionamento_der_logico.html (.png, .svg, .mmd)
    ├── 8.6_diagrama_de_objetos_snapshot_em_tempo_de_execucao.html (.png, .svg, .mmd)
    ├── 8.7_diagrama_de_estados_do_pedido_ciclo_de_vida_simplificado.html (.png, .svg, .mmd)
    ├── diagrama_de_robustez_caso_de_uso_realizar_lancar_pedido.html (.png, .svg, .mmd)
    ├── 8.9.1_ingestao_e_producao_na_chapa_fluxo_critico_da_cozinha_-_uc02uc03_uc05.html (.png, .svg, .mmd)
    ├── 8.9.2_faturamento_fiscal_assincrono_worker_sefaz_-_uc11.html (.png, .svg, .mmd)
    ├── 8.10_diagrama_de_atividades_fluxo_de_caixa_e_fechamento_cego.html (.png, .svg, .mmd)
    └── 8.11_diagrama_de_componentes_clean_architecture_no_monolito_modular.html (.png, .svg, .mmd)
```

---

## 🚀 Como Executar e Demonstrar

### 1. Visualizar a Apresentação Completa e o Simulador
Abra diretamente no navegador padrão:
```powershell
start apresentacao.html
```

### 2. Acessar a Galeria de Diagramas Técnicos
```powershell
start Diagrama\index.html
```

### 3. Regenerar Diagramas em Alta Resolução (PNG, SVG, HTML com Pan/Zoom)
Caso queira alterar qualquer especificação Mermaid no [proposta_final.md](file:///c:/Users/Thales/Documents/WEB/Projeto_Web_Delivery/Arquivos/proposta_final.md), basta rodar:
```powershell
python gerar_diagramas.py --input Arquivos/proposta_final.md --output Diagrama
```

---

## 📄 Licença e Propriedade
Este projeto foi desenvolvido como especificação e produto de engenharia de software para a disciplina de Projeto Web / Engenharia de Software.
Todos os direitos reservados.
