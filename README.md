# Hi there, I'm Ricardo! 👋

Welcome to my GitHub profile. This space is dynamically updated!

<!-- GENERATED_CONTENT_START -->


<div class="profile-container">
  <style>
    .profile-container {
      max-width: 600px;
      width: 100%;
      padding: 30px 20px;
      background: #18191d;
      border-radius: 12px;
      margin: 20px auto;
    }
    
    .message-button {
      background: linear-gradient(to right, #5a48f2, #a078f2);
      border-radius: 28px;
      padding: 15px 25px;
      margin: 18px 0;
      display: flex;
      align-items: center;
      opacity: 0;
      transform: translateY(10px);
      font-size: 1.1em;
      font-weight: 500;
      color: #ffffff;
      box-shadow: 0 4px 15px rgba(90, 72, 242, 0.3);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    }
    
    .message-button.show {
      opacity: 1;
      transform: translateY(0);
      transition: all 0.4s ease-out;
    }
    
    .emoji {
      margin-right: 10px;
      font-size: 1.2em;
    }
    
    .typing-indicator {
      height: 58px;
      display: flex;
      align-items: center;
      padding-left: 25px;
      opacity: 0;
      font-size: 1.1em;
      color: #8b949e;
    }
    
    .typing-indicator.show {
      opacity: 1;
    }
    
    .cursor {
      animation: blink 1s infinite;
      margin-left: 2px;
    }
    
    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }
    
    @media (max-width: 768px) {
      .profile-container {
        padding: 20px 15px;
        max-width: 100%;
      }
      
      .message-button {
        padding: 12px 20px;
        font-size: 1em;
      }
    }
  </style>
  
  <div class="typing-indicator" id="typing-0">|</div>
  <div class="message-button" id="msg-0">
    <span class="emoji">👋</span>
    <span class="text" aria-live="polite"></span>
    <span class="cursor">|</span>
  </div>

  <div class="typing-indicator" id="typing-1">|</div>
  <div class="message-button" id="msg-1">
    <span class="emoji">📍</span>
    <span class="text" aria-live="polite"></span>
    <span class="cursor">|</span>
  </div>

  <div class="typing-indicator" id="typing-2">|</div>
  <div class="message-button" id="msg-2">
    <span class="emoji">💡</span>
    <span class="text" aria-live="polite"></span>
    <span class="cursor">|</span>
  </div>

  <div class="typing-indicator" id="typing-3">|</div>
  <div class="message-button" id="msg-3">
    <span class="emoji">🙏</span>
    <span class="text" aria-live="polite"></span>
    <span class="cursor">|</span>
  </div>

  <script>
    const messages = ["👋 Hi, I'm Ricardo!", "📍 I'm located at São Paulo, SP, Brazil", '💡 AI advancements are accelerating innovation globally.', '🙏 Thanks for stopping by and have a nice Sunday!'];
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

    async function typeText(element, text) {
      const textSpan = element.querySelector('.text');
      const cursor = element.querySelector('.cursor');
      
      for (let i = 0; i <= text.length; i++) {
        textSpan.textContent = text.slice(0, i);
        await sleep(70);
      }
      
      cursor.style.display = 'none';
    }

    async function animateMessage(index) {
      const typingIndicator = document.getElementById(`typing-${index}`);
      const messageButton = document.getElementById(`msg-${index}`);
      
      typingIndicator.classList.add('show');
      await sleep(800);
      
      typingIndicator.classList.remove('show');
      messageButton.classList.add('show');
      await sleep(400);
      
      await typeText(messageButton, messages[index]);
      await sleep(1200);
    }

    async function startAnimation() {
      for (let i = 0; i < messages.length; i++) {
        await animateMessage(i);
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', startAnimation);
    } else {
      startAnimation();
    }
  </script>
</div>


<!-- GENERATED_CONTENT_END -->