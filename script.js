class LegalComplianceSystem {
    constructor() {
        this.apiBase = '/api';
        this.currentConversationId = null;
        this.conversations = new Map();
        this.isUploading = false;
        this.init();
    }

    init() {
        this.initTabs();
        this.initEventListeners();
        this.initUploadFeatures();
        this.initChatFeatures();
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

        // Chat related
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('questionInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        document.getElementById('newConversation').addEventListener('click', () => {
            this.startNewConversation();
        });

        document.getElementById('clearChat').addEventListener('click', () => {
            this.clearCurrentChat();
        });

        document.getElementById('exportChat').addEventListener('click', () => {
            this.exportCurrentChat();
        });

        // Quick questions
        document.querySelectorAll('.quick-question-item').forEach(item => {
            item.addEventListener('click', () => {
                const question = item.dataset.question;
                document.getElementById('questionInput').value = question;
                this.sendMessage();
            });
        });

        // Compliance analysis
        document.getElementById('analyzeCompliance').addEventListener('click', () => {
            this.analyzeCompliance();
        });

        // Other features
        document.getElementById('buildKG').addEventListener('click', () => {
            this.buildKnowledgeGraph();
        });

        document.getElementById('queryKG').addEventListener('click', () => {
            this.queryKnowledgeGraph();
        });

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

    initChatFeatures() {
        // Start new conversation
        this.startNewConversation();
        
        // Auto-adjust input box height
        const textarea = document.getElementById('questionInput');
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
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

    showUploadResult(message, type) {
        const resultDiv = document.getElementById('uploadResult');
        resultDiv.innerHTML = `<div class="upload-message ${type}">${message}</div>`;
        
        setTimeout(() => {
            resultDiv.innerHTML = '';
        }, 5000);
    }

    async updateStats() {
        try {
            const response = await fetch(`${this.apiBase}/statistics`);
            const stats = await response.json();
            
            document.getElementById('totalDocs').textContent = stats.documents.total_count;
            document.getElementById('todayUploads').textContent = '0'; // Can be fetched from backend
            document.getElementById('processingStatus').textContent = 'Ready';
        } catch (error) {
            console.error('Failed to update statistics:', error);
        }
    }

    async searchDocuments() {
        const searchInput = document.getElementById('docSearch');
        const query = searchInput.value.trim();
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
                return;
            }
            
            // Display search results
            listDiv.innerHTML = `
                <div class="search-results-header">
                    <div>
                        <h4>🔍 Search Results</h4>
                        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">
                            Keyword "<strong>${query}</strong>" - Found ${result.total_found} relevant passages
                        </p>
                    </div>
                    <button class="btn btn-clear-search" onclick="document.getElementById('docSearch').value=''; app.loadDocuments();">
                        ✕ Clear Search
                    </button>
                </div>
                ${result.results.map((item, index) => `
                    <div class="search-result-card">
                        <div class="result-header">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span class="result-number">Result ${index + 1}</span>
                                <span style="color: #666; font-size: 14px;">
                                    ${item.document_name || 'Related Document'}
                                </span>
                            </div>
                            <span class="similarity-score">
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
            `;
        } catch (error) {
            listDiv.innerHTML = `<div class="error-message">Search failed: ${error.message}</div>`;
        }
    }
    
    highlightKeywords(text, keyword) {
        // Highlight keywords
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
                return;
            }

            listDiv.innerHTML = documents.map(doc => `
                <div class="document-card">
                    <div class="document-header">
                        <h4>${doc.filename}</h4>
                        <div class="document-actions">
                            <button class="action-btn" onclick="app.viewDocument('${doc.id}')" title="View">👁️</button>
                            <button class="action-btn" onclick="app.deleteDocument('${doc.id}')" title="Delete">🗑️</button>
                        </div>
                    </div>
                    <div class="document-meta">
                        <span class="meta-item">📅 ${new Date(doc.upload_time).toLocaleDateString()}</span>
                        <span class="meta-item">📄 ${doc.file_type.toUpperCase()}</span>
                        <span class="meta-item status-${doc.status}">⚡ ${doc.status}</span>
                    </div>
                    <div class="document-stats">
                        <span>Words: ${doc.metadata?.word_count || 'N/A'}</span>
                        <span>Paragraphs: ${doc.metadata?.paragraph_count || 'N/A'}</span>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            listDiv.innerHTML = `<div class="error-message">Failed to load document list: ${error.message}</div>`;
        }
    }

    startNewConversation() {
        this.currentConversationId = Date.now().toString();
        this.conversations.set(this.currentConversationId, {
            id: this.currentConversationId,
            messages: [],
            title: 'New Conversation',
            createdAt: new Date()
        });
        
        this.clearChatMessages();
        this.showWelcomeMessage();
        this.updateConversationList();
    }

    clearChatMessages() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.innerHTML = '';
    }

    showWelcomeMessage() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="ai-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-text">
                        Hello! I'm your legal Q&A assistant. I can help you with:
                        <ul>
                            <li>Answer legal and regulatory questions</li>
                            <li>Analyze specific clause meanings</li>
                            <li>Provide compliance suggestions</li>
                            <li>Find relevant legal basis</li>
                        </ul>
                        Feel free to ask me anything!
                    </div>
                </div>
            </div>
        `;
    }

    async sendMessage() {
        const input = document.getElementById('questionInput');
        const question = input.value.trim();
        
        if (!question) return;

        // Add user message to interface
        this.addUserMessage(question);
        
        // Clear input box
        input.value = '';
        input.style.height = 'auto';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Get context
            const context = this.getConversationContext();
            const contextMode = document.getElementById('contextMode').checked;
            const detailedMode = document.getElementById('detailedMode').checked;

            const response = await fetch(`${this.apiBase}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: contextMode ? `${context}\n\nCurrent question: ${question}` : question,
                    top_k: detailedMode ? 8 : 5
                })
            });

            const result = await response.json();

            if (response.ok) {
                // Hide typing indicator
                this.hideTypingIndicator();
                
                // Add AI reply
                this.addAIMessage(result);
                
                // Save to conversation history
                this.saveMessageToConversation(question, result);
                
                // Update conversation title
                this.updateConversationTitle(question);
            } else {
                throw new Error(result.detail || 'Q&A failed');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addErrorMessage(`Sorry, an error occurred: ${error.message}`);
        }
    }

    addUserMessage(message) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'user-message';
        messageDiv.innerHTML = `
            <div class="user-avatar">👤</div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(message)}</div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom immediately
        requestAnimationFrame(() => {
            this.scrollToBottom();
        });
    }

    addAIMessage(result) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'ai-message';
        
        const confidenceBadge = `<span class="confidence-badge">${(result.confidence * 100).toFixed(1)}%</span>`;
        
        const sourcesHtml = result.sources && result.sources.length > 0 ? `
            <div class="message-sources">
                <h5>References:</h5>
                ${result.sources.map(source => `
                    <div class="source-item">
                        <strong>Similarity: ${(source.similarity_score * 100).toFixed(1)}%</strong><br>
                        ${source.content}
                    </div>
                `).join('')}
            </div>
        ` : '';

        messageDiv.innerHTML = `
            <div class="ai-avatar">🤖</div>
            <div class="message-content">
                <div class="message-header">
                    <span>AI Assistant</span>
                    ${confidenceBadge}
                </div>
                <div class="message-text">${this.formatMessage(result.answer)}</div>
                ${sourcesHtml}
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        
        // Scroll after DOM update
        requestAnimationFrame(() => {
            this.scrollToBottom();
        });
    }

    addErrorMessage(message) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'ai-message error';
        messageDiv.innerHTML = `
            <div class="ai-avatar">⚠️</div>
            <div class="message-content">
                <div class="message-text">${message}</div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        
        // Scroll after DOM update
        requestAnimationFrame(() => {
            this.scrollToBottom();
        });
    }

    formatMessage(text) {
        return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    showTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'flex';
        requestAnimationFrame(() => {
            this.scrollToBottom();
        });
    }

    hideTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'none';
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    getConversationContext() {
        const conversation = this.conversations.get(this.currentConversationId);
        if (!conversation || conversation.messages.length === 0) return '';
        
        const recentMessages = conversation.messages.slice(-3); // Get last 3 rounds of conversation
        return recentMessages.map(msg => `User: ${msg.question}\nAI: ${msg.answer}`).join('\n\n');
    }

    saveMessageToConversation(question, result) {
        const conversation = this.conversations.get(this.currentConversationId);
        conversation.messages.push({
            question,
            answer: result.answer,
            confidence: result.confidence,
            sources: result.sources,
            timestamp: new Date()
        });
    }

    updateConversationTitle(question) {
        const conversation = this.conversations.get(this.currentConversationId);
        if (conversation.messages.length === 1) {
            conversation.title = question.length > 20 ? question.substring(0, 20) + '...' : question;
            this.updateConversationList();
        }
    }

    updateConversationList() {
        const listContainer = document.getElementById('conversationList');
        const conversations = Array.from(this.conversations.values()).reverse();
        const showDeleteBtn = conversations.length > 1;  // Only show delete button when multiple conversations
        
        listContainer.innerHTML = conversations.map(conv => `
            <div class="conversation-item ${conv.id === this.currentConversationId ? 'active' : ''}">
                <div class="conversation-content" onclick="app.switchConversation('${conv.id}')">
                    <div class="conversation-title">${conv.title}</div>
                    <div class="conversation-meta">
                        ${conv.messages.length} messages • ${conv.createdAt.toLocaleDateString()}
                    </div>
                </div>
                ${showDeleteBtn ? `
                    <button class="conversation-delete-btn" 
                            onclick="event.stopPropagation(); app.deleteConversation('${conv.id}')"
                            title="Delete Conversation">
                        🗑️
                    </button>
                ` : ''}
            </div>
        `).join('');
    }

    deleteConversation(conversationId) {
        // Confirm deletion
        if (!confirm('Are you sure you want to delete this conversation?')) {
            return;
        }
        
        // Delete conversation
        this.conversations.delete(conversationId);
        
        // If deleting current conversation, switch to another
        if (conversationId === this.currentConversationId) {
            const remaining = Array.from(this.conversations.keys());
            if (remaining.length > 0) {
                this.switchConversation(remaining[0]);
            } else {
                // If no conversations left, create a new one
                this.startNewConversation();
            }
        } else {
            this.updateConversationList();
        }
    }

    switchConversation(conversationId) {
        this.currentConversationId = conversationId;
        this.loadConversationMessages(conversationId);
        this.updateConversationList();
    }

    loadConversationMessages(conversationId) {
        const conversation = this.conversations.get(conversationId);
        this.clearChatMessages();
        
        if (conversation.messages.length === 0) {
            this.showWelcomeMessage();
            return;
        }

        conversation.messages.forEach(msg => {
            this.addUserMessage(msg.question);
            this.addAIMessage({
                answer: msg.answer,
                confidence: msg.confidence,
                sources: msg.sources
            });
        });
    }

    clearCurrentChat() {
        if (confirm('Are you sure you want to clear the current conversation?')) {
            const conversation = this.conversations.get(this.currentConversationId);
            conversation.messages = [];
            this.clearChatMessages();
            this.showWelcomeMessage();
        }
    }

    exportCurrentChat() {
        const conversation = this.conversations.get(this.currentConversationId);
        const chatData = {
            title: conversation.title,
            createdAt: conversation.createdAt,
            messages: conversation.messages
        };
        
        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_${conversation.title}_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document?')) return;

        try {
            const response = await fetch(`${this.apiBase}/document/${docId}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            
            if (result.success) {
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

    // Other methods remain unchanged...
    async analyzeCompliance() {
        const businessType = document.getElementById('businessType').value.trim();
        const description = document.getElementById('businessDescription').value.trim();
        const resultDiv = document.getElementById('complianceResult');

        if (!description) {
            this.showResult(resultDiv, 'Please fill in the business description', 'error');
            return;
        }

        const businessData = {
            business_type: businessType || 'Not specified',
            description: description
        };

        this.showLoading(resultDiv);

        try {
            const response = await fetch(`${this.apiBase}/compliance-analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: description,
                    business_data: businessData
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.displayComplianceResult(resultDiv, result);
            } else {
                this.showResult(resultDiv, result.detail || 'Analysis failed', 'error');
            }
        } catch (error) {
            this.showResult(resultDiv, `Analysis error: ${error.message}`, 'error');
        }
    }

    displayComplianceResult(container, result) {
        const statusClass = result.compliance_status === 'Compliant' ? 'status-compliant' :
                          result.compliance_status === 'Violation' ? 'status-violation' : 'status-risk';

        const html = `
            <div class="compliance-result">
                <div class="compliance-status ${statusClass}">
                    ${result.compliance_status}
                </div>
                <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
                
                ${result.violated_regulations && result.violated_regulations.length > 0 ? `
                    <div class="violations">
                        <h4>Violations:</h4>
                        <ul>
                            ${result.violated_regulations.map(violation => `<li>${violation}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${result.recommendations && result.recommendations.length > 0 ? `
                    <div class="recommendations">
                        <h4>Recommendations:</h4>
                        <ul>
                            ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${result.referenced_documents && result.referenced_documents.length > 0 ? `
                    <div class="references">
                        <h4>Reference Regulations:</h4>
                        <ul>
                            ${result.referenced_documents.map(ref => `<li>${ref}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
        
        container.innerHTML = html;
        container.className = 'result-section success';
    }

    async buildKnowledgeGraph() {
        const resultDiv = document.getElementById('kgResult');
        this.showLoading(resultDiv);

        try {
            const response = await fetch(`${this.apiBase}/build-knowledge-graph`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showResult(resultDiv, `Knowledge graph built successfully!\nNodes: ${result.statistics.nodes}\nEdges: ${result.statistics.edges}\nDocuments processed: ${result.statistics.documents_processed}`, 'success');
            } else {
                this.showResult(resultDiv, result.detail || 'Build failed', 'error');
            }
        } catch (error) {
            this.showResult(resultDiv, `Build error: ${error.message}`, 'error');
        }
    }

    async queryKnowledgeGraph() {
        const entityName = document.getElementById('entityQuery').value.trim();
        const resultDiv = document.getElementById('kgResult');

        if (!entityName) {
            this.showResult(resultDiv, 'Please enter entity name', 'error');
            return;
        }

        this.showLoading(resultDiv);

        try {
            const response = await fetch(`${this.apiBase}/knowledge-graph/query?entity_name=${encodeURIComponent(entityName)}`);
            const result = await response.json();

            if (response.ok) {
                this.displayKGResult(resultDiv, result);
            } else {
                this.showResult(resultDiv, 'Query failed', 'error');
            }
        } catch (error) {
            this.showResult(resultDiv, `Query error: ${error.message}`, 'error');
        }
    }

    displayKGResult(container, result) {
        if (!result.nodes || result.nodes.length === 0) {
            this.showResult(container, 'No related entities found', 'warning');
            return;
        }

        const html = `
            <div class="kg-result">
                <h4>Query Results (Found ${result.nodes.length} nodes, ${result.edges.length} relationships)</h4>
                
                <div class="kg-nodes">
                    <h5>Related Entities:</h5>
                    ${result.nodes.map(node => `
                        <div class="node-item">
                            <strong>${node.label}</strong> (${node.type})
                        </div>
                    `).join('')}
                </div>
                
                ${result.edges.length > 0 ? `
                    <div class="kg-edges">
                        <h5>Entity Relationships:</h5>
                        ${result.edges.map(edge => {
                            const source = result.nodes.find(n => n.id === edge.source);
                            const target = result.nodes.find(n => n.id === edge.target);
                            return `
                                <div class="edge-item">
                                    ${source?.label || 'Unknown'} → <em>${edge.relation}</em> → ${target?.label || 'Unknown'}
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        container.innerHTML = html;
        container.className = 'result-section success';
    }

    async getStatistics() {
        const resultDiv = document.getElementById('statsResult');
        this.showLoading(resultDiv);

        try {
            const response = await fetch(`${this.apiBase}/statistics`);
            const result = await response.json();

            if (response.ok) {
                this.displayStatistics(resultDiv, result);
            } else {
                this.showResult(resultDiv, 'Failed to get statistics', 'error');
            }
        } catch (error) {
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
        container.className = 'result-section success';
    }

    showResult(container, message, type = 'info') {
        container.innerHTML = `<p>${message.replace(/\n/g, '<br>')}</p>`;
        container.className = `result-section ${type}`;
    }

    showLoading(container) {
        container.innerHTML = '<p>Processing, please wait...<span class="loading"></span></p>';
        container.className = 'result-section';
    }
}

// Initialize application
const app = new LegalComplianceSystem();