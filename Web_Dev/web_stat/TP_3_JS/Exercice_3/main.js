function applyStyles() {
    // Body 
    document.body.style.fontFamily = 'Arial, sans-serif';
    document.body.style.margin = '20px';
    
    // Container 
    const container = document.getElementById('container');
    container.style.maxWidth = '600px';
    container.style.margin = '0 auto';
    container.style.padding = '20px';
    container.style.border = '1px solid #ddd';
    container.style.borderRadius = '5px';
    
    // Form groups
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        group.style.marginBottom = '15px';
    });
    
    // Labels
    const labels = document.querySelectorAll('label');
    labels.forEach(label => {
        label.style.marginRight = '10px';
        label.style.fontWeight = 'bold';
        label.style.display = 'inline-block';
        label.style.minWidth = '80px';
    });
    
    // URL Input
    const urlInput = document.getElementById('adr');
    urlInput.style.padding = '8px';
    urlInput.style.border = '1px solid #ccc';
    urlInput.style.borderRadius = '4px';
    urlInput.style.width = '100%';
    urlInput.style.boxSizing = 'border-box';
    urlInput.style.marginTop = '5px';
    
    // Number Inputs
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.style.padding = '8px';
        input.style.border = '1px solid #ccc';
        input.style.borderRadius = '4px';
        input.style.width = '80px';
        input.style.margin = '0 5px';
    });
    
    // Open Button
    const openButton = document.getElementById('openButton');
    openButton.style.padding = '10px 15px';
    openButton.style.margin = '0 5px';
    openButton.style.backgroundColor = '#4CAF50';
    openButton.style.color = 'white';
    openButton.style.border = 'none';
    openButton.style.borderRadius = '4px';
    openButton.style.cursor = 'pointer';
    
    // Close Button
    const closeButton = document.getElementById('closeButton');
    closeButton.style.padding = '10px 15px';
    closeButton.style.margin = '0 5px';
    closeButton.style.backgroundColor = '#f44336';
    closeButton.style.color = 'white';
    closeButton.style.border = 'none';
    closeButton.style.borderRadius = '4px';
    closeButton.style.cursor = 'pointer';
    
    const header = document.querySelector('h1');
    header.style.color = '#333';
}

let openedWindow = null;

function openWindow() {
    const url = document.getElementById('adr').value;
    
    if (!url) {
        alert("Veuillez entrer une URL valide");
        return;
    }
    
    let width = document.getElementById('width').value || 600;
    let height = document.getElementById('height').value || 400;
    
    if (openedWindow && !openedWindow.closed) {
        openedWindow.close();
    }
    
    const options = `width=${width},height=${height},resizable=yes,scrollbars=yes,location=yes`;
    
    openedWindow = window.open(url, 'windowName', options);
    
    if (openedWindow) {
        openedWindow.focus();
    }
}

function closeWindow() {
    if (openedWindow && !openedWindow.closed) {
        if (confirm("Êtes-vous sûr de vouloir fermer cette fenêtre?")) {
            openedWindow.close();
        }
    } else {
        alert("Aucune fenêtre n'est actuellement ouverte");
    }
}

window.onload = function() {
    applyStyles();
    
    document.getElementById('openButton').addEventListener('click', openWindow);
    document.getElementById('closeButton').addEventListener('click', closeWindow);
};