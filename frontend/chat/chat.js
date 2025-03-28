const chat = document.getElementById("chat-messages");
const inputText = document.getElementById("message-input");
const template_user = document.getElementById("user-message-template");
const template_ai = document.getElementById("ai-message-template");
let total = 0;
let loading = false;

function get_response(message) {
    return fetch("http://127.0.0.1:5000/completion", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    })
        .then(res => {
            if (!res.ok) {
                throw new Error('Error: ' + res.statusText);
            }
            return res.json();
        })
        .then(data => {
            return data.message;
        })
        .catch(error => {
            console.error('Error:', error);
            return "Sorry, there was an error processing your request.";
        });
}


function create_message(input, isUser = false) {
    const template = isUser ? template_user : template_ai;
    const clone = template.content.cloneNode(true);
    const messageDiv = clone.querySelector(".message-content");
    messageDiv.textContent = input;

    const message = document.createElement("div");
    message.id = `message-${total}`;
    message.appendChild(clone);
    chat.appendChild(message);
}

async function sendMessage() {
    if (loading) {
        return;
    }
    loading = true;
    const input = inputText.value.trim();
    if (!input) {
        return;
    }
    inputText.value = "";
    create_message(input, isUser = true);
    try {
        const response = await get_response(input);
        console.log(response);
        create_message(response);
    } catch (error) {
        create_message("Ha habido un error en el servidor");
    }
    inputText.focus();
    chat.scrollTop = chat.scrollHeight;
    total++;
    loading = false;
}

document.getElementById("send-message").addEventListener("click", sendMessage);

inputText.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

document.addEventListener("DOMContentLoaded", function () {
    create_message("Hola usuario");
});