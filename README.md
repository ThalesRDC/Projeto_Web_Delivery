# Projeto Web Delivery

Plataforma unificada para gestão de delivery, integrando cardápio digital web, lançador rápido de PDV, KDS (Kitchen Display System) offline-first, despacho dinâmico de entregadores e backoffice financeiro com compliance fiscal (NFC-e).

## 📄 Especificação e Documentação Completa

Toda a ideação, modelagem DDD, requisitos, arquitetura de software, diagramas técnicos e trilha de implementação estão centralizados no documento mestre:

👉 **[Documento de Especificação e Ideação (proposta_final.md)](./arquivos.md/proposta_final.md)**

---

## 🏗️ Pilares da Solução

- **Captura**: Cardápio digital web de autoatendimento e Lançador rápido com atalhos para balcão.
- **Operação**: KDS de cozinha com WebSockets/SSE e suporte a modo offline via IndexedDB.
- **Logística**: Despacho com alocação e confirmação de entrega.
- **Backoffice & Fiscal**: Fechamento cego de caixa e emissão de NFC-e com contingência offline.
