document.getElementById('deployButton').addEventListener('click', () => {
    window.location.href = 'input.html';
});

document.getElementById('destroyButton').addEventListener('click', async () => {
    try {
        const response = await fetch('http://127.0.0.1:5000/destroy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to trigger destruction');
        }

        const data = await response.json();
        document.getElementById('statusMessage').textContent = data.message;
    } catch (error) {
        console.error('Error triggering destruction:', error.message);
        document.getElementById('statusMessage').textContent = 'Error triggering destruction. Please try again.';
    }
});
