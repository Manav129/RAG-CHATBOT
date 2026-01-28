# AI Customer Support Agent

A modern AI-powered customer support system using **RAG (Retrieval Augmented Generation)** to answer questions from PDF documents and automatically create support tickets for complaints.

## 🎯 Features

- **Intelligent Q&A**: Answers customer questions using company documentation
- **Citation System**: Provides source references for every answer
- **Auto-Ticket Creation**: Detects complaints and creates support tickets automatically
- **Ticket Management**: Track and update support tickets
- **Modern UI**: Clean, responsive chat interface
- **RAG Pipeline**: Combines Qdrant vector search with Groq LLM

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Groq LLM** - Fast AI inference (Llama 3.1 8B)
- **Qdrant Cloud** - Vector database for semantic search
- **MySQL** - Relational database for tickets
- **SQLAlchemy** - Python ORM
- **SentenceTransformers** - Text embeddings (all-MiniLM-L6-v2)

### Frontend
- **HTML/CSS/JavaScript** - Vanilla, no frameworks
- **Modern UI** - Clean, professional design

## 📁 Project Structure

```
AI Customer Support Agent using RAG/
├── app/
│   ├── config.py              # Configuration & environment variables
│   ├── embedding_service.py   # Text-to-vector conversion
│   ├── pdf_service.py         # PDF processing & chunking
│   ├── qdrant_service.py      # Vector database operations
│   ├── llm_service.py         # Groq LLM integration
│   ├── rag_pipeline.py        # RAG orchestration
│   ├── models.py              # SQLAlchemy models
│   ├── ticket_service.py      # Ticket CRUD operations
│   └── main.py                # FastAPI application
├── frontend/
│   ├── index.html             # Chat UI
│   ├── style.css              # Styling
│   └── script.js              # Client-side logic
├── data/docs/                 # PDF documents
├── scripts/
│   └── generate_sample_pdfs.py
├── .github/workflows/
│   └── deploy.yml             # CI/CD pipeline
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Local development
├── render.yaml                # Render deployment config
├── vercel.json                # Vercel deployment config
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── DEPLOYMENT.md              # Deployment guide
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- Git

### 1. Clone Repository

```bash
git clone https://github.com/Manav129/RAG-CHATBOT.git
cd RAG-CHATBOT
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GROQ_API_KEY=your_groq_api_key
MYSQL_PASSWORD=your_mysql_password
QDRANT_URL=http://localhost:6333
```

Get free API keys:
- **Groq**: https://console.groq.com/keys
- **Qdrant Cloud**: https://cloud.qdrant.io

### 5. Setup MySQL Database

```sql
CREATE DATABASE customer_support;
```

### 6. Run Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Server will start at: http://localhost:8001

### 7. Open Frontend

Navigate to: http://localhost:8001 (frontend served via StaticFiles)

### 8. Ingest Documents

Upload your PDFs to `data/docs/` then run:

```bash
curl -X POST http://localhost:8001/ingest
```

##  API Endpoints

### Chat
```http
POST /chat
Content-Type: application/json

{
  "query": "What is your refund policy?"
}
```

### Get Ticket
```http
GET /tickets/{ticket_id}
```

### Update Ticket Status
```http
PUT /tickets/{ticket_id}/status
Content-Type: application/json

{
  "status": "closed"
}
```

### Health Check
```http
GET /health
```

### Stats
```http
GET /stats
```

### Ingest Documents
```http
POST /ingest
```

## 🎨 How It Works

### RAG Pipeline

1. **Document Ingestion**
   - PDFs are split into chunks (500 chars)
   - Each chunk is converted to embeddings (384-dimensional vectors)
   - Embeddings stored in Qdrant vector database

2. **Query Processing**
   - User query is converted to embedding
   - Qdrant finds 3 most similar document chunks
   - Retrieved documents + query sent to Groq LLM

3. **Response Generation**
   - LLM generates answer using only retrieved documents
   - Citations included for transparency
   - If complaint detected → auto-create ticket

4. **Ticket System**
   - Complaints trigger automatic ticket creation
   - Tickets stored in MySQL with SQLAlchemy ORM
   - Status tracking: open → in_progress → closed

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq LLM API key | Required |
| `MYSQL_HOST` | MySQL hostname | localhost |
| `MYSQL_PORT` | MySQL port | 3306 |
| `MYSQL_USER` | MySQL username | root |
| `MYSQL_PASSWORD` | MySQL password | Required |
| `MYSQL_DATABASE` | Database name | customer_support |
| `QDRANT_URL` | Qdrant server URL | http://localhost:6333 |
| `QDRANT_API_KEY` | Qdrant API key (cloud) | Optional |
| `QDRANT_COLLECTION` | Collection name | support_docs |
| `ENVIRONMENT` | Environment mode | development |

## 🧪 Testing

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is your refund policy?"}'
```

### Test Ticket Creation

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "My product is broken and I am very frustrated!"}'
```

### Check Health

```bash
curl http://localhost:8001/health
```

## 📊 Interview Questions

### Why RAG over fine-tuning?
RAG allows updating knowledge without retraining. Add new PDFs → instant updates. Fine-tuning is expensive and time-consuming.

### Why Qdrant?
Fast vector similarity search, good Python SDK, free tier, and supports both local and cloud deployment.

### Why SQLAlchemy?
ORM prevents SQL injection, makes code more Pythonic, easier to maintain than raw SQL queries.

### Why Groq?
Free tier, extremely fast inference, good model quality (Llama 3.1 8B), simple API.

### How does complaint detection work?
Keyword matching on strong negative words: frustrated, angry, terrible, broken, damaged. If found → auto-create ticket.

### How are embeddings generated?
Using SentenceTransformers model `all-MiniLM-L6-v2` which converts text to 384-dimensional vectors representing semantic meaning.

### What is chunking?
Breaking documents into smaller pieces (500 chars) so retrieval is more precise. Overlap (50 chars) maintains context between chunks.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📝 License

This project is open source and available under the MIT License.

## 🙋 Support

For deployment help, see [DEPLOYMENT.md](DEPLOYMENT.md)

For issues, create a GitHub issue or contact the maintainer.

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **Qdrant**: https://qdrant.tech/documentation
- **Groq**: https://console.groq.com/docs
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **RAG Tutorial**: https://www.pinecone.io/learn/retrieval-augmented-generation

---

**Built with ❤️ using Python, FastAPI, and AI**
