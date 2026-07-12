const API_BASE = 'http://localhost:8010';

let isStreaming = false;

const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');

function addMessage(content, role) {
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'message-content';

    if (role === 'bot') {
        bubble.innerHTML = content.replace(/\n/g, '<br>');
    } else {
        bubble.textContent = content;
    }

    div.appendChild(bubble);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
    const div = document.createElement('div');
    div.className = 'message bot';
    div.id = 'typing-indicator';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';

    div.appendChild(indicator);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}

function updateBotMessage(content) {
    let botDiv = document.querySelector('.message.bot:last-child');
    if (!botDiv || botDiv.id === 'typing-indicator') {
        const div = document.createElement('div');
        div.className = 'message bot';
        const bubble = document.createElement('div');
        bubble.className = 'message-content';
        div.appendChild(bubble);
        chatMessages.appendChild(div);
        botDiv = div;
    }
    const bubble = botDiv.querySelector('.message-content');
    bubble.innerHTML = content.replace(/\n/g, '<br>');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage(question) {
    if (isStreaming) return;
    if (!question.trim()) return;

    isStreaming = true;
    chatSend.disabled = true;
    chatInput.disabled = true;

    addMessage(question, 'user');
    chatInput.value = '';
    showTyping();

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botContent = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const text = decoder.decode(value);
            const lines = text.split('\n');

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                const data = JSON.parse(line.slice(6));

                if (data.error) {
                    botContent = `Error: ${data.error}`;
                    break;
                }

                if (data.token) {
                    botContent += data.token;
                    removeTyping();
                    updateBotMessage(botContent);
                }

                if (data.done) {
                    break;
                }
            }
        }

        removeTyping();
        if (!botContent) {
            updateBotMessage('No se recibio respuesta.');
        }

    } catch (error) {
        removeTyping();
        updateBotMessage(`Error de conexion: ${error.message}`);
    } finally {
        isStreaming = false;
        chatSend.disabled = false;
        chatInput.disabled = false;
        chatInput.focus();
    }
}

chatSend.addEventListener('click', () => sendMessage(chatInput.value));
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(chatInput.value);
    }
});

addMessage('Bienvenido al asistente. Hazme cualquier pregunta sobre el negocio.', 'bot');
