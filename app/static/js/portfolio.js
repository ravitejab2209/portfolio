class PortfolioChatbot {
    constructor() {
        console.log('Initializing PortfolioChatbot...');
        
        // Get DOM elements with debugging
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.floatingBtn = document.getElementById('floatingChatBtn');
        this.chatModal = document.getElementById('chatModal');
        this.closeBtn = document.getElementById('chatCloseBtn');
        
        console.log('DOM Elements found:');
        console.log('- chatMessages:', this.chatMessages);
        console.log('- chatInput:', this.chatInput);
        console.log('- sendBtn:', this.sendBtn);
        console.log('- floatingBtn:', this.floatingBtn);
        console.log('- chatModal:', this.chatModal);
        console.log('- closeBtn:', this.closeBtn);
        
        if (!this.floatingBtn) {
            console.error('CRITICAL: Floating button not found! Check if ID "floatingChatBtn" exists in HTML');
        }
        
        if (!this.chatModal) {
            console.error('CRITICAL: Chat modal not found! Check if ID "chatModal" exists in HTML');
        }
        
        this.setupEventListeners();
        console.log('PortfolioChatbot initialization complete');
    }
    
    setupEventListeners() {
        console.log('Setting up event listeners...');
        console.log('Floating button:', this.floatingBtn);
        console.log('Chat modal:', this.chatModal);
        console.log('Close button:', this.closeBtn);
        
        if (!this.floatingBtn) {
            console.error('Floating button not found!');
            return;
        }
        
        // Floating button click - multiple event types for better compatibility
        this.floatingBtn.addEventListener('click', (e) => {
            console.log('Floating button clicked!');
            e.preventDefault();
            e.stopPropagation();
            this.openModal();
        });
        
        this.floatingBtn.addEventListener('touchstart', (e) => {
            console.log('Floating button touched!');
            e.preventDefault();
            e.stopPropagation();
            this.openModal();
        });
        
        // Add mousedown for immediate response
        this.floatingBtn.addEventListener('mousedown', (e) => {
            console.log('Floating button mouse down!');
            e.preventDefault();
            e.stopPropagation();
            this.openModal();
        });
        
        // Close button click
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', (e) => {
                console.log('Close button clicked!');
                e.preventDefault();
                e.stopPropagation();
                this.closeModal();
            });
        }
        
        // Click outside to close - only if clicking outside the chat panel
        document.addEventListener('click', (e) => {
            if (this.chatModal && this.chatModal.classList.contains('active')) {
                if (!this.chatModal.contains(e.target) && !this.floatingBtn.contains(e.target)) {
                    console.log('Closing chat panel from outside click');
                    this.closeModal();
                }
            }
        });
        
        // Send message
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', (e) => {
                console.log('Send button clicked!');
                e.preventDefault();
                this.sendMessage();
            });
        }
        
        if (this.chatInput) {
            this.chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    console.log('Enter key pressed in chat input');
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.chatModal && this.chatModal.classList.contains('active')) {
                console.log('Escape key pressed, closing modal');
                this.closeModal();
            }
        });
        
        console.log('Event listeners setup complete');
    }
    
    openModal() {
        console.log('Opening modal...');
        console.log('Chat modal element:', this.chatModal);
        
        if (!this.chatModal) {
            console.error('Chat modal element not found!');
            return;
        }
        
        try {
            this.chatModal.classList.add('active');
            console.log('Chat panel classes after opening:', this.chatModal.classList.toString());
            
            // Show welcome message if no messages yet
            if (this.chatMessages && this.chatMessages.children.length === 0) {
                console.log('Showing welcome message...');
                this.showWelcomeMessage();
            }
            
            // Focus input
            setTimeout(() => {
                if (this.chatInput) {
                    console.log('Focusing chat input...');
                    this.chatInput.focus();
                }
            }, 300);
            
            console.log('Modal opened successfully');
        } catch (error) {
            console.error('Error opening modal:', error);
        }
    }
    
    closeModal() {
        console.log('Closing modal...');
        
        if (!this.chatModal) {
            console.error('Chat modal element not found!');
            return;
        }
        
        try {
            this.chatModal.classList.remove('active');
            console.log('Chat panel closed successfully');
        } catch (error) {
            console.error('Error closing modal:', error);
        }
    }
    
    showWelcomeMessage() {
        const welcomeMessage = {
            type: 'ai',
            content: '👋 Hello! I\'m Raviteja\'s AI assistant. I can help you learn about his work experience, technical skills, projects, and education. What would you like to know? 🚀'
        };
        
        this.displayMessage(welcomeMessage);
    }
    
                async sendMessage() {
                const message = this.chatInput.value.trim();
                if (!message) return;
                
                this.displayMessage({
                    type: 'user',
                    content: message
                });
                
                this.chatInput.value = '';
                this.showTypingIndicator();
                
                try {
                    const response = await fetch('/api/chat-stream', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message
                        })
                    });
                    
                    this.hideTypingIndicator();
                    
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    
                    // Create streaming message container
                    const streamingMessageDiv = this.createStreamingMessage();
                    
                    // Read the streaming response
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let accumulatedText = '';
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        
                        if (done) break;
                        
                        const chunk = decoder.decode(value, { stream: true });
                        const lines = chunk.split('\n');
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                const data = line.slice(6);
                                if (data === '[DONE]') {
                                    break;
                                }
                                
                                try {
                                    const jsonData = JSON.parse(data);
                                    if (jsonData.chunk) {
                                        accumulatedText += jsonData.chunk;
                                        this.updateStreamingMessage(streamingMessageDiv, accumulatedText);
                                    }
                                } catch (e) {
                                    // Skip invalid JSON
                                }
                            }
                        }
                    }
                    
                    // Finalize the streaming message
                    this.finalizeStreamingMessage(streamingMessageDiv);
                    
                } catch (error) {
                    console.error('Error:', error);
                    this.hideTypingIndicator();
                    
                    this.displayMessage({
                        type: 'ai',
                        content: 'Sorry, I encountered an error. Please try asking your question again.'
                    });
                }
            }
    
    displayMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message ' + message.type + '-message';
        
        const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = '<div class="message-header">' + (message.type === 'user' ? 'You' : 'AI Assistant') + ' • ' + timestamp + '</div><div class="message-bubble">' + this.formatMessage(message.content) + '</div>';
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        console.log('Formatting message:', content);
        try {
            // Safe string replacements without regex
            let formatted = content;
            
            // Replace **text** with <strong>text</strong>
            while (formatted.includes('**')) {
                const start = formatted.indexOf('**');
                const end = formatted.indexOf('**', start + 2);
                if (end !== -1) {
                    const before = formatted.substring(0, start);
                    const text = formatted.substring(start + 2, end);
                    const after = formatted.substring(end + 2);
                    formatted = before + '<strong>' + text + '</strong>' + after;
                } else {
                    break;
                }
            }
            
            // Replace *text* with <em>text</em>
            while (formatted.includes('*')) {
                const start = formatted.indexOf('*');
                const end = formatted.indexOf('*', start + 1);
                if (end !== -1) {
                    const before = formatted.substring(0, start);
                    const text = formatted.substring(start + 1, end);
                    const after = formatted.substring(end + 1);
                    formatted = before + '<em>' + text + '</em>' + after;
                } else {
                    break;
                }
            }
            
            // Replace newlines with <br>
            formatted = formatted.split('\n').join('<br>');
            
            console.log('Formatted message:', formatted);
            return formatted;
        } catch (error) {
            console.error('Error formatting message:', error);
            return content;
        }
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message ai-message';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = '<div class="typing-indicator"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div>';
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
                createStreamingMessage() {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'chat-message ai-message streaming';
                
                const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                
                messageDiv.innerHTML = `
                    <div class="message-header">AI Assistant • ${timestamp}</div>
                    <div class="message-bubble">
                        <span class="streaming-content"></span>
                        <span class="streaming-cursor">|</span>
                    </div>
                `;
                
                this.chatMessages.appendChild(messageDiv);
                this.scrollToBottom();
                
                return messageDiv;
            }
            
            updateStreamingMessage(messageDiv, content) {
                const contentSpan = messageDiv.querySelector('.streaming-content');
                if (contentSpan) {
                    contentSpan.innerHTML = this.formatMessage(content);
                    this.scrollToBottom();
                }
            }
            
            finalizeStreamingMessage(messageDiv) {
                // Remove streaming cursor and class
                const cursor = messageDiv.querySelector('.streaming-cursor');
                if (cursor) {
                    cursor.remove();
                }
                messageDiv.classList.remove('streaming');
            }
            
            scrollToBottom() {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }
}

// Debug function to test button visibility and position
function debugChatButton() {
    const btn = document.getElementById('floatingChatBtn');
    if (btn) {
        const rect = btn.getBoundingClientRect();
        const styles = window.getComputedStyle(btn);
        console.log('🔍 Button debug info:');
        console.log('- Position:', rect);
        console.log('- Z-index:', styles.zIndex);
        console.log('- Pointer events:', styles.pointerEvents);
        console.log('- Display:', styles.display);
        console.log('- Visibility:', styles.visibility);
        console.log('- Cursor:', styles.cursor);
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM Content Loaded - Initializing chatbot...');
    
    // Test if elements exist before creating chatbot
    const floatingBtn = document.getElementById('floatingChatBtn');
    const chatModal = document.getElementById('chatModal');
    
    console.log('🔍 Pre-init check:');
    console.log('- Floating button exists:', !!floatingBtn);
    console.log('- Chat modal exists:', !!chatModal);
    
    if (!floatingBtn) {
        console.error('❌ FATAL: Floating button not found in DOM!');
        return;
    }
    
    if (!chatModal) {
        console.error('❌ FATAL: Chat modal not found in DOM!');
        return;
    }
    
    // Debug button after a short delay
    setTimeout(debugChatButton, 1000);
    
    // Create chatbot instance
    try {
        const chatbot = new PortfolioChatbot();
        console.log('✅ Chatbot created successfully:', chatbot);
        
        // Add a BACKUP click handler that ALWAYS works
        floatingBtn.addEventListener('click', function(e) {
            console.log('🔄 BACKUP: Direct click handler triggered');
            console.log('Event:', e);
            console.log('Target:', e.target);
            console.log('Current target:', e.currentTarget);
            
            // Force open chat panel as backup
            if (chatModal) {
                chatModal.classList.add('active');
                console.log('✅ BACKUP: Chat panel opened directly');
            }
        });
        
        // Ready for user interaction
        console.log('✅ Chatbot ready for user interaction');
        
    } catch (error) {
        console.error('❌ Error creating chatbot:', error);
    }
}); 