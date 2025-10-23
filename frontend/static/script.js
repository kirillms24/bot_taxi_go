document.getElementById("chat-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const message = document.getElementById("message").value;

    const response = await fetch("/support", {
        method: "POST",
        body: new URLSearchParams({ customer_name: name, message: message })
    });
    const data = await response.json();

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<p><b>Вы:</b> ${message}</p><p><b>Бот:</b> ${data.response}</p>`;
    document.getElementById("message").value = "";
});
