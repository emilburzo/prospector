const API_BASE = '/api';

// Toast notification system
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || icons.info}</div>
        <div class="toast-content">${message}</div>
        <button class="toast-close" onclick="closeToast(this)">×</button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function closeToast(button) {
    const toast = button.closest('.toast');
    toast.classList.add('hiding');
    setTimeout(() => toast.remove(), 300);
}

// Form toggle
function toggleForm(formId) {
    const form = document.getElementById(formId);
    if (form.classList.contains('collapsed')) {
        form.classList.remove('collapsed');
        form.classList.add('expanded');
    } else {
        form.classList.add('collapsed');
        form.classList.remove('expanded');
    }
}

// Tab switching with localStorage persistence
function switchTab(tabName, event) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        document.querySelectorAll('.tab').forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            }
        });
    }
    
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Save to localStorage
    localStorage.setItem('activeTab', tabName);
    
    // Load data for the active tab
    if (tabName === 'applications') loadApplications();
    if (tabName === 'leads') loadLeads();
    if (tabName === 'resume') loadActiveResume();
}

// Restore active tab on page load
window.addEventListener('DOMContentLoaded', () => {
    const savedTab = localStorage.getItem('activeTab') || 'applications';
    switchTab(savedTab);
});

// Job Applications
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('application-form-element').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data = {
            company_name: document.getElementById('app-company').value,
            role_name: document.getElementById('app-role').value,
            stage: document.getElementById('app-stage').value,
            job_ad: document.getElementById('app-job-ad').value,
            notes: document.getElementById('app-notes').value,
            job_match_percentage: parseFloat(document.getElementById('app-match').value) || null
        };
        
        try {
            const response = await fetch(`${API_BASE}/applications/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showToast('Application added successfully!', 'success');
                e.target.reset();
                toggleForm('application-form');
                loadApplications();
            } else {
                showToast('Failed to add application', 'error');
            }
        } catch (error) {
            showToast('Error: ' + error.message, 'error');
        }
    });
});

async function loadApplications() {
    const stageFilter = document.getElementById('stage-filter').value;
    const url = stageFilter 
        ? `${API_BASE}/applications/?stage=${stageFilter}`
        : `${API_BASE}/applications/`;
    
    try {
        const response = await fetch(url);
        const applications = await response.json();
        
        const container = document.getElementById('applications-list');
        
        if (applications.length === 0) {
            container.innerHTML = '<div class="empty-state"><h3>No applications yet</h3><p>Click "+ Add Application" to get started</p></div>';
            return;
        }
        
        container.innerHTML = '<div class="card-grid">' + applications.map(app => `
            <div class="job-card">
                <h4>${app.role_name}</h4>
                <div class="company">${app.company_name}</div>
                <span class="stage ${app.stage}">${app.stage.replace('_', ' ').toUpperCase()}</span>
                ${app.job_match_percentage ? `<div class="match-percentage ${getMatchClass(app.job_match_percentage)}">${app.job_match_percentage.toFixed(1)}% Match</div>` : ''}
                ${app.notes ? `<p><strong>Notes:</strong> ${app.notes.substring(0, 100)}${app.notes.length > 100 ? '...' : ''}</p>` : ''}
                <div class="actions">
                    <button onclick="deleteApplication(${app.id})" class="danger">Delete</button>
                </div>
            </div>
        `).join('') + '</div>';
    } catch (error) {
        console.error('Error loading applications:', error);
        showToast('Failed to load applications', 'error');
    }
}

async function deleteApplication(id) {
    if (!confirm('Are you sure you want to delete this application?')) return;
    
    try {
        await fetch(`${API_BASE}/applications/${id}`, { method: 'DELETE' });
        showToast('Application deleted', 'success');
        loadApplications();
    } catch (error) {
        showToast('Error deleting application', 'error');
    }
}

// Job Leads
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('lead-form-element').addEventListener('submit', (e) => {
        e.preventDefault();
        submitLead(true);
    });
});

async function submitLead(rankImmediately) {
    const data = {
        company_name: document.getElementById('lead-company').value,
        role_name: document.getElementById('lead-role').value,
        job_posting: document.getElementById('lead-posting').value,
        source: document.getElementById('lead-source').value,
        url: document.getElementById('lead-url').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/leads/?rank_immediately=${rankImmediately}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showToast(rankImmediately ? 'Job lead added and ranked!' : 'Job lead added successfully!', 'success');
            document.getElementById('lead-form-element').reset();
            toggleForm('lead-form');
            loadLeads();
        } else {
            showToast('Failed to add job lead', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

async function loadLeads() {
    const sortByMatch = document.getElementById('sort-by-match').checked;
    
    try {
        const response = await fetch(`${API_BASE}/leads/?sort_by_match=${sortByMatch}`);
        const leads = await response.json();
        
        const container = document.getElementById('leads-list');
        
        if (leads.length === 0) {
            container.innerHTML = '<div class="empty-state"><h3>No job leads yet</h3><p>Click "+ Add Lead" to get started</p></div>';
            return;
        }
        
        container.innerHTML = '<div class="card-grid">' + leads.map(lead => `
            <div class="job-card">
                <h4>${lead.role_name}</h4>
                <div class="company">${lead.company_name}</div>
                ${lead.match_percentage !== null && lead.match_percentage !== undefined ? `
                    <div class="match-percentage ${getMatchClass(lead.match_percentage)}">${lead.match_percentage.toFixed(1)}% Match</div>
                    ${lead.match_reasoning ? `<p><small>${lead.match_reasoning.substring(0, 150)}...</small></p>` : ''}
                ` : '<p><em>Not yet ranked</em></p>'}
                ${lead.source ? `<p><strong>Source:</strong> ${lead.source}</p>` : ''}
                <div class="actions">
                    ${lead.match_percentage === null || lead.match_percentage === undefined ? `<button onclick="rankLead(${lead.id})">Rank</button>` : ''}
                    <button onclick="promoteLead(${lead.id})" class="secondary">Promote</button>
                    <button onclick="deleteLead(${lead.id})" class="danger">Delete</button>
                </div>
            </div>
        `).join('') + '</div>';
    } catch (error) {
        console.error('Error loading leads:', error);
        showToast('Failed to load leads', 'error');
    }
}

async function rankLead(id) {
    try {
        showToast('Ranking job lead...', 'info');
        const response = await fetch(`${API_BASE}/leads/${id}/rank`, { method: 'POST' });
        if (response.ok) {
            showToast('Lead ranked successfully!', 'success');
            loadLeads();
        } else {
            const error = await response.json();
            showToast('Failed to rank lead: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        showToast('Error ranking lead: ' + error.message, 'error');
    }
}

async function promoteLead(id) {
    if (!confirm('Promote this lead to a job application?')) return;
    
    try {
        showToast('Promoting lead...', 'info');
        const response = await fetch(`${API_BASE}/leads/${id}/promote`, { method: 'POST' });
        if (response.ok) {
            showToast('Lead promoted successfully!', 'success');
            loadLeads();
        } else {
            showToast('Failed to promote lead', 'error');
        }
    } catch (error) {
        showToast('Error promoting lead: ' + error.message, 'error');
    }
}

async function deleteLead(id) {
    if (!confirm('Are you sure you want to delete this lead?')) return;
    
    try {
        await fetch(`${API_BASE}/leads/${id}`, { method: 'DELETE' });
        showToast('Lead deleted', 'success');
        loadLeads();
    } catch (error) {
        showToast('Error deleting lead', 'error');
    }
}

// Resume
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('resume-form-element').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data = {
            content: document.getElementById('resume-content').value,
            filename: document.getElementById('resume-filename').value || null
        };
        
        try {
            const response = await fetch(`${API_BASE}/resumes/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showToast('Resume saved successfully!', 'success');
                e.target.reset();
                toggleForm('resume-form');
                loadActiveResume();
            } else {
                showToast('Failed to save resume', 'error');
            }
        } catch (error) {
            showToast('Error: ' + error.message, 'error');
        }
    });
});

async function loadActiveResume() {
    try {
        const response = await fetch(`${API_BASE}/resumes/active`);
        const container = document.getElementById('active-resume-display');
        
        if (response.ok) {
            const resume = await response.json();
            container.innerHTML = `
                <div class="card">
                    <h3>Active Resume</h3>
                    ${resume.filename ? `<p><strong>Filename:</strong> ${resume.filename}</p>` : ''}
                    <p><strong>Created:</strong> ${new Date(resume.created_at).toLocaleDateString()}</p>
                    <p><strong>Content Preview:</strong></p>
                    <pre style="background: #252525; padding: 1rem; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; color: #e0e0e0;">${resume.content.substring(0, 500)}${resume.content.length > 500 ? '...' : ''}</pre>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><h3>No active resume</h3><p>Click "+ Add Resume" to upload your resume and start ranking job leads</p></div>';
        }
    } catch (error) {
        console.error('Error loading resume:', error);
        document.getElementById('active-resume-display').innerHTML = '<div class="empty-state"><h3>No active resume</h3><p>Click "+ Add Resume" to upload your resume and start ranking job leads</p></div>';
    }
}

function getMatchClass(percentage) {
    if (percentage >= 70) return 'match-high';
    if (percentage >= 40) return 'match-medium';
    return 'match-low';
}
