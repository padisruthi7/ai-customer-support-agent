const messagesEl = document.getElementById('chat-messages');
const form = document.getElementById('chat-form');
const input = document.getElementById('message-input');
const clearBtn = document.getElementById('clear-btn');

const sessionId = 'browser-session';

function addMessage(role, text) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setLoading(visible) {
  const existing = document.querySelector('.loading');
  if (visible) {
    if (!existing) {
      const loading = document.createElement('div');
      loading.className = 'message assistant loading';
      loading.textContent = 'Thinking...';
      messagesEl.appendChild(loading);
    }
  } else if (existing) {
    existing.remove();
  }
}

async function sendMessage(message) {
  addMessage('user', message);
  setLoading(true);

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId })
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Something went wrong.');
    }

    addMessage('assistant', data.response);
  } catch (error) {
    addMessage('assistant', 'Sorry, I could not complete that request right now. Please try again.');
  } finally {
    setLoading(false);
    input.value = '';
    input.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  sendMessage(message);
});

clearBtn.addEventListener('click', async () => {
  messagesEl.innerHTML = '';
  await fetch('/api/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId })
  });
  addMessage('assistant', 'The conversation has been cleared. How can I help?');
});

addMessage('assistant', 'Hello! I can help with order status, refunds, returns, cancellation, and shipping questions.');
