document.addEventListener("DOMContentLoaded", function () {
    const chatPanel = document.getElementById('chat-panel');
    if (!chatPanel) return;

    const currentUserId = parseInt(chatPanel.dataset.userId);
    const chatId = chatPanel.dataset.chatId;
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";

    const chatSocket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/chat/${chatId}/`);

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const chatMessages = document.getElementById('chat-messages');

        const msg = document.createElement('div');
        msg.classList.add('message');

        if (data.author_id === currentUserId) {
            msg.classList.add('sent');
        } else {
            msg.classList.add('received');
        }

        const p = document.createElement('p');
        p.innerText = data.message;
        msg.appendChild(p);

        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const messageForm = document.querySelector('#chat-input form');
    messageForm.onsubmit = function (e) {
        e.preventDefault();
        const messageInput = this.querySelector('textarea');
        const message = messageInput.value.trim();

        if (message.length > 0) {
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInput.value = '';
        }
    };
});
