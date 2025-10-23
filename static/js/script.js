document.getElementById('messageForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const userMessage = document.getElementById('userMessage').value;
    fetch('/support_bot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `message=${encodeURIComponent(userMessage)}`,
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('botResponse').innerText = data.response;
    });
});
