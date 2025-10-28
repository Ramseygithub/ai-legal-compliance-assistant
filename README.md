# 🧠 AI Regulatory Compliance Assistance System

> An **AI-based legal compliance analysis platform** integrating **Alibaba Cloud Bailian** AI capabilities for regulatory document processing, semantic retrieval, compliance analysis, and knowledge-graph construction.

---

## 🚀 System Overview
The **AI Regulatory Compliance Assistance System** automates compliance interpretation across complex legal frameworks.  
It supports PDF / HTML regulation ingestion, AI-powered question answering, and explainable rule mapping through RAG + knowledge-graph techniques.

---

## ✨ Key Features

### 1. Document Processing Module
- 📄 Upload **PDF** or **HTML** regulatory documents  
- 🔍 Automatic text extraction and segmentation  
- 🧾 Metadata extraction and storage  

### 2. Vectorization & Embedding Module
- 🧠 Uses **Alibaba Cloud Bailian Embedding API** for text vectorization  
- 🗂 Builds **vector indexes** for regulations  
- 🔎 Enables **semantic similarity search**

### 3. Knowledge Graph Construction
- ⚖️ Extracts legal entities *(articles, violations, penalties, etc.)*  
- 🧩 Identifies inter-entity relationships  
- 🗃 Outputs a **JSON-formatted knowledge graph**

### 4. Semantic Retrieval & Q&A (RAG)
- 📚 Regulation retrieval based on **vector similarity**  
- 🕸 Enhances context with **knowledge graphs**  
- 💬 Generates professional answers via **Qwen-Turbo model**

### 5. Compliance Determination Workflow
- 🧮 Multi-factor logical analysis for business compliance  
- 📊 Risk-level evaluation  
- ⚠️ Violation identification & recommendation generation

### 6. Front-End Interactive Interface
- 🗂 Document upload & management  
- 🤖 Real-time Q&A interaction  
- 📑 Compliance analysis report  
- 🔗 Knowledge-graph query  
- 📈 System statistics dashboard  

---

## 🏗 Technical Architecture

### Backend Stack
| Component | Purpose |
|------------|----------|
| **FastAPI** | Web framework |
| **Python** | Core development language |
| **Alibaba Cloud Bailian** | AI model service |
| **scikit-learn** | Vector similarity computation |
| **PyPDF2** | PDF parsing |
| **BeautifulSoup4** | HTML parsing |

### Frontend Stack
| Component | Purpose |
|------------|----------|
| **HTML5** | Page structure |
| **CSS3** | Style design |
| **JavaScript** | Interaction logic |
| **Responsive Design** | Multi-device adaptation |

### Data Storage
- 🗂 **JSON files** – document / vector / graph data  
- 💾 **Local file system** – for uploaded files  

---

## Environment Configuration

### 1. Basic Environment
```bash
Python 3.8+
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variable Configuration
Create a .env file and configure it as follows:
```env
ALIBABA_API_KEY="your api key"
QWEN_MODEL=qwen-turbo
EMBEDDING_MODEL=text-embedding-v1
DATA_DIR=./data
UPLOAD_DIR=./uploads
```

## Quick Start

### Method 1: Use the Launch Script
```bash
python run_system.py
```
Select “4. Full Test” to perform a complete system test.

### Method 2: Manual Start
# Start the service
uvicorn main:app --host 0.0.0.0 --port 8000

# Access the system
http://localhost:8000
```

## API Documentation

After the system starts, visit http://localhost:8000/docs to view the complete API documentation.

### Core API Endpoints
	•	POST /api/upload-document - Upload regulatory document
	•	GET /api/documents - Retrieve document list
	•	POST /api/build-knowledge-graph - Build knowledge graph
	•	POST /api/ask - Regulatory Q&A
	•	POST /api/compliance-analysis - Compliance analysis
	•	GET /api/search-regulations - Search regulations
	•	GET /api/knowledge-graph/query - Query knowledge graph
	•	GET /api/statistics - System statistics

## User Guide

### 1. Document Upload
1. Go to the "Document Upload" tab  
2. Select a regulatory file in **PDF** or **HTML** format  
3. Click **Upload** — the system will automatically process the document  

### 2. Regulatory Q&A
1. Go to the "Regulatory Q&A" tab  
2. Enter a regulation-related question  
3. The system will provide a professional answer based on **RAG technology**  

### 3. Compliance Analysis
1. Go to the "Compliance Analysis" tab  
2. Fill in the business type and detailed description  
3. Obtain a compliance analysis report and recommendations  

### 4. Knowledge Graph
1. Go to the "Knowledge Graph" tab  
2. Build a knowledge graph (using already uploaded documents)  
3. Query related information for specific entities  

## Testing and Validation

The system includes a complete API testing suite:

```bash
# Run all tests
python tests/test_api.py

# Run with pytest
pytest tests/test_api.py -v

## Directory Structure

```
AI_Regulatory_Compliance_Assistance_System/
├── app/                    # Core application module
│   ├── init.py
│   ├── models.py           # Data models
│   ├── storage.py          # Data storage
│   ├── document_processor.py  # Document processing
│   ├── ai_client.py        # AI service client
│   ├── vector_service.py   # Vector services
│   ├── knowledge_graph.py  # Knowledge graph
│   ├── rag_service.py      # RAG service
│   ├── compliance_analyzer.py  # Compliance analysis
│   └── api.py              # API routing
├── static/                 # Front-end static files
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/                  # Test files
│   └── test_api.py
├── data/                   # Data storage directory
├── uploads/                # File upload directory
├── main.py                 # Main application entry point
├── requirements.txt        # Dependency file
├── .env                    # Environment configuration
├── run_system.py           # Launch script
└── README.md               # System documentation
```

## Notes

1. **API Key**: Ensure that your Alibaba Cloud Bailian API key is valid and has sufficient quota.  
2. **File Formats**: Currently supports PDF and HTML formats; make sure the documents are clear and readable.  
3. **Network Connection**: A stable internet connection is required to access Alibaba Cloud services.  
4. **Storage Space**: Ensure there is enough disk space to store uploaded documents and generated data.  

## Future Enhancements

- Support for additional document formats (Word, TXT, etc.)  
- User permission management  
- Integration with more AI model options  
- Database persistence  
- Distributed deployment support  

## Technical Support

If any issues occur, please check the following:  
1. Whether environment variables are configured correctly  
2. Whether the network connection is stable  
3. Whether the API key is valid  
4. Review console error logs for troubleshooting  

---

© 2025 AI Regulatory Compliance Assistance System | Powered by Alibaba Cloud Bailian Platform
