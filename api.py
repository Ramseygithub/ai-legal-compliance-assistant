from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
import uuid
import shutil
from datetime import datetime

from app.models import *
from app.document_processor import DocumentProcessor
from app.vector_service import VectorEmbeddingService
from app.knowledge_graph import KnowledgeGraphBuilder
from app.rag_service import RAGService
from app.compliance_analyzer import ComplianceAnalyzer
from app.storage import storage

router = APIRouter()

doc_processor = DocumentProcessor()
vector_service = VectorEmbeddingService()
kg_builder = KnowledgeGraphBuilder()
rag_service = RAGService()
compliance_analyzer = ComplianceAnalyzer()

@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload legal documents"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename cannot be empty")
        
        file_ext = file.filename.split('.')[-1].lower()
        if f'.{file_ext}' not in doc_processor.supported_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_ext}. Supported types: {', '.join(doc_processor.supported_types)}"
            )
        
        doc_id = str(uuid.uuid4())
        upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{doc_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        processed_data = doc_processor.process_document(file_path, file.filename)
        
        document_info = {
            "id": doc_id,
            "filename": file.filename,
            "file_path": file_path,
            "upload_time": datetime.now().isoformat(),
            "file_type": file_ext,
            "status": "processed",
            "metadata": processed_data["metadata"]
        }
        
        storage.save_document(doc_id, document_info)
        storage.save_segments(doc_id, processed_data["segments"])
        
        vector_service.create_regulation_index(doc_id, processed_data["segments"])
        
        return DocumentUploadResponse(
            success=True,
            document_id=doc_id,
            filename=file.filename,
            message=f"Document uploaded successfully, generated {len(processed_data['segments'])} document segments"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents():
    """Get document list"""
    doc_ids = storage.list_documents()
    documents = []
    
    for doc_id in doc_ids:
        doc_data = storage.load_document(doc_id)
        if doc_data:
            # Return raw data directly to ensure metadata fields are included
            documents.append({
                "id": doc_data["id"],
                "filename": doc_data["filename"],
                "upload_time": doc_data["upload_time"],
                "file_type": doc_data["file_type"],
                "status": doc_data["status"],
                "metadata": doc_data.get("metadata")
            })
    
    return documents

@router.post("/build-knowledge-graph")
async def build_knowledge_graph(doc_ids: Optional[List[str]] = None):
    """Build knowledge graph"""
    try:
        if doc_ids is None:
            doc_ids = storage.list_documents()
        
        if not doc_ids:
            raise HTTPException(status_code=400, detail="No documents available")
        
        graph_data = kg_builder.build_knowledge_graph(doc_ids)
        
        return {
            "success": True,
            "message": "Knowledge graph built successfully",
            "statistics": {
                "nodes": len(graph_data["nodes"]),
                "edges": len(graph_data["edges"]),
                "documents_processed": len(doc_ids)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask", response_model=RAGResponse)
async def ask_question(query: RAGQuery):
    """Legal Q&A"""
    try:
        result = rag_service.ask_question(query.question, query.top_k)
        
        return RAGResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result["sources"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance-analysis", response_model=ComplianceResult)
async def analyze_compliance(query: ComplianceQuery):
    """Compliance analysis"""
    try:
        # Flexible input handling: prioritize business_data, then use query field
        if query.business_data:
            business_data = query.business_data
        elif query.query:
            business_data = {"description": query.query}
        else:
            raise HTTPException(status_code=400, detail="Please provide business_data or query parameter")
        
        result = compliance_analyzer.analyze_compliance(business_data)
        
        return ComplianceResult(
            compliance_status=result["compliance_status"],
            confidence=result.get("risk_score", 0.5),
            violated_regulations=result.get("violated_regulations", []),
            recommendations=result.get("recommendations", []),
            referenced_documents=result.get("relevant_regulations", [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance-analysis-with-doc", response_model=ComplianceResult)
async def analyze_compliance_with_document(
    description: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """Compliance analysis with optional document upload"""
    import tempfile
    
    try:
        business_data = {"description": description}
        
        # If a file is uploaded, process it temporarily
        if file:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            try:
                # Process the document temporarily
                processed_doc = doc_processor.process_document(tmp_file_path, file.filename)
                
                # Extract text from processed segments
                doc_text = ""
                if "segments" in processed_doc:
                    # Combine text from all segments
                    doc_text = "\n".join([seg.get("text", "") for seg in processed_doc["segments"]])[:3000]  # Limit to 3000 chars
                elif "text" in processed_doc:
                    doc_text = processed_doc.get("text", "")[:3000]
                
                # Add document content to the business description for analysis
                if doc_text:
                    business_data["description"] = f"{description}\\n\\User Document:\\n{doc_text}"
                
            finally:
                # Clean up temporary file
                import os
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
        
        # Perform compliance analysis
        result = compliance_analyzer.analyze_compliance(business_data)
        
        return ComplianceResult(
            compliance_status=result["compliance_status"],
            confidence=result.get("risk_score", 0.5),
            violated_regulations=result.get("violated_regulations", []),
            recommendations=result.get("recommendations", []),
            referenced_documents=result.get("relevant_regulations", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-regulations")
async def search_regulations(
    query: str,
    top_k: int = 5,
    min_similarity: float = 0.3
):
    """Search related regulations"""
    try:
        filters = {"min_similarity": min_similarity}
        results = vector_service.search_regulations(query, filters, top_k)
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-graph/query")
async def query_knowledge_graph(entity_name: str, relation_type: Optional[str] = None):
    """Query knowledge graph"""
    try:
        result = kg_builder.query_knowledge_graph(entity_name, relation_type)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_system_statistics():
    """Get system statistics"""
    try:
        doc_count = len(storage.list_documents())
        vector_stats = vector_service.get_vector_statistics()
        kg_stats = kg_builder.get_graph_statistics()
        
        return {
            "documents": {
                "total_count": doc_count
            },
            "vectors": vector_stats,
            "knowledge_graph": kg_stats,
            "system_info": {
                "data_directory": os.getenv("DATA_DIR", "./data"),
                "upload_directory": os.getenv("UPLOAD_DIR", "./uploads")
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance-history")
async def get_compliance_history(limit: int = 10):
    """Get compliance analysis history"""
    try:
        history = compliance_analyzer.get_compliance_history(limit)
        return {
            "history": history,
            "total_records": len(history)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-questions")
async def suggest_related_questions(
    original_question: str,
    num_suggestions: int = 3
):
    """Suggest related questions"""
    try:
        suggestions = rag_service.suggest_related_questions(original_question, num_suggestions)
        
        return {
            "original_question": original_question,
            "suggestions": suggestions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document"""
    try:
        doc_data = storage.load_document(doc_id)
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if os.path.exists(doc_data.get("file_path", "")):
            os.remove(doc_data["file_path"])
        
        doc_file = f"./data/document_{doc_id}.json"
        segments_file = f"./data/segments_{doc_id}.json"
        
        for file_path in [doc_file, segments_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        vectors_data = storage.load_vectors()
        if doc_id in vectors_data:
            del vectors_data[doc_id]
            storage.save_vectors(vectors_data)
        
        return {"success": True, "message": "Document deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))