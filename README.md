## 🏗️ Arquitetura Geral do Sistema 
```
┌────────────────┐     ┌──────────────────┐    ┌─────────────────┐
│   User Query   │───▶│   Orchestrator   │───▶│  Report Engine  │
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
