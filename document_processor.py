import PyPDF2
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import uuid
from datetime import datetime

class DocumentProcessor:
    def __init__(self):
        self.supported_types = {'.pdf', '.html', '.htm', '.txt', '.doc', '.docx'}
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    # Clean up excess line breaks in PDF
                    page_text = re.sub(r'\n(?!\n)', ' ', page_text)  # Replace single line breaks with spaces
                    page_text = re.sub(r'\s+', ' ', page_text)  # Merge multiple spaces into one
                    text += page_text + "\n\n"  # Separate pages with double line breaks
        except Exception as e:
            raise Exception(f"PDF parsing failed: {str(e)}")
        return text.strip()
    
    def extract_text_from_html(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                text = soup.get_text()
                text = re.sub(r'\n+', '\n', text)
                return text.strip()
        except Exception as e:
            raise Exception(f"HTML parsing failed: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                return text.strip()
        except Exception as e:
            raise Exception(f"Text file parsing failed: {str(e)}")
    
    def segment_text(self, text: str, max_length: int = 512) -> List[Dict[str, Any]]:
        sentences = re.split(r'[.。!！?？；;]', text)
        segments = []
        current_segment = ""
        segment_id = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_segment + sentence) <= max_length:
                current_segment += sentence + "。"
            else:
                if current_segment:
                    segments.append({
                        "id": str(uuid.uuid4()),
                        "content": current_segment.strip(),
                        "segment_index": segment_id,
                        "length": len(current_segment),
                        "created_at": datetime.now().isoformat()
                    })
                    segment_id += 1
                current_segment = sentence + "。"
        
        if current_segment:
            segments.append({
                "id": str(uuid.uuid4()),
                "content": current_segment.strip(),
                "segment_index": segment_id,
                "length": len(current_segment),
                "created_at": datetime.now().isoformat()
            })
        
        return segments
    
    def extract_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        # Calculate word count correctly (Chinese by characters, English by word splitting)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        word_count = chinese_chars + english_words
        
        # Improved paragraph counting (based on double line breaks or obvious paragraph markers)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paragraphs:  # If no double line breaks, try single line breaks
            paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]  # Only count lines >50 as paragraphs
        paragraph_count = len(paragraphs)
        
        law_keywords = ['law', 'regulation', 'statute', 'provision', 'measure', 'rule', 'notice', 'announcement']
        detected_keywords = [kw for kw in law_keywords if kw in text]
        
        metadata = {
            "filename": filename,
            "word_count": word_count,
            "character_count": len(text),  # Keep character count statistics
            "paragraph_count": paragraph_count,
            "detected_keywords": detected_keywords,
            "extraction_time": datetime.now().isoformat()
        }
        
        return metadata
    
    def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        file_ext = filename.lower().split('.')[-1]
        
        if f'.{file_ext}' not in self.supported_types:
            raise Exception(f"Unsupported file type: {file_ext}")
        
        if file_ext == 'pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_ext in ['html', 'htm']:
            text = self.extract_text_from_html(file_path)
        elif file_ext == 'txt':
            text = self.extract_text_from_txt(file_path)
        elif file_ext in ['doc', 'docx']:
            # For now, treat doc/docx as text files - in production you'd use python-docx
            text = self.extract_text_from_txt(file_path)
        else:
            raise Exception(f"Unsupported file type: {file_ext}")
        
        if not text.strip():
            raise Exception("Document content is empty")
        
        segments = self.segment_text(text)
        metadata = self.extract_metadata(text, filename)
        
        return {
            "text": text,
            "segments": segments,
            "metadata": metadata
        }