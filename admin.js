class AdminPortal {
    constructor() {
        this.apiBase = '/api';
        this.isUploading = false;
        this.init();
    }

    init() {
        this.initTabs();
        this.initEventListeners();
        this.initUploadFeatures();
        this.loadDocuments();
        this.updateStats();
    }

    initTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.dataset.tab;
                
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                button.classList.add('active');
                document.getElementById(tabName).classList.add('active');
            });
        });
    }

    initEventListeners() {
        // Document upload related
        document.getElementById('selectFilesBtn').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files);
        });

        document.getElementById('refreshDocs').addEventListener('click', () => {
            this.loadDocuments();
        });

        document.getElementById('buildIndexBtn').addEventListener('click', () => {
            this.buildKnowledgeGraph();
        });

        // Document search
        const searchBtn = document.querySelector('.search-btn');
        const searchInput = document.getElementById('docSearch');
        
        searchBtn.addEventListener('click', () => {
            this.searchDocuments();
        });
        
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.searchDocuments();
            }
        });

        // Knowledge Graph
        document.getElementById('buildKG').addEventListener('click', () => {
            this.buildKnowledgeGraph();
        });

        document.getElementById('queryKG').addEventListener('click', () => {
            this.queryKnowledgeGraph();
        });

        // System Statistics
        document.getElementById('getStats').addEventListener('click', () => {
            this.getStatistics();
        });
    }

    initUploadFeatures() {
        const uploadZone = document.getElementById('uploadZone');
        
        // Drag and drop upload
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            this.handleFileSelection(e.dataTransfer.files);
        });
    }

    async handleFileSelection(files) {
        if (this.isUploading) return;
        
        this.isUploading = true;
        const progressDiv = document.getElementById('uploadProgress');
        const resultDiv = document.getElementById('uploadResult');
        
        progressDiv.style.display = 'block';
        resultDiv.innerHTML = '';

        const uploadPromises = Array.from(files).map(file => this.uploadSingleFile(file));
        
        try {
            const results = await Promise.all(uploadPromises);
            const successCount = results.filter(r => r.success).length;
            
            this.showUploadResult(`Successfully uploaded ${successCount}/${files.length} files`, 'success');
            this.loadDocuments();
            this.updateStats();
        } catch (error) {
            this.showUploadResult(`Batch upload failed: ${error.message}`, 'error');
        } finally {
            this.isUploading = false;
            progressDiv.style.display = 'none';
        }
    }

    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.apiBase}/upload-document`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (response.ok && result.success) {
                return { success: true, data: result };
            } else {
                throw new Error(result.detail || 'Upload failed');
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    showUploadResult(message, type = 'info') {
        const resultDiv = document.getElementById('uploadResult');
        resultDiv.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    }

    async updateStats() {
        try {
            console.log('Updating stats from:', `${this.apiBase}/statistics`);
            const response = await fetch(`${this.apiBase}/statistics`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const stats = await response.json();
            console.log('Stats for update:', stats);
            
            const totalDocsElement = document.getElementById('totalDocs');
            const todayUploadsElement = document.getElementById('todayUploads');
            const processingStatusElement = document.getElementById('processingStatus');
            
            if (totalDocsElement) {
                totalDocsElement.textContent = stats.documents.total_count;
            }
            if (todayUploadsElement) {
                todayUploadsElement.textContent = '0'; // Can be fetched from backend
            }
            if (processingStatusElement) {
                processingStatusElement.textContent = 'Ready';
            }
        } catch (error) {
            console.error('Failed to update statistics:', error);
        }
    }

    async searchDocuments() {
        const query = document.getElementById('docSearch').value;
        const listDiv = document.getElementById('documentsList');
        
        if (!query) {
            // If search box is empty, load all documents
            this.loadDocuments();
            return;
        }
        
        listDiv.innerHTML = '<div class="loading">Searching...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/search-regulations?query=${encodeURIComponent(query)}&top_k=10`);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Search failed');
            }
            
            if (result.results.length === 0) {
                listDiv.innerHTML = `<div class="no-documents">No documents found containing "${query}"</div>`;
            } else {
                // Display search results
                const html = `
                    <div class="search-results">
                        <h4>🔍 Search Results</h4>
                        <p class="search-summary">
                            Keyword "<strong>${query}</strong>" - Found ${result.total_found} relevant passages
                        </p>
                        <button class="btn btn-secondary clear-search" onclick="app.loadDocuments()">
                        ✕ Clear Search
                        </button>
                        <div class="results-list">
                            ${result.results.map((item, index) => `
                                <div class="search-result-item">
                                    <div class="result-header">
                                        <span class="result-number">Result ${index + 1}</span>
                                        <span class="result-doc">
                                            ${item.document_name || 'Related Document'}
                                        </span>
                                        <span class="result-score">
                                        Match ${(item.similarity_score * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    <div class="result-content">
                                        ${this.highlightKeywords(item.content, query)}
                                    </div>
                                    <div class="result-meta">
                                        <span class="meta-item">📄 Source: ${item.document_name || 'Legal Document'}</span>
                                        <span class="meta-item">📍 Position: Section ${item.segment_index !== undefined ? item.segment_index + 1 : 'N/A'}</span>
                                        <span class="meta-item">📏 Length: ${item.content ? item.content.length : 0} characters</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                listDiv.innerHTML = html;
            }
        } catch (error) {
            listDiv.innerHTML = `<div class="error-message">Search failed: ${error.message}</div>`;
        }
    }

    highlightKeywords(text, keyword) {
        const regex = new RegExp(`(${keyword})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    async loadDocuments() {
        const listDiv = document.getElementById('documentsList');
        
        try {
            const response = await fetch(`${this.apiBase}/documents`);
            const documents = await response.json();
            
            if (documents.length === 0) {
                listDiv.innerHTML = '<div class="no-documents">No documents uploaded yet</div>';
            } else {
                const html = documents.map(doc => `
                    <div class="document-card">
                        <div class="document-header">
                            <h4>${doc.filename}</h4>
                            <div class="document-actions">
                                <button class="action-btn" onclick="app.viewDocument('${doc.id}')" title="View">👁️</button>
                                <button class="action-btn" onclick="app.deleteDocument('${doc.id}')" title="Delete">🗑️</button>
                            </div>
                        </div>
                        <div class="document-meta">
                            <span>Type: ${doc.file_type.toUpperCase()}</span>
                            <span>Upload: ${new Date(doc.upload_time).toLocaleDateString()}</span>
                        </div>
                        ${doc.metadata ? `
                        <div class="document-stats">
                            <span>Words: ${doc.metadata?.word_count || 'N/A'}</span>
                            <span>Paragraphs: ${doc.metadata?.paragraph_count || 'N/A'}</span>
                        </div>
                        ` : ''}
                    </div>
                `).join('');
                listDiv.innerHTML = html;
            }
        } catch (error) {
            listDiv.innerHTML = `<div class="error-message">Failed to load document list: ${error.message}</div>`;
        }
    }

    viewDocument(docId) {
        console.log('View document:', docId);
        // Implement document viewing functionality
    }

    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document?')) return;
        
        try {
            const response = await fetch(`${this.apiBase}/document/${docId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showUploadResult('Document deleted successfully', 'success');
                this.loadDocuments();
                this.updateStats();
            } else {
                this.showUploadResult('Delete failed', 'error');
            }
        } catch (error) {
            this.showUploadResult(`Delete error: ${error.message}`, 'error');
        }
    }

    async buildKnowledgeGraph() {
        const resultDiv = document.getElementById('kgResult');
        this.showLoading(resultDiv);
        
        try {
            const response = await fetch(`${this.apiBase}/build-knowledge-graph`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showResult(resultDiv, `Knowledge graph built successfully!\nNodes: ${result.statistics.nodes}\nEdges: ${result.statistics.edges}\nDocuments processed: ${result.statistics.documents_processed}`, 'success');
            } else {
                this.showResult(resultDiv, result.detail || 'Build failed', 'error');
            }
        } catch (error) {
            this.showResult(resultDiv, `Build error: ${error.message}`, 'error');
        }
    }

    async queryKnowledgeGraph() {
        const query = document.getElementById('entityQuery').value;
        const resultDiv = document.getElementById('kgResult');
        
        if (!query) {
            this.showResult(resultDiv, 'Please enter entity name', 'error');
            return;
        }
        
        this.showLoading(resultDiv);
        
        try {
            const response = await fetch(`${this.apiBase}/knowledge-graph/query?entity_name=${encodeURIComponent(query)}`);
            const result = await response.json();
            
            if (response.ok) {
                this.displayKnowledgeGraphResult(resultDiv, result);
            } else {
                this.showResult(resultDiv, 'Query failed', 'error');
            }
        } catch (error) {
            this.showResult(resultDiv, `Query error: ${error.message}`, 'error');
        }
    }

    displayKnowledgeGraphResult(container, result) {
        if (!result.nodes || result.nodes.length === 0) {
            this.showResult(container, 'No related entities found', 'warning');
            return;
        }
        
        const html = `
            <div class="kg-result">
                <h4>Query Results (Found ${result.nodes.length} nodes, ${result.edges.length} relationships)</h4>
                
                <div class="kg-nodes">
                    <h5>Related Entities:</h5>
                    <ul>
                        ${result.nodes.map(node => `
                            <li><strong>${node.label}</strong> (${node.type})</li>
                        `).join('')}
                    </ul>
                </div>
                
                ${result.edges.length > 0 ? `
                    <div class="kg-edges">
                        <h5>Entity Relationships:</h5>
                        <ul>
                            ${result.edges.map(edge => {
                                const source = result.nodes.find(n => n.id === edge.source);
                                const target = result.nodes.find(n => n.id === edge.target);
                                return `<li>
                                    ${source?.label || 'Unknown'} → <em>${edge.relation}</em> → ${target?.label || 'Unknown'}
                                </li>`;
                            }).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
        
        container.innerHTML = html;
    }

    async getStatistics() {
        const resultDiv = document.getElementById('statsResult');
        this.showLoading(resultDiv);

        try {
            console.log('Fetching statistics from:', `${this.apiBase}/statistics`);
            const response = await fetch(`${this.apiBase}/statistics`);
            console.log('Response received:', response);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Statistics data:', result);
            
            this.displayStatistics(resultDiv, result);
        } catch (error) {
            console.error('Statistics error:', error);
            this.showResult(resultDiv, `Statistics error: ${error.message}`, 'error');
        }
    }

    displayStatistics(container, stats) {
        const html = `
            <div class="stats-grid">
                <div class="stats-card">
                    <h4>Document Statistics</h4>
                    <p>Total Documents: ${stats.documents.total_count}</p>
                </div>
                
                <div class="stats-card">
                    <h4>Vector Store Statistics</h4>
                    <p>Total Documents: ${stats.vectors.total_documents}</p>
                    <p>Text Segments: ${stats.vectors.total_segments}</p>
                    <p>Vector Count: ${stats.vectors.vector_count}</p>
                    <p>Average Vector Dimension: ${stats.vectors.average_vector_dimension.toFixed(0)}</p>
                </div>
                
                <div class="stats-card">
                    <h4>Knowledge Graph Statistics</h4>
                    <p>Nodes: ${stats.knowledge_graph.total_nodes}</p>
                    <p>Edges: ${stats.knowledge_graph.total_edges}</p>
                    ${stats.knowledge_graph.node_types ? `
                        <p>Node Types:</p>
                        <ul>
                            ${Object.entries(stats.knowledge_graph.node_types).map(([type, count]) => 
                                `<li>${type}: ${count}</li>`
                            ).join('')}
                        </ul>
                    ` : ''}
                </div>
                
                <div class="stats-card">
                    <h4>System Information</h4>
                    <p>Data Directory: ${stats.system_info.data_directory}</p>
                    <p>Upload Directory: ${stats.system_info.upload_directory}</p>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    showResult(container, message, type = 'info') {
        container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    }

    showLoading(container) {
        container.innerHTML = '<p>Processing, please wait...<span class="loading"></span></p>';
    }
}

// Initialize application
const app = new AdminPortal();