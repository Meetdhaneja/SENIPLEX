// Admin Dashboard JavaScript

// Auto-refresh stats
function refreshStats() {
    fetch('/api/admin/stats')
        .then(response => response.json())
        .then(data => {
            console.log('Stats updated:', data);
        })
        .catch(error => console.error('Error fetching stats:', error));
}

// Refresh every 30 seconds
setInterval(refreshStats, 30000);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Admin dashboard loaded');
});
