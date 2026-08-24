// Global JavaScript helper functions for Personal Finance Analyzer

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Helper for rendering Chart.js Expense Doughnut Chart
function renderExpenseChart(canvasId, chartData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !chartData || !chartData.labels || chartData.labels.length === 0) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: [
                    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 
                    '#8b5cf6', '#ec4899', '#06b6d4', '#64748b', '#d97706'
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Helper for rendering Chart.js Monthly Income vs Expenses Bar/Line Chart
function renderMonthlyChart(canvasId, chartData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !chartData || !chartData.labels || chartData.labels.length === 0) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Income ($)',
                    data: chartData.income_data,
                    backgroundColor: '#10b981',
                    borderRadius: 4
                },
                {
                    label: 'Expenses ($)',
                    data: chartData.expense_data,
                    backgroundColor: '#ef4444',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) { return '$' + value; }
                    }
                }
            }
        }
    });
}

// Helper for rendering Savings Trend Line Chart
function renderSavingsTrendChart(canvasId, chartData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !chartData || !chartData.labels || chartData.labels.length === 0) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Cumulative Savings ($)',
                data: chartData.data,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) { return '$' + value; }
                    }
                }
            }
        }
    });
}
