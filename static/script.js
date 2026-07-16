// 전역 변수
let socket;
let currentRoom = null;
let currentUsername = null;
let sourceLanguage = 'ko';
let targetLanguage = 'en';
let lastTranslatedText = '';
let recognition = null;
let permissionRequestPromise = null; // to prevent multiple simultaneous permission prompts

const LANGUAGE_LABELS = {
    ko: '한국어',
    en: '영어',
    ja: '일본어',
    tl: '필리핀어',
    id: '인도네시아어',
    vi: '베트남어'
};

const LANGUAGE_CODES = {
    한국어: 'ko',
    영어: 'en',
    일본어: 'ja',
    필리핀어: 'tl',
    인도네시아어: 'id',
    베트남어: 'vi'
};

// DOM 요소들
const mainView = document.getElementById('mainView');
const chatView = document.getElementById('chatView');
const newRoomBtn = document.getElementById('newRoomBtn');
const backBtn = document.getElementById('backBtn');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const messagesContainer = document.getElementById('messagesContainer');
const roomsList = document.getElementById('roomsList');
// header username element (compact header)
const chatUsernameEl = document.getElementById('chatUsername');
const newRoomModal = document.getElementById('newRoomModal');
const usernameModal = document.getElementById('usernameModal');
const roomNameInput = document.getElementById('roomNameInput');
const cancelBtn = document.getElementById('cancelBtn');
const createBtn = document.getElementById('createBtn');
const usernameInput = document.getElementById('usernameInput');
const usernameConfirmBtn = document.getElementById('usernameConfirmBtn');
const usernameModalTitle = document.getElementById('usernameModalTitle');
const languageSelect = document.getElementById('languageSelect');
const mainLanguageSelect = document.getElementById('mainLanguageSelect');
const detectBtn = document.getElementById('detectBtn');
let detectMode = false;
const voiceBtn = document.getElementById('voiceBtn');
const ttsBtn = document.getElementById('ttsBtn');
const typingIndicator = document.getElementById('typingIndicator');
const userBadge = document.getElementById('userBadge');
const userBadgeName = document.getElementById('userBadgeName');
const changeNameBtn = document.getElementById('changeNameBtn');
// mic hint element removed

// 소켓 초기화
function initSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
        if (currentUsername) {
            loadRooms();
            // 재연결 시 현재 채팅방 자동 재입장
            if (currentRoom) {
                socket.emit('join_room', {
                    room_id: currentRoom.room_id,
                    username: currentUsername,
                    my_language: sourceLanguage
                });
            }
        } else {
            showUsernameModal();
        }
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });

    socket.on('new_message', (data) => {
        displayMessage(data, false);
    });

    socket.on('user_joined', (data) => {
        displaySystemMessage(`${data.username}님이 입장했습니다.`);
    });

    socket.on('user_left', (data) => {
        displaySystemMessage(`${data.username}님이 퇴장했습니다.`);
    });

    socket.on('user_typing', (data) => {
        showTypingIndicator();
    });

    socket.on('error', (data) => {
        alert(`오류: ${data.message}`);
    });
}

// UI 이벤트 리스너
newRoomBtn.addEventListener('click', () => {
    newRoomModal.classList.add('active');
    roomNameInput.focus();
});



cancelBtn.addEventListener('click', () => {
    newRoomModal.classList.remove('active');
    roomNameInput.value = '';
});

createBtn.addEventListener('click', createNewRoom);

roomNameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') createNewRoom();
});

backBtn.addEventListener('click', () => {
    if (currentRoom) {
        socket.emit('leave_room', {
            room_id: currentRoom.room_id,
            username: currentUsername
        });
        currentRoom = null;
        chatView.classList.remove('active');
        mainView.classList.add('active');
        loadRooms();
    }
});

sendBtn.addEventListener('click', sendMessage);
// voice button: if detectMode enabled, run multi-language detect; otherwise normal toggle
voiceBtn.addEventListener('click', () => {
    if (detectMode) {
        detectSpeechBest();
    } else {
        toggleVoiceInput();
    }
});

detectBtn.addEventListener('click', () => {
    detectMode = !detectMode;
    detectBtn.classList.toggle('active', detectMode);
    detectBtn.textContent = detectMode ? '자동감지 ON' : '자동감지';
});
ttsBtn.addEventListener('click', () => {
    if (lastTranslatedText) {
        speakText(lastTranslatedText, getSpeechLangCode(targetLanguage));
    }
});
changeNameBtn.addEventListener('click', () => {
    usernameModalTitle.textContent = '사용자 이름 수정';
    usernameInput.value = currentUsername || '';
    usernameConfirmBtn.disabled = usernameInput.value.trim() === '';
    usernameModal.classList.add('active');
    usernameInput.focus();
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
    else emitTyping();
});

// when focusing input on mobile, ensure messages are visible above keyboard
messageInput.addEventListener('focus', () => {
    ensureMessagesAtBottom(200);
});

usernameConfirmBtn.addEventListener('click', () => {
    const username = usernameInput.value.trim();
    if (username) {
        setUsername(username);
    }
});

usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const username = usernameInput.value.trim();
        if (username) {
            setUsername(username);
        }
    }
});

usernameInput.addEventListener('input', (e) => {
    usernameConfirmBtn.disabled = e.target.value.trim() === '';
});

// 언어 선택
mainLanguageSelect.value = sourceLanguage;
languageSelect.value = targetLanguage;
mainLanguageSelect.addEventListener('change', (e) => {
    sourceLanguage = e.target.value;
});

languageSelect.addEventListener('change', (e) => {
    targetLanguage = e.target.value;
});

function loadStoredUsername() {
    const storedName = localStorage.getItem('yujinTranslatorUsername');
    if (storedName) {
        currentUsername = storedName;
        updateUserBadge();
        if (chatUsernameEl) chatUsernameEl.textContent = currentUsername;
    }
}

loadStoredUsername();

// microphone permission hint removed — no-op

function resetUsernameModal() {
    usernameInput.value = '';
    usernameConfirmBtn.disabled = true;
    usernameModalTitle.textContent = '사용자 이름 입력';
}

function getSpeechLangCode(lang) {
    return lang === 'ko' ? 'ko-KR'
        : lang === 'en' ? 'en-US'
        : lang === 'ja' ? 'ja-JP'
        : lang === 'tl' ? 'tl-PH'
        : lang === 'id' ? 'id-ID'
        : lang === 'vi' ? 'vi-VN'
        : `${lang}`;
}

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        voiceBtn.disabled = true;
        voiceBtn.title = '브라우저가 음성 인식을 지원하지 않습니다.';
        return;
    }

    recognition = new SpeechRecognition();
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        messageInput.value = transcript;
        messageInput.focus();
        displaySystemMessage('음성 인식 완료 — 내용을 확인한 뒤 전송하세요.');
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        try { recognition.stop(); } catch (e) {}
        voiceBtn.classList.remove('active');
        voiceBtn.textContent = '🎙';

        const err = event && event.error ? event.error : '';
        if (err === 'not-allowed' || err === 'permission-denied' || err === 'service-not-allowed') {
            displaySystemMessage('마이크 권한이 거부되었습니다. 브라우저의 사이트 설정에서 마이크 접근을 허용해 주세요.');
        } else if (err === 'no-speech') {
            displaySystemMessage('음성이 감지되지 않았습니다. 조용한 곳에서 다시 시도하세요.');
        } else if (err === 'network' || err === 'network-error') {
            displaySystemMessage('네트워크 오류로 음성 인식에 실패했습니다. 네트워크 상태를 확인하세요.');
        } else {
            displaySystemMessage('음성 인식 중 오류가 발생했습니다. 브라우저를 재시작하거나 다른 브라우저로 시도해 보세요.');
        }
    };

    recognition.onend = () => {
        voiceBtn.classList.remove('active');
        voiceBtn.textContent = '🎙';
    };
}

function toggleVoiceInput() {
    if (!recognition) {
        initSpeechRecognition();
        if (!recognition) return;
    }

    if (voiceBtn.classList.contains('active')) {
        recognition.stop();
        voiceBtn.classList.remove('active');
        voiceBtn.textContent = '🎙';
        return;
    }

    // choose recognition language from the visible language selector (what user expects to speak)
    const speechLang = (languageSelect && languageSelect.value) ? languageSelect.value : sourceLanguage;
    // start with safe wrapper to handle mobile/browser quirks
    startRecognitionSafely(getSpeechLangCode(speechLang));
}

// Try to start recognition with retries to handle intermittent mobile/browser failures
// Ensure microphone permission before starting recognition to avoid repeated prompts
async function ensureMicrophonePermission() {
    try {
        if (navigator.permissions && navigator.permissions.query) {
            try {
                const status = await navigator.permissions.query({ name: 'microphone' });
                if (status && status.state) {
                    return status.state; // 'granted' | 'denied' | 'prompt'
                }
            } catch (e) {
                // ignore and fallback to getUserMedia
            }
        }

        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // If a permission request is already in progress, wait for it instead of creating a new prompt
            if (permissionRequestPromise) {
                try {
                    return await permissionRequestPromise;
                } catch (e) {
                    return 'denied';
                }
            }

            // create a single shared permission request promise
            permissionRequestPromise = navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    stream.getTracks().forEach(t => t.stop());
                    return 'granted';
                })
                .catch(e => {
                    const name = e && e.name ? e.name : '';
                    if (name === 'NotAllowedError' || name === 'SecurityError' || name === 'NotFoundError') return 'denied';
                    return 'denied';
                })
                .finally(() => { permissionRequestPromise = null; });

            try {
                return await permissionRequestPromise;
            } catch (e) {
                return 'denied';
            }
        }
    } catch (e) {
        console.warn('Permission check error', e);
    }
    return 'unsupported';
}

// Try to start recognition with retries to handle intermittent mobile/browser failures
async function startRecognitionSafely(lang, maxRetries = 2, delayMs = 600) {
    // check permission first
    const perm = await ensureMicrophonePermission();
    if (perm === 'denied') {
        displaySystemMessage('마이크 권한이 거부되어 음성 입력을 시작할 수 없습니다. 브라우저 사이트 설정에서 마이크 접근을 허용하세요.');
        return;
    }
    if (perm === 'unsupported') {
        displaySystemMessage('브라우저에서 마이크 권한 상태를 확인할 수 없습니다. HTTPS로 접속하거나 최신 브라우저를 사용하세요.');
        // continue and attempt to start once; but avoid multiple permission prompts
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        displaySystemMessage('브라우저가 음성 인식을 지원하지 않습니다.');
        return;
    }

    let attempts = 0;

    const tryStart = () => {
        attempts += 1;
        try {
            if (!recognition) initSpeechRecognition();
            if (!recognition) return;
            recognition.lang = lang;
            voiceBtn.classList.add('active');
            voiceBtn.textContent = '⏹';
            recognition.start();
        } catch (e) {
            console.warn('Recognition start failed (attempt', attempts, '):', e);
            try { if (recognition) recognition.stop(); } catch (e2) {}
            voiceBtn.classList.remove('active');
            voiceBtn.textContent = '🎙';
            // If permission was denied, do not retry (avoid repeated permission prompts)
            if (perm === 'denied') {
                displaySystemMessage('마이크 권한이 거부되었습니다. 설정에서 허용한 뒤 다시 시도하세요.');
                return;
            }
            if (attempts <= maxRetries) {
                setTimeout(tryStart, delayMs);
            } else {
                displaySystemMessage('마이크를 시작하지 못했습니다. 권한 또는 브라우저 호환성을 확인하세요.');
            }
        }
    };

    tryStart();
}

// Use Web Speech API to recognize once for a specific language. Returns {transcript, confidence} or null.
function recognizeOnce(lang, timeout = 4000) {
    return new Promise((resolve) => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return resolve(null);

        const r = new SpeechRecognition();
        r.interimResults = false;
        r.maxAlternatives = 1;
        r.lang = lang;

        let finished = false;

        const finish = (res) => {
            if (finished) return;
            finished = true;
            try { r.stop(); } catch (e) {}
            resolve(res);
        };

        r.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const confidence = event.results[0][0].confidence || 0;
            finish({ transcript, confidence, lang });
        };

        r.onerror = () => finish(null);
        r.onend = () => finish(null);

        try {
            r.start();
        } catch (e) {
            finish(null);
        }

        // timeout fallback
        setTimeout(() => finish(null), timeout + 100);
    });
}

// Try recognition across multiple languages and pick the best confidence result.
async function detectSpeechBest() {
    const detectLangs = ['ja-JP','en-US','tl-PH','id-ID','vi-VN','ko-KR'];
    if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
        alert('브라우저가 음성 인식을 지원하지 않습니다.');
        return;
    }

    detectBtn.disabled = true;
    detectBtn.classList.add('active');
    const origVoiceText = voiceBtn.textContent;
    voiceBtn.textContent = '듣는 중...';

    let best = { confidence: 0, transcript: null, lang: null };

    for (const lang of detectLangs) {
        const res = await recognizeOnce(lang, 3500);
        if (res && res.transcript) {
            if ((res.confidence || 0) > best.confidence) {
                best = { confidence: res.confidence || 0, transcript: res.transcript, lang: res.lang };
            }
            // if confident enough, stop early
            if ((res.confidence || 0) > 0.7) break;
        }
    }

    detectBtn.disabled = false;
    detectBtn.classList.toggle('active', detectMode);
    voiceBtn.textContent = origVoiceText;

    if (best.transcript) {
        messageInput.value = best.transcript;
        sourceLanguage = best.lang && best.lang.startsWith('ko') ? 'ko' : 'auto';
        messageInput.focus();
        displaySystemMessage('자동 감지 완료 — 내용을 확인한 뒤 전송하세요.');
    } else {
        alert('음성 인식에 실패했습니다. 다른 언어로 다시 시도해보세요.');
    }
}

// 함수들
function showUsernameModal() {
    usernameModalTitle.textContent = '사용자 이름 입력';
    usernameModal.classList.add('active');
    usernameInput.focus();
}

function updateUserBadge() {
    if (!currentUsername) {
        userBadge.hidden = true;
        return;
    }

    userBadgeName.textContent = `안녕하세요, ${currentUsername}님`;
    userBadge.hidden = false;
}

function setUsername(username) {
    currentUsername = username;
    localStorage.setItem('yujinTranslatorUsername', username);
    usernameModal.classList.remove('active');
    updateUserBadge();
    // update compact header username if present
    if (chatUsernameEl) chatUsernameEl.textContent = currentUsername;
    resetUsernameModal();
    loadRooms();
}

async function loadRooms() {
    try {
        const response = await fetch('/api/rooms');
        const data = await response.json();

        if (data.success) {
            displayRooms(data.rooms);
        }
    } catch (error) {
        console.error('Error loading rooms:', error);
    }
}

function displayRooms(rooms) {
    if (rooms.length === 0) {
        roomsList.innerHTML = '<p class="empty-state">채팅방이 없습니다</p>';
        return;
    }

    roomsList.innerHTML = rooms.map(room => `
        <div class="room-item" onclick="joinRoom(${room.room_id}, '${room.room_name}')">
            <div class="room-item-info">
                <h3>${room.room_name}</h3>
                <p>${new Date(room.created_at).toLocaleDateString('ko-KR')}</p>
            </div>
            <div class="room-item-actions">
                <button class="room-delete-btn" onclick="deleteRoom(event, ${room.room_id})">삭제</button>
                <div class="room-item-icon">→</div>
            </div>
        </div>
    `).join('');
}

async function deleteRoom(event, roomId) {
    event.stopPropagation();

    if (!confirm('정말 이 채팅방을 삭제하시겠습니까?')) {
        return;
    }

    try {
        const response = await fetch(`/api/rooms/${roomId}`, {
            method: 'DELETE'
        });
        const data = await response.json();

        if (data.success) {
            if (currentRoom && currentRoom.room_id === roomId) {
                currentRoom = null;
                chatView.classList.remove('active');
                mainView.classList.add('active');
            }
            loadRooms();
        } else {
            alert(`오류: ${data.error}`);
        }
    } catch (error) {
        console.error('Error deleting room:', error);
        alert('채팅방 삭제 중 오류가 발생했습니다');
    }
}

async function createNewRoom() {
    const roomName = roomNameInput.value.trim();
    if (!roomName) {
        alert('채팅방 이름을 입력하세요');
        return;
    }

    try {
        const response = await fetch('/api/rooms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                room_name: roomName,
                language: LANGUAGE_LABELS[targetLanguage] || 'Korean'
            })
        });

        const data = await response.json();

        if (data.success) {
            newRoomModal.classList.remove('active');
            roomNameInput.value = '';
            joinRoom(data.room_id, roomName);
            loadRooms();
        } else {
            alert(`오류: ${data.error}`);
        }
    } catch (error) {
        console.error('Error creating room:', error);
        alert('채팅방 생성 중 오류가 발생했습니다');
    }
}

function joinRoom(roomId, roomName) {
    currentRoom = { room_id: roomId, room_name: roomName };

    socket.emit('join_room', {
        room_id: roomId,
        username: currentUsername,
        my_language: sourceLanguage
    });

    mainView.classList.remove('active');
    chatView.classList.add('active');
    messagesContainer.innerHTML = '';
    messageInput.value = '';
    messageInput.focus();

    loadMessages(roomId);
}

async function loadMessages(roomId) {
    try {
        const response = await fetch(`/api/rooms/${roomId}/messages?my_lang=${sourceLanguage}`);
        const data = await response.json();

        if (data.success) {
            messagesContainer.innerHTML = '';
            data.messages.forEach(msg => {
                displayMessage(msg, true);
            });
                // ensure bottom after loading history (esp. on mobile)
                ensureMessagesAtBottom(80);
        }
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function displayMessage(message, isHistorical = false) {
    const isOwnMessage = message.username === currentUsername;
    const messageEl = document.createElement('div');
    messageEl.className = `message ${isOwnMessage ? 'own' : 'other'}`;

    const languageLabel = LANGUAGE_LABELS[message.language] || message.language;
    const translatedLabel = LANGUAGE_LABELS[message.target_language_code] || message.target_language || '번역';

    if (message.translated) {
        lastTranslatedText = message.translated;
    }

    messageEl.innerHTML = `
        ${!isOwnMessage ? `<div class="message-username">${message.username}</div>` : ''}
        <div class="message-bubble">
            <div class="message-original">${escapeHtml(message.message)}</div>
            ${message.translated ? `
                <div class="message-translation">
                    <small>[${translatedLabel}] ${escapeHtml(message.translated)}</small>
                </div>
            ` : ''}
        </div>
        ${message.created_at ? `<div class="message-time">${formatTime(message.created_at)}</div>` : ''}
    `;

    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    // on mobile, try multiple delayed scrolls to account for keyboard resize
    if (window.innerWidth <= 640) {
        ensureMessagesAtBottomRetries();
    }
}

function ensureMessagesAtBottomRetries() {
    // schedule several scroll attempts to handle mobile keyboard/viewport changes
    [80, 300, 700].forEach(delay => ensureMessagesAtBottom(delay));
}

// Ensure the messages container is scrolled to bottom, with a small delay
// to allow mobile keyboards to resize the viewport.
function ensureMessagesAtBottom(delay = 120) {
    setTimeout(() => {
        try {
            if (messagesContainer.lastElementChild) {
                messagesContainer.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end' });
            } else {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        } catch (e) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }, delay);
}

function displaySystemMessage(text) {
    const messageEl = document.createElement('div');
    messageEl.className = 'system-message';
    messageEl.textContent = text;
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    setTimeout(() => {
        typingIndicator.style.display = 'none';
    }, 3000);
}

function sendMessage() {
    const message = messageInput.value.trim();

    if (!message || !currentRoom) {
        return;
    }

    socket.emit('send_message', {
        room_id: currentRoom.room_id,
        username: currentUsername,
        message: message,
        language: 'auto',
        target_language: targetLanguage
    });

    messageInput.value = '';
    messageInput.focus();
    // scroll after sending so the latest message is visible above keyboard
    ensureMessagesAtBottom(180);
}

function speakText(text, lang) {
    if (!window.speechSynthesis) {
        alert('브라우저가 음성 합성을 지원하지 않습니다.');
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    window.speechSynthesis.speak(utterance);
}

function emitTyping() {
    if (!currentRoom) return;

    socket.emit('typing', {
        room_id: currentRoom.room_id,
        username: currentUsername
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    initSocket();
});
