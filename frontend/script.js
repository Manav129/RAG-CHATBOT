// ============================================
// GOEL Electronics Customer Support - JavaScript
// ============================================
// Modern, clean implementation for the chat interface

// API base URL - dynamically set based on environment
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "" // Same origin for local development
    : "https://ai-support-backend-3z5o.onrender.com"; // Render backend URL

// ============================================
// SEND MESSAGE FUNCTION
// ============================================
async function sendMessage() {
    const inputElement = document.getElementById("user-input");
    const message = inputElement.value.trim();
    
    if (message === "") return;
    
    // Clear input and disable button
    inputElement.value = "";
    const sendBtn = document.getElementById("send-btn");
    sendBtn.disabled = true;
    
    // Add user message to chat
    addMessage(message, "user");
    
    // Show loading animation
    showLoading();
    
    try {
        const response = await fetch(API_URL + "/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: message })
        });
        
        if (!response.ok) {
            throw new Error("Server error: " + response.status);
        }
        
        const data = await response.json();
        
        // Remove loading and add bot response
        hideLoading();
        addBotMessage(data);
        
    } catch (error) {
        hideLoading();
        addMessage("Sorry, I'm having trouble connecting. Please try again.", "bot", true);
        console.error("Error:", error);
    }
    
    sendBtn.disabled = false;
    inputElement.focus();
}

// ============================================
// ADD MESSAGE TO CHAT
// ============================================
function addMessage(text, sender, isError = false) {
    const messagesDiv = document.getElementById("chat-messages");
    
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = sender === "user" ? "👤" : "🤖";
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content ${isError ? 'error' : ''}">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

// ============================================
// ADD BOT MESSAGE WITH CITATIONS & TICKET
// ============================================
function addBotMessage(data) {
    const messagesDiv = document.getElementById("chat-messages");
    
    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message";
    
    let content = `<p>${formatResponse(data.answer)}</p>`;
    
    // Add citations if available
    if (data.citations && data.citations.length > 0) {
        // Handle citations that might be objects or strings
        const citationTags = data.citations.map(c => {
            let citationText = "";
            if (typeof c === "string") {
                citationText = c;
            } else if (c && c.source) {
                citationText = c.source;
            } else if (c && c.name) {
                citationText = c.name;
            } else if (c && c.filename) {
                citationText = c.filename;
            } else {
                citationText = JSON.stringify(c);
            }
            return `<span class="citation-tag">${escapeHtml(citationText)}</span>`;
        }).join("");
        
        content += `
            <div class="citations">
                <div class="citations-title">📚 Sources:</div>
                ${citationTags}
            </div>
        `;
    }
    
    // Add ticket alert if created
    if (data.ticket_created && data.ticket_id) {
        content += `
            <div class="ticket-alert">
                <strong>🎫 Support Ticket Created</strong>
                Your concern has been escalated. Ticket ID: <code>${escapeHtml(data.ticket_id)}</code>
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">${content}</div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

// ============================================
// LOADING ANIMATION
// ============================================
function showLoading() {
    const messagesDiv = document.getElementById("chat-messages");
    
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "message bot-message loading";
    loadingDiv.id = "loading-indicator";
    
    loadingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    messagesDiv.appendChild(loadingDiv);
    scrollToBottom();
}

function hideLoading() {
    const loading = document.getElementById("loading-indicator");
    if (loading) loading.remove();
}

// ============================================
// TICKET LOOKUP
// ============================================
async function lookupTicket() {
    const ticketInput = document.getElementById("ticket-id-input");
    const ticketId = ticketInput.value.trim().toUpperCase();
    const resultDiv = document.getElementById("ticket-result");
    
    if (!ticketId) {
        showTicketError("Please enter a ticket ID");
        return;
    }
    
    resultDiv.innerHTML = `<div style="text-align: center; padding: 20px; color: #64748b;">Loading...</div>`;
    resultDiv.classList.add("show");
    
    try {
        const response = await fetch(API_URL + "/tickets/" + encodeURIComponent(ticketId));
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            if (response.status === 404) {
                showTicketError("Ticket not found. Please check the ID and try again.");
            } else {
                showTicketError(errorData.detail || "Error looking up ticket. Please try again.");
            }
            return;
        }
        
        const ticket = await response.json();
        showTicketDetails(ticket);
        
    } catch (error) {
        console.error("Ticket lookup error:", error);
        showTicketError("Connection error. Please make sure the server is running.");
    }
}

function showTicketDetails(ticket) {
    const resultDiv = document.getElementById("ticket-result");
    
    const statusClass = ticket.status.toLowerCase().replace(" ", "_");
    const priorityClass = ticket.priority.toLowerCase();
    const createdDate = new Date(ticket.created_at).toLocaleString();
    
    resultDiv.innerHTML = `
        <div class="ticket-card">
            <div class="ticket-card-header">
                <span class="ticket-id">🎫 ${escapeHtml(ticket.ticket_id)}</span>
                <span class="status-badge ${statusClass}">${escapeHtml(ticket.status)}</span>
            </div>
            <div class="ticket-details">
                <div class="ticket-row">
                    <span class="ticket-label">Priority:</span>
                    <span class="ticket-value">
                        <span class="priority-badge ${priorityClass}">${escapeHtml(ticket.priority)}</span>
                    </span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-label">Category:</span>
                    <span class="ticket-value">${escapeHtml(ticket.category || "General")}</span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-label">Created:</span>
                    <span class="ticket-value">${createdDate}</span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-label">Query:</span>
                    <span class="ticket-value">${escapeHtml(ticket.customer_query)}</span>
                </div>
            </div>
        </div>
    `;
    resultDiv.classList.add("show");
}

function showTicketError(message) {
    const resultDiv = document.getElementById("ticket-result");
    resultDiv.innerHTML = `
        <div class="ticket-error">
            ❌ ${escapeHtml(message)}
        </div>
    `;
    resultDiv.classList.add("show");
}

// ============================================
// QUICK ACTIONS
// ============================================
function askQuestion(question) {
    const inputElement = document.getElementById("user-input");
    inputElement.value = question;
    sendMessage();
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function handleTicketKeyPress(event) {
    if (event.key === "Enter") {
        lookupTicket();
    }
}

function scrollToBottom() {
    const messagesDiv = document.getElementById("chat-messages");
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function formatResponse(text) {
    if (!text) return "";
    // Convert line breaks to <br> and escape HTML
    return escapeHtml(text).replace(/\n/g, "<br>");
}

// ============================================
// INITIALIZE
// ============================================
document.addEventListener("DOMContentLoaded", function() {
    // Focus on input when page loads
    document.getElementById("user-input").focus();
});
