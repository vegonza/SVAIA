const chat = document.getElementById("chat-messages");
const inputText = document.getElementById("message-input");
let total = 0;
let loading = false;

function get_response(message) {
    return fetch('http://127.0.0.1:5000/completion', {
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


function create_message_IA(input) {
    const message = document.createElement('div');
    message.id = `message-${total}`;
    message.innerHTML = `
    <li class="d-flex align-items-start mb-3 container-fluid pe-0">
        <i class="bi bi-robot me-4"></i>
        <div class="bg-secondary text-white p-4 rounded-1 container-fluid">
            ${input}
        </div>
    </li>
    `;
    chat.appendChild(message);


}
function create_message_user(input) {
    const message = document.createElement('div');
    message.id = `message-${total}`;
    message.innerHTML = `
    <li class="d-flex align-items-start justify-content-end mb-3 ps-0">
        <div class="bg-primary text-white p-4 rounded-2 container-fluid">
                    ${input}
        </div>
        <i class="bi bi-person-fill ms-4"></i>
    </li>
    `;
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
    create_message_user(input);
    try {
        const response = await get_response(input);
        console.log(response);
        create_message_IA(response);
    } catch (error) {
        create_message_IA("Sorry, there was an error processing your request.");
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
    create_message_IA("Hola usuario");
});