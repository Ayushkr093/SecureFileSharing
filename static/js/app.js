// App Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// App State
let currentUser = null;
let currentUserType = 'client';
let authToken = localStorage.getItem('authToken');
let selectedFile = null; // Store the selected file globally

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    
    // Check if user is already logged in
    if (authToken) {
        const userType = localStorage.getItem('userType');
        if (userType === 'ops') {
            showOpsDashboard();
        } else if (userType === 'client') {
            showClientDashboard();
        }
    }
});

// Initialize App
function initializeApp() {
    showPage('landingPage');
}

// Setup Event Listeners
function setupEventListeners() {
    // Login Form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Signup Form
    document.getElementById('signupForm').addEventListener('submit', handleSignup);
    
    // Verification Form
    document.getElementById('verificationForm').addEventListener('submit', handleVerification);
    
    // Upload Form
    document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
    
    // File Input
    const fileInput = document.getElementById('fileInput');
    const fileUploadArea = document.getElementById('fileUploadArea');
    
    console.log('🔧 Initializing file upload components');
    console.log('File input element:', fileInput);
    console.log('File upload area element:', fileUploadArea);
    
    if (!fileInput || !fileUploadArea) {
        console.error('❌ Failed to find upload elements!');
        return;
    }
    
    fileUploadArea.addEventListener('click', () => {
        console.log('📁 Upload area clicked, triggering file input');
        fileInput.click();
    });
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and Drop
    fileUploadArea.addEventListener('dragover', handleDragOver);
    fileUploadArea.addEventListener('dragleave', handleDragLeave);
    fileUploadArea.addEventListener('drop', handleFileDrop);
}

// Navigation Functions
function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    document.getElementById(pageId).classList.add('active');
}

function showLogin() {
    showPage('loginPage');
    updateNavigation(false);
}

function showSignup() {
    showPage('signupPage');
    updateNavigation(false);
}

function showVerification() {
    showPage('verificationPage');
}

function showOpsDashboard() {
    showPage('opsDashboard');
    updateNavigation(true);
    loadOpsFiles();
}

function showClientDashboard() {
    showPage('clientDashboard');
    updateNavigation(true);
    loadClientFiles();
}

function updateNavigation(isLoggedIn) {
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (isLoggedIn) {
        loginBtn.style.display = 'none';
        signupBtn.style.display = 'none';
        logoutBtn.style.display = 'block';
    } else {
        loginBtn.style.display = 'block';
        signupBtn.style.display = 'block';
        logoutBtn.style.display = 'none';
    }
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userType');
    authToken = null;
    currentUser = null;
    showPage('landingPage');
    updateNavigation(false);
    showToast('Logged out successfully', 'success');
}

// User Type Selection
function selectUserType(type) {
    currentUserType = type;
    document.querySelectorAll('.user-type-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-type="${type}"]`).classList.add('active');
}

// Authentication Functions
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    console.log('🔐 Login attempt:', currentUserType, email);
    
    showLoading(true);
    
    try {
        const endpoint = currentUserType === 'ops' ? '/auth/ops/login' : '/auth/client/login';
        console.log('📡 Login endpoint:', `${API_BASE_URL}${endpoint}`);
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        console.log('📥 Login response:', response.status, data);
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('userType', currentUserType);
            
            console.log('✅ Login successful, token stored:', authToken ? 'Yes' : 'No');
            
            showToast(data.message, 'success');
            
            if (currentUserType === 'ops') {
                showOpsDashboard();
            } else {
                showClientDashboard();
            }
        } else {
            console.log('❌ Login failed:', data.message);
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('❌ Login error:', error);
        showToast('Login failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleSignup(e) {
    e.preventDefault();
    
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/client/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Account created! Please check your email for verification.', 'success');
            showVerification();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Signup failed. Please try again.', 'error');
        console.error('Signup error:', error);
    } finally {
        showLoading(false);
    }
}

async function handleVerification(e) {
    e.preventDefault();
    
    const token = document.getElementById('verificationToken').value;
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/client/verify-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Email verified successfully! You can now login.', 'success');
            showLogin();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Verification failed. Please try again.', 'error');
        console.error('Verification error:', error);
    } finally {
        showLoading(false);
    }
}

// File Upload Functions
function handleFileSelect(e) {
    console.log('📁 File selection event triggered');
    const file = e.target.files[0];
    console.log('📁 Selected file:', file);
    console.log('📁 Input files count:', e.target.files.length);
    
    if (file) {
        selectedFile = file; // Store globally
        console.log('📁 File stored globally:', selectedFile);
        updateFileUploadUI(file);
    } else {
        selectedFile = null;
        console.log('❌ No file found in selection event');
    }
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    console.log('📁 Files dropped:', files.length);
    
    if (files.length > 0) {
        const file = files[0];
        console.log('📁 Processing dropped file:', file.name);
        
        // Store the file globally
        selectedFile = file;
        console.log('📁 File stored globally from drop:', selectedFile);
        
        // Create a new FileList-like object and assign to the input
        const fileInput = document.getElementById('fileInput');
        try {
            // Use DataTransfer to properly set the files
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
            console.log('📁 File assigned to input, files count:', fileInput.files.length);
        } catch (error) {
            console.error('❌ Error assigning file to input:', error);
        }
        
        updateFileUploadUI(file);
    }
}

function updateFileUploadUI(file) {
    const uploadArea = document.getElementById('fileUploadArea');
    const uploadBtn = document.getElementById('uploadBtn');
    
    if (isValidFileType(file)) {
        uploadArea.innerHTML = `
            <i class="fas fa-file-check"></i>
            <p><strong>${file.name}</strong></p>
            <p class="file-types">Size: ${formatFileSize(file.size)}</p>
        `;
        uploadBtn.disabled = false;
    } else {
        showToast('Invalid file type. Please upload .pptx, .docx, or .xlsx files only.', 'error');
        uploadBtn.disabled = true;
    }
}

function isValidFileType(file) {
    const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.presentationml.presentation', // .pptx
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',   // .docx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'          // .xlsx
    ];
    
    const allowedExtensions = ['pptx', 'docx', 'xlsx'];
    const extension = file.name.split('.').pop().toLowerCase();
    
    return allowedTypes.includes(file.type) || allowedExtensions.includes(extension);
}

async function handleFileUpload(e) {
    e.preventDefault();
    
    console.log('🔧 File upload started');
    console.log('Auth token:', authToken);
    console.log('Selected file from global storage:', selectedFile);
    
    // Use the globally stored file instead of trying to find the input element
    if (!selectedFile) {
        console.error('❌ No file selected');
        showToast('Please select a file to upload', 'error');
        return;
    }
    
    console.log('✅ Using stored file:', selectedFile.name, 'Size:', selectedFile.size);
    
    if (!isValidFileType(selectedFile)) {
        console.log('❌ Invalid file type:', selectedFile.type, selectedFile.name);
        showToast('Invalid file type. Please upload .pptx, .docx, or .xlsx files only.', 'error');
        return;
    }
    
    console.log('✅ File validation passed');
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        console.log('📡 Sending upload request to:', `${API_BASE_URL}/ops/upload`);
        console.log('Authorization header:', `Bearer ${authToken}`);
        
        const response = await fetch(`${API_BASE_URL}/ops/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
            body: formData,
        });
        
        console.log('📥 Upload response status:', response.status);
        
        const data = await response.json();
        console.log('📥 Upload response data:', data);
        
        if (response.ok) {
            showToast('File uploaded successfully!', 'success');
            resetUploadForm();
            loadOpsFiles();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('❌ Upload error:', error);
        showToast('Upload failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

function resetUploadForm() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('fileUploadArea');
    const uploadBtn = document.getElementById('uploadBtn');
    
    // Clear global file storage
    selectedFile = null;
    console.log('🔄 Upload form reset, cleared selected file');
    
    if (fileInput) fileInput.value = '';
    if (uploadBtn) uploadBtn.disabled = true;
    
    if (uploadArea) {
        uploadArea.innerHTML = `
            <i class="fas fa-file-upload"></i>
            <p>Drag and drop files here or click to browse</p>
            <p class="file-types">Supported: .pptx, .docx, .xlsx</p>
        `;
    }
}

// File Loading Functions
async function loadOpsFiles() {
    try {
        const response = await fetch(`${API_BASE_URL}/client/files`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayOpsFiles(data.files);
        }
    } catch (error) {
        console.error('Error loading ops files:', error);
    }
}

async function loadClientFiles() {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/client/files`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayClientFiles(data.files);
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Failed to load files', 'error');
        console.error('Error loading client files:', error);
    } finally {
        showLoading(false);
    }
}

function displayOpsFiles(files) {
    const container = document.getElementById('opsFilesList');
    
    if (files.length === 0) {
        container.innerHTML = '<p>No files uploaded yet.</p>';
        return;
    }
    
    container.innerHTML = files.slice(0, 5).map(file => `
        <div class="file-item">
            <div class="file-info">
                <i class="fas ${getFileIcon(file.file_type)} file-icon"></i>
                <div class="file-details">
                    <h4>${file.original_filename}</h4>
                    <p>Size: ${formatFileSize(file.file_size)} • Uploaded: ${formatDate(file.uploaded_at)}</p>
                </div>
            </div>
        </div>
    `).join('');
}

function displayClientFiles(files) {
    const container = document.getElementById('clientFilesList');
    
    if (files.length === 0) {
        container.innerHTML = '<div class="file-item"><p>No files available for download.</p></div>';
        return;
    }
    
    container.innerHTML = files.map(file => `
        <div class="file-item">
            <div class="file-info">
                <i class="fas ${getFileIcon(file.file_type)} file-icon"></i>
                <div class="file-details">
                    <h4>${file.original_filename}</h4>
                    <p>Size: ${formatFileSize(file.file_size)}</p>
                    <p>Uploaded by: ${file.uploaded_by}</p>
                    <p>Date: ${formatDate(file.uploaded_at)}</p>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn primary small" onclick="generateDownloadLink(${file.id})">
                    <i class="fas fa-download"></i> Download
                </button>
            </div>
        </div>
    `).join('');
}

async function generateDownloadLink(fileId) {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/client/download-file/${fileId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Trigger download
            window.open(data['download-link'], '_blank');
            showToast('Download started!', 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Failed to generate download link', 'error');
        console.error('Download error:', error);
    } finally {
        showLoading(false);
    }
}

// Utility Functions
function getFileIcon(fileType) {
    switch (fileType.toLowerCase()) {
        case 'pptx':
            return 'fa-file-powerpoint';
        case 'docx':
            return 'fa-file-word';
        case 'xlsx':
            return 'fa-file-excel';
        default:
            return 'fa-file';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// UI Helper Functions
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.add('show');
    } else {
        overlay.classList.remove('show');
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const icon = toast.querySelector('.toast-icon');
    const messageEl = toast.querySelector('.toast-message');
    
    // Set icon based on type
    let iconClass = 'fas fa-info-circle';
    if (type === 'success') {
        iconClass = 'fas fa-check-circle';
    } else if (type === 'error') {
        iconClass = 'fas fa-exclamation-circle';
    }
    
    icon.className = `toast-icon ${iconClass}`;
    messageEl.textContent = message;
    
    // Reset classes and add type
    toast.className = `toast ${type}`;
    
    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Hide toast after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 5000);
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Application error:', e.error);
    showToast('An unexpected error occurred', 'error');
});

// Prevent form submission on Enter key for file inputs
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.type === 'file') {
        e.preventDefault();
    }
});
