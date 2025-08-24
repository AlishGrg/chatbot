 window.onload = function () {
      const box = document.getElementById("chat-box");
      box.innerHTML += `
        <div class="bot-response">
          <p class="bot-message">
            <span class="icon">🤖</span><strong>Bot:</strong><br>👋 Hi there! I am Alex, your project management companion.
          </p>
          <p class="bot-message"><span class="icon">🤖</span><strong>Bot:</strong><br>To compare projects, type 'compare projects' or select any of the option for the calculations. Else, you can ask me about various PM concepts.</p>
        </div>
        <div class="quick-buttons">
          <button onclick="sendQuick('Calculate Net Profit')">Net Profit</button>
          <button onclick="sendQuick('Calculate ROI')">ROI</button>
          <button onclick="sendQuick('Calculate NPV')">NPV</button>
          <button onclick="sendQuick('Calculate IRR')">IRR</button>
          <button onclick="sendQuick('Calculate Payback')">Payback</button>
        </div>
      `;
    };

    function sendQuick(text) {
      document.getElementById("user-input").value = text;
      sendMessage();
    }

    function sendMessage() {
      const input = document.getElementById("user-input");
      const message = input.value.trim();
      const box = document.getElementById("chat-box");
      if (!message) return;

      box.innerHTML += `<p class="user-message"><span class="icon">👤</span><strong>You:</strong><br>${message}</p>`;
      box.scrollTop = box.scrollHeight;
      input.value = "";

      const typingId = `typing-${Date.now()}`;
      box.innerHTML += `<p class="bot-message" id="${typingId}"><span class="icon">🤖</span><strong>Bot:</strong><br><em>Typing...</em></p>`;
      box.scrollTop = box.scrollHeight;

      fetch("/chat", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
      })
        .then(res => res.json())
        .then(data => {
          const typingElement = document.getElementById(typingId);
          if (typingElement) {
            typingElement.innerHTML = `<span class="icon">🤖</span><strong>Bot:</strong><br>${data.reply}`;
          }
          box.scrollTop = box.scrollHeight;
        })
        .catch(() => {
          const typingElement = document.getElementById(typingId);
          if (typingElement) {
            typingElement.innerHTML = `<span class="icon">🤖</span><strong>Bot:</strong><br>❌ Failed to get response. Please try again.`;
          }
          box.scrollTop = box.scrollHeight;
        });
    }

    document.getElementById("user-input").addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
      }
    });
