// human bird's interface
const socket = io();

const connDot = document.getElementById('bird-conn-dot');
const connText = document.getElementById('bird-conn-text');
const birdLog = document.getElementById('bird-log');
const answerInput = document.getElementById('bird-answer');
const sendBtn = document.getElementById('bird-send-btn');

let currentRound = 0;

socket.on('connect', () => {
  socket.emit('bird_join', { room_code: ROOM_CODE });
});

socket.on('connected', (data) => {
  connDot.className = 'status-dot dot-online';
  connText.textContent = 'connected — stay in character';
  answerInput.disabled = false;
  sendBtn.disabled = false;
  clearEmpty();
  appendSystem(data.message);
});

socket.on('question_received', (data) => {
  currentRound = data.round;
  appendQuestion(data.question, data.round);
  answerInput.disabled = false;
  answerInput.focus();
  sendBtn.disabled = false;
});

socket.on('error', (data) => {
  connText.textContent = data.message;
});

sendBtn.addEventListener('click', sendReply);
answerInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendReply();
  }
});

function sendReply() {
  const reply = answerInput.value.trim();
  if (!reply) return;
  socket.emit('bird_reply', { room_code: ROOM_CODE, reply, round: currentRound });
  appendSent(reply);
  answerInput.value = '';
  answerInput.disabled = true;
  sendBtn.disabled = true;
}

function appendQuestion(text, round) {
  const div = document.createElement('div');
  div.className = 'bird-msg bird-question';
  div.innerHTML = `<span class="round-label">round ${round}</span>${text}`;
  birdLog.appendChild(div);
  birdLog.scrollTop = birdLog.scrollHeight;
}

function appendSent(text) {
  const div = document.createElement('div');
  div.className = 'bird-msg bird-sent';
  div.textContent = text;
  birdLog.appendChild(div);
  birdLog.scrollTop = birdLog.scrollHeight;
}

function appendSystem(text) {
  const div = document.createElement('div');
  div.className = 'bird-msg bird-system';
  div.textContent = text;
  birdLog.appendChild(div);
  birdLog.scrollTop = birdLog.scrollHeight;
}

function clearEmpty() {
  const empty = birdLog.querySelector('.bird-log-empty');
  if (empty) empty.remove();
}
