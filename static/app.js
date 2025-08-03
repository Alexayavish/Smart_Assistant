document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("user-input");
    const chatWindow = document.getElementById("chat-window");
    const languageSelect = document.getElementById("language-select");  // new dropdown for languages

    function appendMessage(sender, text) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");
        messageDiv.classList.add(sender === "You" ? "user" : "assistant");
        messageDiv.textContent = `${sender}: ${text}`;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const userText = input.value.trim();
        if (!userText) return;

        const language = languageSelect ? languageSelect.value : 'en';

        appendMessage("You", userText);
        input.value = "";
        input.disabled = true;

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: userText, language })  // send language here
            });

            const data = await res.json();

            if (res.ok) {
                appendMessage("DESKTECH", data.response);
            } else {
                appendMessage("Error", data.error || "Unknown error");
            }
        } catch (err) {
            appendMessage("Error", err.message);
        } finally {
            input.disabled = false;
            input.focus();
        }
    });
});
