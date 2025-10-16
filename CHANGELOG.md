# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.5.0] - 2025-10-16

### Adicionado - Respostas em Streaming
- **Suporte a Streaming**: Agentes agora podem fazer streaming de respostas em tempo real
  - Métodos `stream()` e `astream()` adicionados a `Agent` e `ReactAgent`
  - Streaming implementado nos providers OpenAI e Anthropic
  - Nova classe `StreamChunk` para manipular dados de streaming
  - Suporte completo para streaming com chamadas de ferramentas
  - Exemplo: `examples/streaming_example.py`

### Adicionado - Integração com Bancos de Dados Vetoriais
- **Módulo de Embeddings**: Novos provedores de embeddings para representações vetoriais
  - Classe abstrata base `EmbeddingProvider`
  - `OpenAIEmbeddings` para modelos de embeddings da OpenAI
  - Suporte para `text-embedding-3-small` e `text-embedding-3-large`

- **Vector Stores**: Capacidades de busca semântica para bases de conhecimento
  - Classe abstrata base `VectorStore` com tipos `Document` e `SearchResult`
  - Integração `ChromaVectorStore` para uso fácil de banco de dados vetorial
  - Suporte async completo com `aadd()`, `asearch()`, `adelete()`, `aclear()`

- **KnowledgeMemory Aprimorada**:
  - Backend opcional de vector store para busca semântica
  - Compatível com busca baseada em palavras-chave
  - Fallback automático para busca por palavras-chave se não houver vector store

- **Exemplo de RAG**: Exemplo completo de Retrieval-Augmented Generation
  - Exemplo: `examples/vector_rag_example.py`
  - Mostra como construir bases de conhecimento e responder perguntas com contexto

### Adicionado - Orquestração de Agentes
- **Sistema de Workflow**: Encadear múltiplos agentes
  - Classe `Workflow` para definir workflows de agentes
  - `SequentialWorkflow` para passar resultados entre agentes
  - Placeholder para `ParallelWorkflow` (em desenvolvimento)

### Modificado
- Classe `Agent` atualizada para suportar métodos de streaming
- Interface de provider aprimorada com método `supports_streaming()`
- Melhor tratamento de erros em cenários de streaming

### Dependências
- Dependências opcionais adicionadas:
  - `vectordb`: Suporte a ChromaDB (`chromadb>=0.4.0`)
  - `qdrant`: Suporte a Qdrant (`qdrant-client>=1.7.0`)

## [0.4.0] - 2025-10-15

### Preparação
- Preparação para implementação do Model Context Protocol (MCP)
- Estrutura base do módulo MCP criada
- Documentação do plano de implementação MCP

### Planejado
- Implementação completa do servidor MCP
- Implementação do cliente MCP
- Suporte a transporte stdio e HTTP/SSE
- Integração com sistema de agents e tools existente
- Exemplos práticos de uso do MCP

## [0.3.0] - 2025-01-XX

### Adicionado
- Suporte a data e hora atual para agentes
- Sistema de logging com modos verbose e debug
- Parâmetros `current_date` e `current_datetime` para agents
- Logs detalhados de execução de ferramentas
- Rastreamento de tempo de execução

### Melhorado
- System prompts agora incluem contexto de data/hora
- Melhor visibilidade do fluxo de execução
- Mensagens de log mais informativas e estruturadas

## [0.2.4] - 2025-01-XX

### Adicionado
- Tratamento de exceções melhorado
- Atualização de dependências do pacote

## [0.2.2] - 2025-01-XX

### Adicionado
- Suporte a arquivos .env nos exemplos
- Melhorias na documentação

## [0.2.1] - 2025-01-XX

### Adicionado
- Suporte oficial para Python 3.12+
- Melhorias na compatibilidade

## Versões Anteriores

Versões anteriores a 0.2.1 não possuem changelog detalhado.
