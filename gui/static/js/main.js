document.addEventListener('DOMContentLoaded', function() {
    const scanForm = document.getElementById('scanForm');
    const resultsContainer = document.getElementById('resultsContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const downloadReportBtn = document.getElementById('downloadReport');
    const showConfigBtn = document.getElementById('showConfig');
    const configEditor = document.getElementById('configEditor');
    const configText = document.getElementById('configText');
    const saveConfigBtn = document.getElementById('saveConfig');
    
    let currentReport = null;
    
    // Load config when the page loads
    loadConfig();
    
    // Submit scan form
    scanForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            directory: document.getElementById('directory').value,
            recursive: document.getElementById('recursive').checked,
            format: document.getElementById('format').value
        };
        
        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        resultsContainer.innerHTML = '';
        downloadReportBtn.disabled = true;
        
        // Send scan request
        fetch('/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('d-none');
            
            if (data.success) {
                displayResults(data.results);
                downloadReportBtn.disabled = false;
                currentReport = data.results;
            } else {
                resultsContainer.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            }
        })
        .catch(error => {
            loadingIndicator.classList.add('d-none');
            resultsContainer.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
    });
    
    // Display scan results
    function displayResults(results) {
        if (results.report) {
            // HTML or console format
            if (results.format === 'html') {
                // For HTML report, create an iframe
                resultsContainer.innerHTML = `<iframe style="width:100%; height:600px; border:none;" srcdoc="${escapeHtml(results.report)}"></iframe>`;
            } else {
                // For console report, use pre tag
                resultsContainer.innerHTML = `<pre>${escapeHtml(results.report)}</pre>`;
            }
        } else {
            // JSON format, create a summary view
            let html = '<div class="results-summary">';
            
            html += `<h4>Scan Summary</h4>`;
            html += `<p>Directory: ${results.directory}</p>`;
            html += `<p>HTML Files: ${results.html_files}</p>`;
            html += `<p>JS Files: ${results.js_files}</p>`;
            
            // HTML Results
            html += `<h4>HTML Analysis</h4>`;
            html += `<div class="accordion" id="htmlAccordion">`;
            
            results.html_results.forEach((result, index) => {
                const fileId = `html-file-${index}`;
                html += `
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${fileId}">
                                ${result.file}
                            </button>
                        </h2>
                        <div id="${fileId}" class="accordion-collapse collapse" data-bs-parent="#htmlAccordion">
                            <div class="accordion-body">
                                <p><strong>IDs:</strong> ${result.ids.join(', ') || 'None'}</p>
                                <p><strong>Names:</strong> ${result.names.join(', ') || 'None'}</p>
                                <p><strong>Inline Events:</strong></p>
                                <ul>
                                    ${result.inline_events.length ? 
                                        result.inline_events.map(event => `<li>${event[0]} - ${event[1]} = ${event[2]}</li>`).join('') :
                                        '<li>None</li>'
                                    }
                                </ul>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
            
            // JS Results
            html += `<h4 class="mt-4">JavaScript Analysis</h4>`;
            html += `<div class="accordion" id="jsAccordion">`;
            
            results.js_regex_results.forEach((result, index) => {
                const fileId = `js-file-${index}`;
                let vulnerabilityCount = 0;
                Object.values(result.vulnerabilities).forEach(v => vulnerabilityCount += v.length);
                
                html += `
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${fileId}">
                                ${result.file} 
                                ${vulnerabilityCount > 0 ? `<span class="badge bg-danger ms-2">${vulnerabilityCount}</span>` : ''}
                            </button>
                        </h2>
                        <div id="${fileId}" class="accordion-collapse collapse" data-bs-parent="#jsAccordion">
                            <div class="accordion-body">
                                <p><strong>Vulnerabilities:</strong></p>
                                ${Object.keys(result.vulnerabilities).length > 0 ?
                                    '<ul>' + Object.entries(result.vulnerabilities).map(([issue, occurrences]) => 
                                        `<li class="text-danger">${issue}: ${occurrences.length} occurrence(s)</li>`
                                    ).join('') + '</ul>' :
                                    '<p class="text-success">No vulnerabilities detected</p>'
                                }
                                
                                <p><strong>DOM Clobbering:</strong></p>
                                ${result.dom_clobbering.length > 0 ?
                                    '<ul>' + result.dom_clobbering.map(issue => 
                                        `<li class="text-danger">${issue}</li>`
                                    ).join('') + '</ul>' :
                                    '<p class="text-success">No DOM clobbering issues detected</p>'
                                }
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
            
            // AST Results
            html += `<h4 class="mt-4">AST Analysis</h4>`;
            html += `<div class="accordion" id="astAccordion">`;
            
            results.js_ast_results.forEach((result, index) => {
                const fileId = `ast-file-${index}`;
                const vulnerabilityCount = result.vulnerabilities ? result.vulnerabilities.length : 0;
                
                html += `
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${fileId}">
                                ${result.file}
                                ${vulnerabilityCount > 0 ? `<span class="badge bg-danger ms-2">${vulnerabilityCount}</span>` : ''}
                            </button>
                        </h2>
                        <div id="${fileId}" class="accordion-collapse collapse" data-bs-parent="#astAccordion">
                            <div class="accordion-body">
                                <p><strong>Vulnerabilities:</strong></p>
                                ${result.vulnerabilities && result.vulnerabilities.length > 0 ?
                                    '<ul>' + result.vulnerabilities.map(vuln => 
                                        `<li class="text-danger">${vuln}</li>`
                                    ).join('') + '</ul>' :
                                    '<p class="text-success">No vulnerabilities detected</p>'
                                }
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
            
            html += '</div>';
            resultsContainer.innerHTML = html;
            
            // Initialize Bootstrap components
            const accordionElements = document.querySelectorAll('.accordion');
            accordionElements.forEach(accordion => {
                new bootstrap.Collapse(accordion);
            });
        }
    }
    
    // Download report
    downloadReportBtn.addEventListener('click', function() {
        if (!currentReport) return;
        
        let content, filename, type;
        
        if (currentReport.report) {
            // HTML or console report
            content = currentReport.report;
            filename = `dom-auditor-report.${currentReport.format === 'html' ? 'html' : 'txt'}`;
            type = currentReport.format === 'html' ? 'text/html' : 'text/plain';
        } else {
            // JSON report
            content = JSON.stringify(currentReport, null, 2);
            filename = 'dom-auditor-report.json';
            type = 'application/json';
        }
        
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
    
    // Show/hide config editor
    showConfigBtn.addEventListener('click', function() {
        configEditor.classList.toggle('d-none');
        if (!configEditor.classList.contains('d-none')) {
            loadConfig();
        }
    });
    
    // Save config
    saveConfigBtn.addEventListener('click', function() {
        try {
            const configData = JSON.parse(configText.value);
            saveConfig(configData);
        } catch (e) {
            alert('Invalid JSON configuration: ' + e.message);
        }
    });
    
    // Load config from server
    function loadConfig() {
        fetch('/config')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    configText.value = JSON.stringify(data.config, null, 2);
                    
                    // Pre-fill the form with config values
                    document.getElementById('directory').value = data.config.scan_directory || '';
                    document.getElementById('recursive').checked = data.config.recursive !== false;
                    
                    const formatSelect = document.getElementById('format');
                    if (data.config.output_format) {
                        for (let i = 0; i < formatSelect.options.length; i++) {
                            if (formatSelect.options[i].value === data.config.output_format) {
                                formatSelect.selectedIndex = i;
                                break;
                            }
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error loading config:', error);
            });
    }
    
    // Save config to server
    function saveConfig(configData) {
        fetch('/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Configuration saved successfully!');
                loadConfig(); // Reload to ensure we have the correct values
            } else {
                alert('Error saving configuration: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error saving configuration: ' + error.message);
        });
    }
    
    // Helper function to escape HTML
    function escapeHtml(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
});