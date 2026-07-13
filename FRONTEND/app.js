const API_BASE = 'http://localhost:8020';

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

function sendMessage(question) {
    if (isStreaming) return;
    if (!question.trim()) return;

    isStreaming = true;
    chatSend.disabled = true;
    chatInput.disabled = true;

    addMessage(question, 'user');
    chatInput.value = '';
    showTyping();

    var url = API_BASE + '/api/stream?q=' + encodeURIComponent(question);
    var eventSource = new EventSource(url);
    var botContent = '';

    eventSource.onmessage = function(event) {
        var data = JSON.parse(event.data);

        if (data.error) {
            botContent = 'Error: ' + data.error;
            eventSource.close();
            return;
        }

        if (data.token) {
            botContent += data.token;
            removeTyping();
            updateBotMessage(botContent);
        }

        if (data.done) {
            eventSource.close();
        }
    };

    eventSource.onerror = function() {
        eventSource.close();
        removeTyping();
        if (!botContent) {
            updateBotMessage('Error de conexion.');
        }
        isStreaming = false;
        chatSend.disabled = false;
        chatInput.disabled = false;
        chatInput.focus();
    };

    eventSource.addEventListener('done', function() {
        eventSource.close();
    });

    var checkDone = setInterval(function() {
        if (eventSource.readyState === EventSource.CLOSED) {
            clearInterval(checkDone);
            removeTyping();
            if (!botContent) {
                updateBotMessage('No se recibio respuesta.');
            }
            isStreaming = false;
            chatSend.disabled = false;
            chatInput.disabled = false;
            chatInput.focus();
        }
    }, 100);
}

chatSend.addEventListener('click', function() { sendMessage(chatInput.value); });
chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(chatInput.value);
    }
});

addMessage('Bienvenido al asistente. Hazme cualquier pregunta sobre el negocio.', 'bot');