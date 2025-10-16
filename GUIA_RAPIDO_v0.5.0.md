# Guia Rápido - Orquestra v0.5.0

Guia rápido para usar as novas funcionalidades da versão 0.5.0.

## 🌊 1. Streaming (Respostas em Tempo Real)

### Instalação
Não requer dependências adicionais. Use com OpenAI ou Anthropic.

### Uso Básico

```python
from orquestra import ReactAgent

# Criar agente
agent = ReactAgent(
    name="Assistant",
    provider="gpt-4o-mini"  # ou "claude-3-5-sonnet-20241022"
)

# Streaming síncrono
for chunk in agent.stream("Conte uma história curta"):
    print(chunk, end="", flush=True)

print("\n")  # Nova linha no final
```

### Streaming Assíncrono

```python
import asyncio

async def main():
    agent = ReactAgent(name="Assistant", provider="gpt-4o-mini")

    async for chunk in agent.astream("Explique IA em 2 frases"):
        print(chunk, end="", flush=True)

    print()

asyncio.run(main())
```

### Com Tools

O streaming funciona normalmente com tools - a execução da tool não é streamed, mas a resposta final sim:

```python
agent = ReactAgent(name="Assistant", provider="gpt-4o-mini")

@agent.tool()
def get_weather(city: str) -> str:
    """Get weather for a city"""
    return f"Weather in {city}: Sunny, 25°C"

# Stream com tool calling
for chunk in agent.stream("What's the weather in Paris?"):
    print(chunk, end="", flush=True)
```

---

## 🔍 2. Vector Database & RAG

### Instalação

```bash
uv add orquestra --optional vectordb
```

### Configuração Básica

```python
from orquestra.embeddings import OpenAIEmbeddings
from orquestra.vectorstores import ChromaVectorStore, Document

# 1. Criar embedding provider
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"  # Mais rápido e barato
    # model="text-embedding-3-large"  # Melhor qualidade
)

# 2. Criar vector store
store = ChromaVectorStore(
    collection_name="meu_conhecimento",
    embedding_provider=embeddings,
    persist_directory="./chroma_db"  # Opcional: persistir dados
)

# 3. Adicionar documentos
docs = [
    Document(
        content="Python é uma linguagem de programação de alto nível.",
        metadata={"source": "docs", "language": "pt"}
    ),
    Document(
        content="JavaScript é usado principalmente para desenvolvimento web.",
        metadata={"source": "docs", "language": "pt"}
    ),
]

ids = store.add(docs)
print(f"Adicionados {len(ids)} documentos")
```

### Busca Semântica

```python
# Buscar por similaridade
results = store.search(
    query="linguagens de programação",
    limit=5,
    filter={"language": "pt"}  # Filtro opcional
)

for result in results:
    print(f"Score: {result.score:.2f}")
    print(f"Content: {result.document.content}")
    print(f"Metadata: {result.document.metadata}")
    print()
```

### RAG Completo com Agente

```python
from orquestra import ReactAgent

# Criar agente
agent = ReactAgent(
    name="Knowledge Assistant",
    provider="gpt-4o-mini"
)

# Adicionar tool de busca
@agent.tool()
def search_knowledge(query: str) -> str:
    """Buscar na base de conhecimento"""
    results = store.search(query, limit=3)

    if not results:
        return "Nenhuma informação encontrada."

    context = "\n\n".join([
        f"[Relevância {r.score:.0%}] {r.document.content}"
        for r in results
    ])

    return f"Informações relevantes:\n{context}"

# Agente usa conhecimento automaticamente
answer = agent.run("Quais linguagens de programação você conhece?")
print(answer)
```

### Com KnowledgeMemory

```python
from orquestra import KnowledgeMemory

# Criar memória com vector store
memory = KnowledgeMemory(vector_store=store)

# Adicionar conhecimento
memory.add("Orquestra é um framework de agentes AI")
memory.add("Suporta OpenAI, Anthropic, Gemini e Ollama")

# Buscar semanticamente
results = memory.search("framework IA", limit=3)
for result in results:
    print(result.content)
```

---

## 🤝 3. Orquestração de Agentes

### Workflow Sequencial

```python
from orquestra import ReactAgent
from orquestra.orchestration import SequentialWorkflow

# Criar agentes especializados
researcher = ReactAgent(
    name="Pesquisador",
    description="Pesquisa informações sobre um tópico",
    provider="gpt-4o-mini"
)

writer = ReactAgent(
    name="Escritor",
    description="Escreve artigos baseados em pesquisa",
    provider="gpt-4o-mini"
)

editor = ReactAgent(
    name="Editor",
    description="Revisa e melhora textos",
    provider="gpt-4o-mini"
)

# Criar workflow
workflow = SequentialWorkflow(name="Produção de Artigo")
workflow.add_agent(researcher)  # Passo 1: Pesquisar
workflow.add_agent(writer)      # Passo 2: Escrever
workflow.add_agent(editor)      # Passo 3: Editar

# Executar - cada agente recebe o output do anterior
result = workflow.run(
    "Escreva um artigo sobre computação quântica",
    temperature=0.7
)

print(result)
```

### Workflow Customizado

```python
from orquestra.orchestration import Workflow

# Criar workflow customizado
workflow = Workflow(name="Custom")

# Adicionar steps customizados
workflow.add_step(
    name="research",
    func=researcher.run,
    pass_previous=True  # Recebe input do step anterior
)

workflow.add_step(
    name="custom_processing",
    func=lambda text: text.upper(),  # Função customizada
    pass_previous=True
)

workflow.add_step(
    name="finalize",
    func=editor.run,
    pass_previous=True
)

# Executar
result = workflow.run("Initial input")
```

---

## 🎯 Combinando Tudo: RAG + Streaming + Orchestration

```python
from orquestra import ReactAgent
from orquestra.embeddings import OpenAIEmbeddings
from orquestra.vectorstores import ChromaVectorStore, Document
from orquestra.orchestration import SequentialWorkflow

# 1. Setup vector store
embeddings = OpenAIEmbeddings()
store = ChromaVectorStore(
    collection_name="knowledge",
    embedding_provider=embeddings
)

# Adicionar conhecimento
store.add([
    Document(content="Informação técnica sobre IA..."),
    Document(content="Dados sobre machine learning..."),
])

# 2. Criar agentes com RAG
research_agent = ReactAgent(name="Researcher", provider="gpt-4o-mini")

@research_agent.tool()
def search_docs(query: str) -> str:
    """Buscar documentação"""
    results = store.search(query, limit=3)
    return "\n".join([r.document.content for r in results])

writer_agent = ReactAgent(name="Writer", provider="gpt-4o-mini")

# 3. Criar workflow
workflow = SequentialWorkflow()
workflow.add_agent(research_agent)
workflow.add_agent(writer_agent)

# 4. Executar com streaming
print("Gerando resposta...\n")
for chunk in writer_agent.stream(
    workflow.run("Explique IA de forma simples")
):
    print(chunk, end="", flush=True)

print("\n\nConcluído!")
```

---

## 📝 Dicas e Best Practices

### Streaming
- ✅ Use `flush=True` no print para ver chunks em tempo real
- ✅ Combine com frameworks web (FastAPI, Flask) para UIs responsivas
- ⚠️ Tool execution não é streamed (apenas a resposta final)

### Vector Databases
- ✅ Use `text-embedding-3-small` para economia
- ✅ Use `persist_directory` para não perder dados
- ✅ Adicione metadata para filtros mais precisos
- ⚠️ ChromaDB requer instalação separada: `uv add chromadb`

### Orquestração
- ✅ Use agentes especializados (researcher, writer, editor)
- ✅ Configure temperature diferente para cada agente
- ✅ Teste cada agente individualmente antes do workflow
- ⚠️ Workflows podem consumir muitos tokens

---

## 🔧 Troubleshooting

### Streaming não funciona
```python
# Verificar se provider suporta streaming
if agent.provider.supports_streaming():
    print("Streaming suportado!")
else:
    print("Provider não suporta streaming")
```

### Vector store não encontra resultados
```python
# Verificar se há documentos
count = store.count()
print(f"Documentos no store: {count}")

# Tentar sem filtros
results = store.search(query, limit=10)  # Sem filter=
```

### ChromaDB não instalado
```bash
uv add chromadb
# ou
pip install chromadb
```

---

## 📚 Recursos Adicionais

- **Exemplos completos**: `/examples/`
  - `streaming_example.py`
  - `vector_rag_example.py`

- **Documentação**: `README.md`
- **Changelog**: `CHANGELOG.md`
- **Implementação**: `IMPLEMENTACAO_v0.5.0.md`

---

## ❓ FAQ

**P: Posso usar streaming sem tools?**
R: Sim! Funciona perfeitamente sem tools.

**P: ChromaDB funciona em produção?**
R: Sim! Use `persist_directory` para dados persistentes.

**P: Preciso de GPU para embeddings?**
R: Não com OpenAI embeddings (API). Sim com embeddings locais (futura feature).

**P: Workflows são assíncronos?**
R: SequentialWorkflow é síncrono. ParallelWorkflow (futuro) será async.

**P: Posso combinar streaming + RAG?**
R: Sim! Veja exemplo combinado acima.

---

**Versão**: 0.5.0
**Data**: 16/10/2025
**Autor**: Marcos Oliveira
