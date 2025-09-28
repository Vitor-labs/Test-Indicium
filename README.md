## 🏗️ Arquitetura Geral do Sistema 
```
┌────────────────┐     ┌──────────────────┐    ┌─────────────────┐
│   User Query   │────▶│   Orchestrator   │───▶│  Report Engine  │
└────────────────┘     └──────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼─────────────────┐
                ▼               ▼                 ▼
          ┌─────────────┐  ┌─────────────┐ ┌─────────────┐
          │SQL Agent    │  │Vector Agent │ │LLM Agent    │
          └─────────────┘  └─────────────┘ └─────────────┘
                 │               │               │
                 ▼               ▼               ▼
          ┌─────────────┐  ┌─────────────┐ ┌─────────────┐
          │Relational DB│  │Vector DB    │ │Knowledge    │
          │(PostgreSQL, │  │(Pinecone,   │ │Base/Context │
          │ MySQL, etc.)│  │ Weaviate,   │ └─────────────┘
          └─────────────┘  │ Chroma)     │
                           └─────────────┘
```
### Pre-requisits:
1. Crie um `.env` baseado no `exemple.env` fornecido.
2. Crie as chaves de API necessrias para a NEWs API e OpenAI.

### Como rodar:
1. sincronize o ambiente (use o uv, é mais facil)
```bash
uv sync
``` 
2. suba os containers necessarios:
```bash
docker-compose up -d
```
3. Rode o notebook `1.0-Download_Data.ipynb`
   - ele vai baixar as fontes de dados, dividir por ambientes e criar a coleção no Qdrant

### 2. **Core Components**

#### **Query Orchestrator**
- **Function**: Intent classification and query routing
- **Responsibilities**:
  - Parse user queries to determine data requirements
  - Route queries to appropriate agents (SQL, vector, or both)
  - Aggregate results from multiple sources
  - Handle query optimization and caching

#### **SQL Agent**
- **Function**: Relational database querying
- **Features**:
  - Schema awareness and metadata understanding
  - Query validation and optimization
  - Result formatting and aggregation

#### **Vector Agent**
- **Function**: Semantic search and retrieval
- **Features**:
  - Similarity search across unstructured data
  - Hybrid search (dense + sparse retrieval)
  - Relevance scoring and filtering

#### **Report Generation Engine**
- **Function**: Synthesize multi-source data into coherent reports
- **Features**:
  - Template-based report generation
  - Data visualization integration
  - Multi-format output (PDF, HTML, JSON)
