class CustomerPortal {
    constructor() {
        this.apiBase = '/api';
        this.currentConversationId = null;
        this.conversations = new Map();
        this.init();
    }

    init() {
        this.initTabs();
        this.initEventListeners();
        this.initChatFeatures();
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

        // File upload for compliance
        this.initFileUpload();
    }

    initFileUpload() {
        const fileInput = document.getElementById('complianceFileInput');
        const fileUploadBox = document.getElementById('fileUploadBox');
        let selectedFile = null;

        // Click to upload
        fileUploadBox.addEventListener('click', (e) => {
            if (!e.target.classList.contains('remove-file')) {
                fileInput.click();
            }
        });

        // File selection
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFileSelection(file);
            }
        });

        // Drag and drop
        fileUploadBox.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUploadBox.classList.add('dragover');
        });

        fileUploadBox.addEventListener('dragleave', () => {
            fileUploadBox.classList.remove('dragover');
        });

        fileUploadBox.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUploadBox.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) {
                this.handleFileSelection(file);
            }
        });
    }

    handleFileSelection(file) {
        const fileUploadBox = document.getElementById('fileUploadBox');
        const fileInfo = fileUploadBox.querySelector('.file-info');
        const uploadText = fileUploadBox.querySelector('.upload-text');
        
        // Store file reference
        this.selectedFile = file;
        
        // Update UI
        fileUploadBox.classList.add('has-file');
        uploadText.style.display = 'none';
        fileInfo.style.display = 'block';
        fileInfo.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        
        // Add remove button if not exists
        if (!fileUploadBox.querySelector('.remove-file')) {
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-file';
            removeBtn.innerHTML = '×';
            removeBtn.onclick = () => this.removeFile();
            fileUploadBox.appendChild(removeBtn);
        }
    }

    removeFile() {
        const fileUploadBox = document.getElementById('fileUploadBox');
        const fileInfo = fileUploadBox.querySelector('.file-info');
        const uploadText = fileUploadBox.querySelector('.upload-text');
        const fileInput = document.getElementById('complianceFileInput');
        
        // Clear file reference
        this.selectedFile = null;
        fileInput.value = '';
        
        // Reset UI
        fileUploadBox.classList.remove('has-file');
        uploadText.style.display = 'block';
        fileInfo.style.display = 'none';
        fileInfo.textContent = '';
        
        // Remove the remove button
        const removeBtn = fileUploadBox.querySelector('.remove-file');
        if (removeBtn) {
            removeBtn.remove();
        }
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

    startNewConversation() {
        const conversationId = 'conv_' + Date.now();
        const conversation = {
            id: conversationId,
            title: 'New Conversation',
            messages: [],
            createdAt: new Date()
        };
        
        this.conversations.set(conversationId, conversation);
        this.currentConversationId = conversationId;
        
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.innerHTML = `
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
        
        this.updateConversationList();
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
            const contextMode = document.getElementById('contextMode').checked;
            const context = contextMode ? this.getConversationContext() : '';
            
            const response = await fetch(`${this.apiBase}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: contextMode ? `${context}\n\nCurrent question: ${question}` : question,
                    top_k: 5
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Hide typing indicator
                this.hideTypingIndicator();
                
                // Add AI reply
                this.addAIMessage(result.answer, result.sources);
                
                // Save to conversation history
                this.saveToConversation(question, result.answer);
                
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
        const messagesDiv = document.getElementById('chatMessages');
        const messageHtml = `
            <div class="message user-message">
                <div class="message-content">
                    <div class="message-text">${this.escapeHtml(message)}</div>
                </div>
                <div class="user-avatar">👤</div>
            </div>
        `;
        messagesDiv.insertAdjacentHTML('beforeend', messageHtml);
        
        // Scroll to bottom immediately
        this.scrollToBottom();
    }

    addAIMessage(message, sources = []) {
        const messagesDiv = document.getElementById('chatMessages');
        let sourcesHtml = '';
        
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="message-sources">
                <h5>References:</h5>
                <ul>
                    ${sources.map(source => `
                        <li>
                        <strong>Similarity: ${(source.similarity_score * 100).toFixed(1)}%</strong><br>
                        ${this.escapeHtml(source.content)}
                        </li>
                    `).join('')}
                </ul>
                </div>
            `;
        }
        
        const messageHtml = `
            <div class="message ai-message">
                <div class="ai-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-header">
                    <span>AI Assistant</span>
                    <span class="message-time">${new Date().toLocaleTimeString()}</span>
                    </div>
                    <div class="message-text">${this.formatAIResponse(message)}</div>
                    ${sourcesHtml}
                </div>
            </div>
        `;
        
        messagesDiv.insertAdjacentHTML('beforeend', messageHtml);
        
        // Scroll after DOM update
        setTimeout(() => this.scrollToBottom(), 100);
    }

    addErrorMessage(message) {
        const messagesDiv = document.getElementById('chatMessages');
        const messageHtml = `
            <div class="message error-message">
                <div class="message-content">
                    <div class="message-text">❌ ${this.escapeHtml(message)}</div>
                </div>
            </div>
        `;
        messagesDiv.insertAdjacentHTML('beforeend', messageHtml);
        
        // Scroll after DOM update
        setTimeout(() => this.scrollToBottom(), 100);
    }

    showTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'none';
    }

    scrollToBottom() {
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    getConversationContext() {
        const conversation = this.conversations.get(this.currentConversationId);
        if (!conversation || conversation.messages.length === 0) {
            return '';
        }
        
        const recentMessages = conversation.messages.slice(-3); // Get last 3 rounds of conversation
        return recentMessages.map(msg => `User: ${msg.question}\nAI: ${msg.answer}`).join('\n\n');
    }

    saveToConversation(question, answer) {
        const conversation = this.conversations.get(this.currentConversationId);
        if (conversation) {
            conversation.messages.push({ question, answer, timestamp: new Date() });
        }
    }

    updateConversationTitle(firstQuestion) {
        const conversation = this.conversations.get(this.currentConversationId);
        if (conversation && conversation.title === 'New Conversation') {
            conversation.title = firstQuestion.substring(0, 30) + (firstQuestion.length > 30 ? '...' : '');
            this.updateConversationList();
        }
    }

    updateConversationList() {
        const listDiv = document.getElementById('conversationList');
        const conversations = Array.from(this.conversations.values()).reverse();
        
        listDiv.innerHTML = conversations.map(conv => `
            <div class="conversation-item ${conv.id === this.currentConversationId ? 'active' : ''}" 
                 data-id="${conv.id}">
                <div class="conversation-title">${conv.title}</div>
                <div class="conversation-meta">
                    ${conv.messages.length} messages • ${conv.createdAt.toLocaleDateString()}
                </div>
            </div>
        `).join('');
        
        listDiv.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', () => {
                this.loadConversation(item.dataset.id);
            });
        });
    }

    loadConversation(conversationId) {
        this.currentConversationId = conversationId;
        const conversation = this.conversations.get(conversationId);
        
        if (!conversation) return;
        
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.innerHTML = '';
        
        conversation.messages.forEach(msg => {
            this.addUserMessage(msg.question);
            this.addAIMessage(msg.answer);
        });
        
        this.updateConversationList();
    }

    clearCurrentChat() {
        if (confirm('Are you sure you want to clear the current conversation?')) {
            this.startNewConversation();
        }
    }

    exportCurrentChat() {
        const conversation = this.conversations.get(this.currentConversationId);
        if (!conversation || conversation.messages.length === 0) {
            alert('No messages to export');
            return;
        }
        
        const content = conversation.messages.map(msg => 
            `Q: ${msg.question}\nA: ${msg.answer}\n`
        ).join('\n---\n\n');
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation_${conversation.id}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    async analyzeCompliance() {
        const description = document.getElementById('businessDescription').value;
        const resultDiv = document.getElementById('complianceResult');
        const progressDiv = document.getElementById('complianceProgress');
        
        if (!description) {
            this.showResult(resultDiv, 'Please fill in the business description', 'error');
            return;
        }
        
        // Show progress
        progressDiv.style.display = 'block';
        this.showLoading(resultDiv);
        
        try {
            // Always use FormData for this endpoint
            const formData = new FormData();
            formData.append('description', description);
            
            // Add file if selected
            if (this.selectedFile) {
                formData.append('file', this.selectedFile);
            }
            
            const response = await fetch(`${this.apiBase}/compliance-analysis-with-doc`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.displayComplianceResult(resultDiv, result);
            } else {
                this.showResult(resultDiv, result.detail || 'Analysis failed', 'error');
            }
        } catch (error) {
            this.showResult(resultDiv, `Analysis error: ${error.message}`, 'error');
        } finally {
            progressDiv.style.display = 'none';
        }
    }

    displayComplianceResult(container, result) {
        const statusClass = result.compliance_status === 'Compliant' ? 'status-compliant' :
                          result.compliance_status === 'Violation' ? 'status-violation' : 'status-risk';
        
        const html = `
            <div class="compliance-report">
                <h3>Compliance Analysis Report</h3>
                <div class="compliance-status ${statusClass}">
                    Status: ${result.compliance_status}
                </div>
                <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
                
                ${result.violated_regulations && result.violated_regulations.length > 0 ? `
                    <div class="violations-section">
                        <h4>Violations:</h4>
                        <ul>
                            ${result.violated_regulations.map(v => `<li>${v}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${result.recommendations && result.recommendations.length > 0 ? `
                    <div class="recommendations-section">
                        <h4>Recommendations:</h4>
                        <ul>
                            ${result.recommendations.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${result.referenced_documents && result.referenced_documents.length > 0 ? `
                    <div class="references-section">
                        <h4>Reference Regulations:</h4>
                        <ul>
                            ${result.referenced_documents.map(d => `<li>${d}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatAIResponse(text) {
        return text.replace(/\n/g, '<br>');
    }
}

// Initialize application
const app = new CustomerPortal();