document.addEventListener('DOMContentLoaded', () => {
    const leadForm = document.getElementById('leadForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    const messageBox = document.getElementById('messageBox');

    // Configuration: Update this URL for production deployment
    const WEBHOOK_URL = 'http://localhost:5678/webhook-test/new-lead';

    leadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Reset messages
        messageBox.classList.add('hidden');
        messageBox.className = 'message-box hidden';

        // 2. Client-side Validation
        const formData = new FormData(leadForm);
        const data = {
            name: formData.get('name').trim(),
            email: formData.get('email').trim(),
            company: formData.get('company').trim(),
            budget: Number(formData.get('budget')),
            requirements: formData.get('requirements').trim()
        };

        // Basic validation check (most handled by HTML 'required' and 'type')
        if (!validateEmail(data.email)) {
            showMessage('Please enter a valid work email.', 'error');
            return;
        }

        // 3. Loading State
        setLoading(true);

        try {
            // 4. Send POST request
            const response = await fetch(WEBHOOK_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                // 5. Success
                showMessage('Thank you! Your inquiry has been sent successfully. Our team will contact you shortly.', 'success');
                leadForm.reset();
            } else {
                // 6. Error handling
                const errorText = await response.text();
                console.error('Submission failed:', errorText);
                showMessage('Something went wrong. Please try again or contact support directly.', 'error');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            showMessage('Connection failed. Please ensure the lead service is running.', 'error');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    }

    function showMessage(text, type) {
        messageBox.textContent = text;
        messageBox.className = `message-box ${type}`;
        messageBox.classList.remove('hidden');
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});
