from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from app.api import router

load_dotenv()

app = FastAPI(title="AI Legal Compliance Assistant System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def customer_portal():
    """Customer portal - Legal Q&A and Compliance Analysis"""
    try:
        with open("static/customer.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>AI Legal Compliance Assistant System</h1>
                <p>Customer portal is being developed...</p>
                <p>API documentation: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)

@app.get("/admin", response_class=HTMLResponse)
async def admin_portal():
    """Admin portal - Document Upload, Knowledge Graph, System Statistics"""
    try:
        with open("static/admin.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>AI Legal Compliance Assistant System - Admin</h1>
                <p>Admin portal is being developed...</p>
                <p>API documentation: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Test page for debugging"""
    with open("test_stats.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Legal Compliance Assistant System is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)