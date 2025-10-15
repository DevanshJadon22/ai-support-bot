document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    let sessionId = null;

    // Function to start a new session
    async function startNewSession() {
        try {
            const response = await fetch('/session', { method: 'POST' });
            const data = await response.json();
            sessionId = data.session_id;
        } catch (error) {
            console.error('Error starting session:', error);
            addMessage('Error: Could not connect to the server.', 'bot-message');
        }
    }

    // Function to add a message to the chat box
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.innerHTML = `<p>${message}</p>`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
    }

    // Function to handle sending a message
    async function sendMessage() {
        const query = userInput.value.trim();
        if (query === '' || sessionId === null) return;

        addMessage(query, 'user-message');
        userInput.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    query: query,
                }),
            });
            const data = await response.json();
            addMessage(data.response, 'bot-message');
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot-message');
        }
    }

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Initialize the chat by starting a session
    startNewSession();
});