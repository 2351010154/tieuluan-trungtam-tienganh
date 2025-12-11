document.addEventListener('DOMContentLoaded', function() {
    const revenueCtx = document.getElementById('revenueChart');
    const sourceCtx = document.getElementById('sourceChart');

    if (revenueCtx) {
        let dashboardChart = null;
        const initialData = window.revenueData || [0,0,0,0,0,0,0,0,0,0,0,0];

        dashboardChart = new Chart(revenueCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'],
                datasets: [{
                    label: 'Doanh thu',
                    data: initialData,
                    backgroundColor: '#1C4E64',
                    borderRadius: 0,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#E5E5E5', borderDash: [5, 5] },
                        ticks: { callback: function(value) { return value.toLocaleString('vi-VN'); } }
                    },
                    x: { grid: { display: true, color: '#f0f0f0' } }
                }
            }
        });

        const yearSelect = document.getElementById('yearSelect');
        const chartDesc = document.getElementById('chartYearDesc');

        if (yearSelect && dashboardChart) {
            yearSelect.addEventListener('change', function() {
                const selectedYear = this.value;

                if (chartDesc) {
                    chartDesc.innerText = `Diễn biến tài chính năm ${selectedYear}`;
                }

                fetch(`/api/chart-data?year=${selectedYear}`)
                    .then(response => response.json())
                    .then(newData => {
                        dashboardChart.data.datasets[0].data = newData;
                        dashboardChart.update();
                    })
                    .catch(err => console.error("Lỗi cập nhật Dashboard:", err));
            });
        }
    }

    if (sourceCtx) {
        const sourceFromDB = window.sourceData || [0, 0, 0];
        new Chart(sourceCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Beginner', 'Intermediate', 'Advanced'],
                datasets: [{
                    data: sourceFromDB,
                    backgroundColor: ['#3b82f6', '#f59e0b', '#ef4444'],
                    borderWidth: 0, hoverOffset: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '75%',
                plugins: { legend: { display: false } }
            }
        });
    }


    const detailChartCanvas = document.getElementById('detailChart');

        if (detailChartCanvas) {
        let myDetailChart = null;

        function updateReportChart() {
            // Lấy giá trị bộ lọc
            const type = document.getElementById('reportType').value;
            const year = document.getElementById('reportYear').value;
            const period = document.getElementById('reportPeriod').value;

            const titleLabel = document.getElementById('chartTitle');
            const btnFilter = document.getElementById('btnFilter');

            const originalBtnText = btnFilter.innerHTML;
            btnFilter.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tải...';
            btnFilter.disabled = true;

            const typeText = (type === 'revenue') ? 'Doanh thu' : 'Số lượng học viên';
            const periodText = (period === 'month') ? '' : '(Theo Quý)';
            titleLabel.textContent = `Biểu đồ ${typeText} năm ${year} ${periodText}`;

            fetch(`/api/stats?type=${type}&year=${year}&period=${period}`)
                .then(response => response.json())
                .then(res => {
                    const chartData = res.data;
                    const chartLabel = res.label;
                    const xLabels = res.labels;

                    if (myDetailChart) {
                        myDetailChart.destroy();
                    }

                    const barColor = (type === 'revenue') ? '#1C4E64' : '#2563eb';

                    myDetailChart = new Chart(detailChartCanvas.getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: xLabels,
                            datasets: [{
                                label: chartLabel,
                                data: chartData,
                                backgroundColor: barColor,
                                borderRadius: 4,
                                barPercentage: 0.6
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: true, position: 'top' },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            let label = context.dataset.label || '';
                                            if (label) { label += ': '; }
                                            if (context.parsed.y !== null) {
                                                if (type === 'revenue')
                                                    return label + context.parsed.y.toLocaleString('vi-VN') + ' VNĐ';
                                                return label + context.parsed.y + ' Học viên';
                                            }
                                            return label;
                                        }
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    grid: { color: '#f0f0f0' },
                                    ticks: {
                                        precision: 0,
                                        callback: function(value) {
                                            if (value % 1 === 0) {
                                                if (type === 'revenue') return value.toLocaleString('vi-VN');
                                                return value;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    });
                })
                .catch(err => console.error("Lỗi tải báo cáo:", err))
                .finally(() => {
                    btnFilter.innerHTML = originalBtnText;
                    btnFilter.disabled = false;
                });
        }

        const btnFilter = document.getElementById('btnFilter');
        if (btnFilter) {
            btnFilter.addEventListener('click', updateReportChart);
        }

        updateReportChart();
    }
});