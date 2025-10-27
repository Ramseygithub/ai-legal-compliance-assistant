AI Regulatory Compliance Assistance System

System Overview

This is an AI-based legal compliance analysis platform that integrates the AI capabilities of Alibaba Cloud’s Bailian platform. It provides functions such as regulatory document processing, semantic retrieval, compliance analysis, and knowledge graph construction.

Key Features

1. Document Processing Module
	•	Supports uploading PDF and HTML regulatory documents
	•	Automatically extracts and segments text
	•	Extracts and stores metadata

2. Vectorization and Embedding Module
	•	Uses Alibaba Cloud Bailian embedding API for text vectorization
	•	Builds a vector index of regulatory documents
	•	Supports semantic similarity search

3. Knowledge Graph Construction
	•	Automatically extracts legal entities (articles, violations, penalties, etc.)
	•	Identifies relationships among entities
	•	Builds a JSON-formatted knowledge graph

4. Semantic Retrieval and Q&A (RAG)
	•	Regulation retrieval based on vector similarity
	•	Context enhancement with knowledge graphs
	•	Generates professional answers using the Qwen-Turbo model

5. Compliance Determination Workflow
	•	Multi-factor logical analysis for business compliance
	•	Risk level evaluation
	•	Violation identification and recommendation generation

6. Front-End Interactive Interface
	•	Document upload management
	•	Real-time Q&A interaction
	•	Compliance analysis report
	•	Knowledge graph query
	•	System statistics dashboard

Technical Architecture

Backend Tech Stack
	•	FastAPI – Web framework
	•	Python – Core development language
	•	Alibaba Cloud Bailian – AI model service
	•	scikit-learn – Vector similarity computation
	•	PyPDF2 – PDF document parsing
	•	BeautifulSoup4 – HTML document parsing

Frontend Tech Stack
	•	HTML5 – Page structure
	•	CSS3 – Style design
	•	JavaScript – Interaction logic
	•	Responsive Design – Multi-device adaptation

Data Storage
	•	JSON files – For document, vector, and knowledge graph data
	•	Local file system – For uploaded files

1. Environment Setup

1. Basic Environment
Python 3.8+

2. Install Dependencies
pip install -r requirements.txt

3. Environment Variable Configuration
ALIBABA_API_KEY="API"
QWEN_MODEL=qwen-turbo
EMBEDDING_MODEL=text-embedding-v1
DATA_DIR=./data
UPLOAD_DIR=./uploads

Quick Start

Method 1: Use the Launch Script
python run_system.py

Method 2: Manual Start
# Start the service
uvicorn main:app --host 0.0.0.0 --port 8000

# Access the system
http://localhost:8000

API Documentation

After system startup, visit http://localhost:8000/docs to view the full API documentation.

Core API Endpoints
	•	POST /api/upload-document – Upload a regulatory document
	•	GET /api/documents – Retrieve document list
	•	POST /api/build-knowledge-graph – Build knowledge graph
	•	POST /api/ask – Regulatory Q&A
	•	POST /api/compliance-analysis – Compliance analysis
	•	GET /api/search-regulations – Search regulations
	•	GET /api/knowledge-graph/query – Query knowledge graph
	•	GET /api/statistics – System statistics

User Guide

1. Document Upload
	1.	Go to the “Document Upload” tab
	2.	Select a PDF or HTML regulatory file
	3.	Click Upload — the system will process the document automatically

2. Regulatory Q&A
	1.	Go to the “Regulatory Q&A” tab
	2.	Enter a question about regulations
	3.	The system will generate a professional answer using RAG technology

3. Compliance Analysis
	1.	Go to the “Compliance Analysis” tab
	2.	Enter business type and detailed description
	3.	Receive a compliance analysis report and recommendations

4. Knowledge Graph
	1.	Go to the “Knowledge Graph” tab
	2.	Build a graph from uploaded documents
	3.	Query relationships for specific entities

Testing and Validation

The system includes a full API testing suite:
# Run all tests
python tests/test_api.py

# Run with pytest
pytest tests/test_api.py -v

Directory Structure
AI_Regulatory_Compliance_System/
├── app/                    # Core application module
│   ├── __init__.py
│   ├── models.py            # Data models
│   ├── storage.py           # Data storage
│   ├── document_processor.py # Document processing
│   ├── ai_client.py         # AI service client
│   ├── vector_service.py    # Vector services
│   ├── knowledge_graph.py   # Knowledge graph
│   ├── rag_service.py       # RAG service
│   ├── compliance_analyzer.py # Compliance analysis
│   └── api.py               # API routing
├── static/                  # Front-end static files
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/                   # Test files
│   └── test_api.py
├── data/                    # Data storage directory
├── uploads/                 # File upload directory
├── main.py                  # Main application entry
├── requirements.txt          # Dependencies
├── .env                      # Environment configuration
├── run_system.py              # Launch script
└── README.md                  # System documentation

Notes
	1.	API Key – Ensure your Alibaba Cloud Bailian API key is valid and has sufficient quota
	2.	File Formats – Only PDF and HTML are currently supported; documents must be clearly readable
	3.	Network Connection – Requires stable internet access to Alibaba Cloud services
	4.	Storage Space – Ensure sufficient disk space for uploads and generated data

    Future Enhancements
	•	Support for additional document formats (Word, TXT, etc.)
	•	User permission management
	•	Integration with more AI model options
	•	Database persistence
	•	Distributed deployment support

Technical Support

If issues arise, check:
	1.	Environment variable configuration
	2.	Network connectivity
	3.	API key validity
	4.	Console error logs

⸻

© 2025 AI Regulatory Compliance Assistance System | Powered by Alibaba Cloud Bailian Platform