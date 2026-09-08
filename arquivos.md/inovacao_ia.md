# Documento de Especificação de Software: Plataforma Unificada de Gestão de Delivery

## 7. Inovação e Inteligência Artificial Pragmática

A adoção de Inteligência Artificial e Modelos de Linguagem (LLMs) é tratada com rigor pragmático: a IA é uma camada de assistência e produtividade, jamais um ponto de falha crítica na operação.

### 7.1 Lançador Assistido (Parser de Pedidos de WhatsApp)
- **Desafio:** Clientes enviam mensagens informais como: *"Boa noite, manda 2 X-Salada sem tomate, uma coca zero lata e entrega aqui na Rua das Flores 123 no apto 42, vou pagar no pix"*.
- **Arquitetura da Solução:**
  - Webhook de mensageria encaminha o texto para uma função com prompt estruturado para LLM leve e de baixa latência (ex: Gemini Flash).
  - A IA extrai o JSON padronizado com os itens, modificadores e endereço.
  - **Limiar de Confiança e Guardrails:** O sistema só preenche os campos automaticamente se a confiança do parser for superior a 95%. Se houver ambiguidade no cardápio, a interface do Lançador destaca os campos em amarelo e exige validação explícita do atendente humano antes da submissão à cozinha.

### 7.2 Co-pilot de Gestão de Catálogo
- **Funcionalidade:** O lojista pode enviar uma foto do cardápio físico impresso ou ditar comandos de áudio: *"Aumente o preço de todos os refrigerantes em R$ 1,50 e pause o hambúrguer de picanha porque acabou a carne hoje"*.
- **Segurança:** O assistente gera uma visualização de "Antes vs. Depois" (Diff) no painel administrativo e exige confirmação com 1 clique do gerente para aplicar as alterações em lote.