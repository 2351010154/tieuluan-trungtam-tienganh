document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('myChart').getContext('2d');

    const dataValues = [170, 130, 350, 280, 320, 360];
    const labels = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6'];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Doanh thu',
                data: dataValues,
                backgroundColor: '#1C4E64',
                borderRadius: 0,
                barPercentage: 0.7,
                categoryPercentage: 0.8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 400,
                    ticks: {
                        stepSize: 100,
                        font: { size: 12 },
                        color: '#666'
                    },
                    grid: {
                        color: '#E5E5E5',
                    },
                    border: { display: false }
                },
                x: {
                    grid: {
                        display: true,
                        color: '#E5E5E5'
                    },
                    ticks: {
                        font: { size: 12 },
                        color: '#666',
                        padding: 10
                    },
                    border: { display: false }
                }
            }
        }
    });
});

function updateChart() {
    alert("Đang tải dữ liệu mới...");
}