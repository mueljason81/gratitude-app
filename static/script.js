document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('gratitude-form');
    const input = document.getElementById('gratitude-input');
    const list = document.getElementById('gratitudes-list');

    // Fetch and display existing gratitudes
    async function getGratitudes() {
        try {
            const response = await fetch('/gratitudes');
            const gratitudes = await response.json();
            list.innerHTML = '';
            gratitudes.forEach(gratitude => {
                addGratitudeToList(gratitude);
            });
        } catch (error) {
            console.error('Error fetching gratitudes:', error);
        }
    }

    // Add a single gratitude to the list
    function addGratitudeToList(gratitude) {
        const item = document.createElement('div');
        item.className = 'gratitude-item';

        const date = new Date(gratitude.timestamp).toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric'
        });

        item.innerHTML = `
            <div class="date">${date}</div>
            <div class="text">${gratitude.text}</div>
        `;
        list.prepend(item);
    }

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (text) {
            try {
                const response = await fetch('/gratitudes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ text })
                });
                const newGratitude = await response.json();
                addGratitudeToList(newGratitude);
                input.value = '';
            } catch (error) {
                console.error('Error submitting gratitude:', error);
            }
        }
    });

    // Initial load
    getGratitudes();
});
