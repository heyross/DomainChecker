document.addEventListener('DOMContentLoaded', () => {
    const generateForm = document.getElementById('generate-form');
    const checkForm = document.getElementById('check-form');
    const resultsDiv = document.getElementById('results');

    generateForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const description = document.getElementById('description').value;
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({description})
        });
        const data = await response.json();
        resultsDiv.innerHTML = `<h3>Generated Names:</h3><ul>${data.names.map(name => `<li>${name}</li>`).join('')}</ul>`;
    });

    checkForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const domain = document.getElementById('domain').value;
        const response = await fetch('/check', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({domain})
        });
        const data = await response.json();
        resultsDiv.innerHTML = `<h3>Domain Status:</h3><p>${domain} is ${data.domain_status}</p>`;
    });
});
