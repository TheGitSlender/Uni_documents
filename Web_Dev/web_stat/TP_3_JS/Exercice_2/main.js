function applyPageStyles() {
    // Body 
    document.body.style.fontFamily = 'Arial, sans-serif';
    document.body.style.margin = '20px';
    
    // Container 
    const container = document.getElementById('container');
    container.style.display = 'flex';
    container.style.flexWrap = 'wrap';
    container.style.gap = '20px';
    
    // Control Panel
    const controlPanel = document.getElementById('controlPanel');
    controlPanel.style.flex = '1';
    controlPanel.style.minWidth = '300px';
    controlPanel.style.padding = '15px';
    controlPanel.style.border = '1px solid #ddd';
    controlPanel.style.borderRadius = '5px';
    
    // Preview Area
    const previewArea = document.getElementById('previewArea');
    previewArea.style.flex = '2';
    previewArea.style.minWidth = '300px';
    previewArea.style.minHeight = '400px';
    previewArea.style.padding = '15px';
    previewArea.style.border = '1px solid #ddd';
    previewArea.style.borderRadius = '5px';
    previewArea.style.position = 'relative';
    
    // Custom Div
    const customDiv = document.getElementById('customDiv');
    customDiv.style.padding = '15px';
    customDiv.style.backgroundColor = '#f0f0f0';
    customDiv.style.width = '200px';
    customDiv.style.height = '100px';
    customDiv.style.position = 'relative';
    customDiv.style.overflow = 'auto';
    
    // Inputs
    const inputs = document.querySelectorAll('input:not([type="radio"])');
    inputs.forEach(input => {
        input.style.padding = '8px';
        input.style.width = input.type === 'range' ? '200px' : '100%';
        input.style.border = '1px solid #ccc';
        input.style.borderRadius = '4px';
        input.style.boxSizing = 'border-box';
        input.style.marginTop = '5px';
    });
    
    // Textarea
    const textarea = document.getElementById('divText');
    textarea.style.padding = '8px';
    textarea.style.width = '100%';
    textarea.style.border = '1px solid #ccc';
    textarea.style.borderRadius = '4px';
    textarea.style.boxSizing = 'border-box';
    
    // Buttons
    const applyButton = document.getElementById('applyButton');
    applyButton.style.padding = '10px 15px';
    applyButton.style.marginRight = '10px';
    applyButton.style.backgroundColor = '#4CAF50';
    applyButton.style.color = 'white';
    applyButton.style.border = 'none';
    applyButton.style.borderRadius = '4px';
    applyButton.style.cursor = 'pointer';
    
    const resetButton = document.getElementById('resetButton');
    resetButton.style.padding = '10px 15px';
    resetButton.style.backgroundColor = '#f44336';
    resetButton.style.color = 'white';
    resetButton.style.border = 'none';
    resetButton.style.borderRadius = '4px';
    resetButton.style.cursor = 'pointer';
    
    // Labels
    const labels = document.querySelectorAll('label');
    labels.forEach(label => {
        if (label.getAttribute('for') && 
           !label.getAttribute('for').startsWith('pos')) {
            label.style.fontWeight = 'bold';
        }
    });
    
    // Spacing
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        group.style.marginBottom = '15px';
    });
}

window.onload = function() {
    applyPageStyles();
    
    document.getElementById('divOpacity').addEventListener('input', function() {
        document.getElementById('opacityValue').textContent = this.value + '%';
    });
    
    document.getElementById('posAbsolute').addEventListener('change', togglePositionInputs);
    document.getElementById('posRelative').addEventListener('change', togglePositionInputs);
    
    document.getElementById('applyButton').addEventListener('click', applySettings);
    document.getElementById('resetButton').addEventListener('click', resetSettings);
};

function togglePositionInputs() {
    const absoluteInputs = document.getElementById('absoluteInputs');
    const isAbsolute = document.getElementById('posAbsolute').checked;
    
    absoluteInputs.style.display = isAbsolute ? 'block' : 'none';
}

function applySettings() {
    const customDiv = document.getElementById('customDiv');
    
    customDiv.style.backgroundColor = document.getElementById('divColor').value;
    
    const isAbsolute = document.getElementById('posAbsolute').checked;
    customDiv.style.position = isAbsolute ? 'absolute' : 'relative';
    
    if (isAbsolute) {
        const unit = document.querySelector('input[name="positionUnit"]:checked').value;
        const topValue = document.getElementById('topPos').value;
        const leftValue = document.getElementById('leftPos').value;
        
        customDiv.style.top = topValue + unit;
        customDiv.style.left = leftValue + unit;
    } else {
        customDiv.style.top = '';
        customDiv.style.left = '';
    }
    
    const width = document.getElementById('divWidth').value;
    const height = document.getElementById('divHeight').value;
    
    customDiv.style.width = width ? width + 'px' : '200px';
    customDiv.style.height = height ? height + 'px' : '100px';
    
    customDiv.textContent = document.getElementById('divText').value;
    
    const opacity = document.getElementById('divOpacity').value / 100;
    customDiv.style.opacity = opacity;
}

function resetSettings() {
    // Reset controls
    document.getElementById('divColor').value = '#f0f0f0';
    document.getElementById('posRelative').checked = true;
    document.getElementById('posAbsolute').checked = false;
    document.getElementById('posPixels').checked = true;
    document.getElementById('posPercent').checked = false;
    document.getElementById('topPos').value = '0';
    document.getElementById('leftPos').value = '0';
    document.getElementById('divWidth').value = '200';
    document.getElementById('divHeight').value = '100';
    document.getElementById('divText').value = 'Ceci est un calque configurable.';
    document.getElementById('divOpacity').value = '100';
    document.getElementById('opacityValue').textContent = '100%';
    
    togglePositionInputs();
    
    const customDiv = document.getElementById('customDiv');
    customDiv.style.backgroundColor = '#f0f0f0';
    customDiv.style.position = 'relative';
    customDiv.style.top = '';
    customDiv.style.left = '';
    customDiv.style.width = '200px';
    customDiv.style.height = '100px';
    customDiv.textContent = 'Ceci est un calque configurable.';
    customDiv.style.opacity = '1';
}