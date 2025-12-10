document.addEventListener('DOMContentLoaded', function() {

    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        const dataFromDB = window.revenueData || [0,0,0,0,0,0,0,0,0,0,0,0];

        new Chart(revenueCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'],
                datasets: [{
                    label: 'Doanh thu',

                    data: dataFromDB,

                    backgroundColor: '#3b82f6',
                    borderRadius: 0,
                    barPercentage: 0.6,
                    categoryPercentage: 0.8
                }]
            },
        });
    }

    const sourceCtx = document.getElementById('sourceChart');
    if (sourceCtx) {
        const sourceFromDB = window.sourceData || [0, 0, 0];

        new Chart(sourceCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Beginner', 'Intermediate', 'Advanced'],
                datasets: [{

                    data: sourceFromDB,

                    backgroundColor: [
                        '#3b82f6',
                        '#f59e0b',
                        '#ef4444'
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
        });
    }
});