// BookMyShoot JavaScript Functions

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
    }
    form.classList.add('was-validated');
}

// Show Toast Notification
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">BookMyShoot</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    toastContainer.innerHTML = toastHtml;
    document.body.appendChild(toastContainer);
    
    const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
    toast.show();
}

// Format Currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Format Date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

// Calculate Total Price
function calculateTotalPrice(basePrice, hourlyRate, hours) {
    return basePrice + (hourlyRate * hours);
}

// Confirm Action
function confirmAction(message) {
    return confirm(message || 'Are you sure?');
}

// Fetch Photographers
async function fetchPhotographers(categoryId) {
    try {
        const response = await fetch(`/booking/api/photographers/${categoryId}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching photographers:', error);
        return [];
    }
}

// Load Photographers into Select
function loadPhotographersToSelect(categoryId, selectId) {
    fetchPhotographers(categoryId).then(photographers => {
        const selectElement = document.getElementById(selectId);
        selectElement.innerHTML = '<option value="">Select a photographer</option>';
        
        photographers.forEach(photographer => {
            const option = document.createElement('option');
            option.value = photographer.id;
            option.textContent = `${photographer.full_name} (₹${photographer.hourly_rate}/hr)`;
            selectElement.appendChild(option);
        });
    });
}

// Date Range Validation
function validateDateRange(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    return start <= end;
}

// Check if Date is in Future
function isFutureDate(date) {
    return new Date(date) > new Date();
}

// Validate Email
function validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

// Validate Phone
function validatePhone(phone) {
    const pattern = /^[0-9]{10}$/;
    return pattern.test(phone.replace(/\D/g, ''));
}

// Copy to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Document Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add active class to current nav item
    const currentLocation = location.pathname;
    const navItems = document.querySelectorAll('nav a');
    navItems.forEach(item => {
        if (item.getAttribute('href') === currentLocation) {
            item.classList.add('active');
        }
    });

    // Real-time form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    });

    // Password show/hide toggle
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', function() {
            const targetSelector = this.getAttribute('data-target');
            const input = document.querySelector(targetSelector);
            if (!input) return;
            if (input.type === 'password') {
                input.type = 'text';
                this.querySelector('i').classList.remove('fa-eye');
                this.querySelector('i').classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                this.querySelector('i').classList.remove('fa-eye-slash');
                this.querySelector('i').classList.add('fa-eye');
            }
        });
    });
});

// AJAX Request Helper
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Logout with Confirmation
function confirmLogout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
}

// Set Active Navigation
function setActiveNav(linkText) {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.textContent.includes(linkText)) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Load More Pagination
function loadMore(page, container) {
    // Implementation depends on backend
    console.log(`Loading page ${page}`);
}

// Search Filter
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toUpperCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        let text = rows[i].textContent || rows[i].innerText;
        if (text.toUpperCase().indexOf(filter) > -1) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

// Export Table to CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cells = row.querySelectorAll('td, th');
        const rowData = Array.from(cells).map(cell => cell.textContent);
        csv.push(rowData.join(','));
    });

    const csvContent = 'data:text/csv;charset=utf-8,' + csv.join('\n');
    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csvContent));
    link.setAttribute('download', filename);
    link.click();
}

// Print Element
function printElement(elementId) {
    const printWindow = window.open('', '', 'width=600, height=700');
    const element = document.getElementById(elementId);
    printWindow.document.write(element.innerHTML);
    printWindow.document.close();
    printWindow.print();
}

// Initialize Charts (if using Chart.js)
function initializeCharts() {
    // Chart initialization code here
}

// Error Handler
function handleError(error) {
    console.error('Error:', error);
    showToast(`Error: ${error.message}`, 'danger');
}

// Success Handler
function handleSuccess(message) {
    showToast(message, 'success');
}
