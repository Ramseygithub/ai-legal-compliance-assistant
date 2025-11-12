from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: str
    filename: str
    message: str

class DocumentInfo(BaseModel):
    id: str
    filename: str
    upload_time: datetime
    file_type: str
    status: str
    metadata: Optional[Dict[str, Any]] = None

class TextSegment(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None

class KnowledgeGraphNode(BaseModel):
    id: str
    type: str
    properties: Dict[str, Any]

class KnowledgeGraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    properties: Dict[str, Any] = {}

class ComplianceQuery(BaseModel):
    query: Optional[str] = Field(None, description="合规查询文本")
    business_data: Optional[Dict[str, Any]] = Field(None, description="业务数据字典")

class ComplianceResult(BaseModel):
    compliance_status: str
    confidence: float
    violated_regulations: List[str]
    recommendations: List[str]
    referenced_documents: List[str]

class RAGQuery(BaseModel):
    question: str
    top_k: int = 5

class RAGResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]