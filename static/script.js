document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('gratitude-form');
    const input = document.getElementById('gratitude-input');
    const list = document.getElementById('gratitudes-list');

    // Create loading overlay
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.background = 'rgba(255,255,255,0.8)';
    overlay.style.display = 'flex';
    overlay.style.flexDirection = 'column';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.style.zIndex = 2000;
    overlay.style.fontSize = '1.3em';
    overlay.style.color = '#1877f2';
    overlay.style.fontWeight = 'bold';
    overlay.style.backdropFilter = 'blur(3px)';
    overlay.innerHTML = '<div id="loading-spinner" style="margin-bottom:20px;"><i class="fa-solid fa-spinner fa-spin fa-2x"></i></div><div id="loading-message">Saving your gratitude...</div>';
    overlay.style.display = 'none';
    document.body.appendChild(overlay);
    const loadingMessage = overlay.querySelector('#loading-message');

    function showOverlay(msg) {
        loadingMessage.textContent = msg;
        overlay.style.display = 'flex';
    }
    function hideOverlay() {
        overlay.style.display = 'none';
    }

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
    let submitting = false;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (submitting) return;
        const text = input.value.trim();
        if (text) {
            submitting = true;
            showOverlay('Saving your gratitude...');
            try {
                // Start submit
                const response = await fetch('/gratitudes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ text })
                });
                showOverlay('Generating image...');
                const newGratitude = await response.json();
                showOverlay('Success!');
                addGratitudeToList(newGratitude);
                input.value = '';
                setTimeout(() => {
                    hideOverlay();
                    submitting = false;
                }, 900);
            } catch (error) {
                showOverlay('Something went wrong. Please try again.');
                setTimeout(() => {
                    hideOverlay();
                    submitting = false;
                }, 1800);
                console.error('Error submitting gratitude:', error);
            }
        }
    });

    // Initial load
    getGratitudes();
});
