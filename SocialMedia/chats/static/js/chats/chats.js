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
        msg.classList.add(data.author_id === currentUserId ? 'sent' : 'received');

        const p = document.createElement('p');
        p.innerText = data.message;
        msg.appendChild(p);

        const time = document.createElement('span');
        time.classList.add('message-time');
        const now = new Date();
        time.innerText = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
        msg.appendChild(time);

        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const messageForm = document.querySelector('#chat-input form');
    const messageInput = messageForm.querySelector('textarea');

    messageInput.focus();

    messageForm.onsubmit = function (e) {
        e.preventDefault();
        const message = messageInput.value.trim();

        if (message.length > 0) {
            chatSocket.send(JSON.stringify({ 'message': message }));
            messageInput.value = '';
        }
    };

    messageInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            messageForm.dispatchEvent(new Event("submit"));
        }
    });
});
