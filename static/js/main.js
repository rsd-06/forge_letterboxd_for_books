// Bookboxd Client JavaScript
document.addEventListener('DOMContentLoaded', () => {

    // Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-toggle');
    const mobileNavDrawer = document.getElementById('mobile-nav-drawer');
    if (mobileMenuBtn && mobileNavDrawer) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileNavDrawer.classList.toggle('hidden');
        });
    }

    // 1. Spoilers Reveal Click
    document.querySelectorAll('.spoiler-toggle-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const container = btn.closest('.spoiler-container');
            if (container) {
                const content = container.querySelector('.spoiler-content');
                if (content) {
                    content.classList.toggle('spoiler-hidden');
                    if (!content.classList.contains('spoiler-hidden')) {
                        btn.textContent = 'Hide Spoilers';
                    } else {
                        btn.textContent = 'Reveal Spoilers';
                    }
                }
            }
        });
    });

    // 2. Star Rating Selector in Rate Modal/Forms
    const starContainer = document.getElementById('star-rating-selector');
    const ratingInput = document.getElementById('selected-rating-input');
    const ratingLabel = document.getElementById('rating-display-label');

    if (starContainer && ratingInput) {
        const stars = starContainer.querySelectorAll('.star-icon');
        
        function highlightStars(val) {
            stars.forEach(s => {
                const sVal = parseFloat(s.dataset.value);
                if (sVal <= val) {
                    s.classList.remove('text-stone-300');
                    s.classList.add('text-amber-500');
                } else {
                    s.classList.remove('text-amber-500');
                    s.classList.add('text-stone-300');
                }
            });
            if (ratingLabel) {
                ratingLabel.textContent = `${val.toFixed(1)} / 5.0`;
            }
        }

        stars.forEach(star => {
            star.addEventListener('mouseenter', () => {
                highlightStars(parseFloat(star.dataset.value));
            });
            star.addEventListener('click', () => {
                const val = parseFloat(star.dataset.value);
                ratingInput.value = val;
                highlightStars(val);
            });
        });

        starContainer.addEventListener('mouseleave', () => {
            const current = parseFloat(ratingInput.value) || 0;
            highlightStars(current);
        });

        // Initialize with existing value
        if (ratingInput.value) {
            highlightStars(parseFloat(ratingInput.value));
        }
    }

    // 3. Floating Gemini AI Chat Widget
    const chatToggle = document.getElementById('ai-chat-toggle');
    const chatWidget = document.getElementById('ai-chat-widget');
    const chatClose = document.getElementById('ai-chat-close');
    const chatInput = document.getElementById('ai-chat-input');
    const chatSend = document.getElementById('ai-chat-send');
    const chatMessages = document.getElementById('ai-chat-messages');

    let chatHistory = [];

    if (chatToggle && chatWidget) {
        chatToggle.addEventListener('click', () => {
            chatWidget.classList.toggle('hidden');
            if (!chatWidget.classList.contains('hidden') && chatInput) {
                chatInput.focus();
            }
        });

        if (chatClose) {
            chatClose.addEventListener('click', () => {
                chatWidget.classList.add('hidden');
            });
        }

        async function sendChatMessage() {
            const text = chatInput.value.trim();
            if (!text) return;

            // Add user bubble
            appendChatBubble('user', text);
            chatInput.value = '';
            chatHistory.push({ sender: 'user', text });

            // Add typing indicator
            const typingId = appendTypingIndicator();
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const csrfToken = getCookie('csrftoken');
                const response = await fetch('/ai-assistant/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        message: text,
                        history: chatHistory
                    })
                });

                removeTypingIndicator(typingId);

                if (response.ok) {
                    const data = await response.json();
                    appendChatBubble('assistant', data.response, data.is_live_ai);
                    chatHistory.push({ sender: 'assistant', text: data.response });
                } else {
                    appendChatBubble('assistant', "I'm having a little trouble connecting right now. Please check back in a moment!");
                }
            } catch (err) {
                removeTypingIndicator(typingId);
                appendChatBubble('assistant', "Could not reach the AI service. Please ensure your network is connected.");
            }

            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        if (chatSend && chatInput) {
            chatSend.addEventListener('click', sendChatMessage);
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    sendChatMessage();
                }
            });
        }
    }

    function appendChatBubble(role, text, isLiveAi = false) {
        if (!chatMessages) return;
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-3`;

        const bubble = document.createElement('div');
        if (role === 'user') {
            bubble.className = 'bg-[#382110] text-amber-50 rounded-2xl rounded-tr-none px-4 py-2 max-w-[85%] text-sm shadow-sm';
            bubble.textContent = text;
        } else {
            bubble.className = 'bg-stone-100 text-stone-800 rounded-2xl rounded-tl-none px-4 py-2.5 max-w-[85%] text-sm shadow-sm border border-stone-200';
            
            // Format basic markdown like bold and bullets
            let formatted = text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/•\s+(.*)/g, '<div class="ml-2 mb-1">• $1</div>')
                .replace(/\n\n/g, '<div class="h-2"></div>')
                .replace(/\n/g, '<br>');

            bubble.innerHTML = formatted;
            if (isLiveAi) {
                const badge = document.createElement('div');
                badge.className = 'text-[10px] text-amber-700 mt-1 font-semibold flex items-center gap-1';
                badge.innerHTML = '✨ Powered by Gemini Live';
                bubble.appendChild(badge);
            }
        }

        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'flex justify-start mb-3';
        div.innerHTML = `
            <div class="bg-stone-100 text-stone-500 rounded-2xl rounded-tl-none px-4 py-2 text-xs flex items-center gap-1.5 border border-stone-200">
                <span class="animate-bounce">●</span>
                <span class="animate-bounce" style="animation-delay: 0.15s">●</span>
                <span class="animate-bounce" style="animation-delay: 0.3s">●</span>
                <span class="ml-1 text-[11px]">Bibliophile is thinking...</span>
            </div>
        `;
        chatMessages.appendChild(div);
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // CSRF helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
