document.addEventListener("DOMContentLoaded", () => {
    
    // Global chart configurations
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Outfit', sans-serif";
    
    // Initialize gauges
    const cpuCtx = document.getElementById('cpuChart').getContext('2d');
    const memCtx = document.getElementById('memoryChart').getContext('2d');
    
    const createGauge = (ctx, color) => {
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [0, 100],
                    backgroundColor: [color, 'rgba(255, 255, 255, 0.1)'],
                    borderWidth: 0,
                    circumference: 270,
                    rotation: 225,
                    cutout: '80%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { tooltip: { enabled: false } },
                animation: { duration: 500, easing: 'easeOutQuart' }
            }
        });
    };

    const cpuChart = createGauge(cpuCtx, '#3b82f6');
    const memoryChart = createGauge(memCtx, '#8b5cf6');

    // Fetch System Metrics (Real-time)
    const updateMetrics = async () => {
        try {
            const res = await fetch('/api/system');
            const data = await res.json();
            
            // Update CPU
            document.getElementById('cpu-value').textContent = `${Math.round(data.cpu)}%`;
            cpuChart.data.datasets[0].data = [data.cpu, 100 - data.cpu];
            cpuChart.update();
            
            // Update Memory
            document.getElementById('memory-value').textContent = `${Math.round(data.memory)}%`;
            memoryChart.data.datasets[0].data = [data.memory, 100 - data.memory];
            memoryChart.update();
        } catch (e) {
            console.error('Error fetching system metrics:', e);
        }
    };

    // Update every 2 seconds
    setInterval(updateMetrics, 2000);
    updateMetrics();

    // Fetch Analytics Data
    const loadAnalytics = async () => {
        try {
            const res = await fetch('/api/analytics');
            const data = await res.json();

            // Update Summary Cards
            document.getElementById('total-commands').textContent = data.total_commands;
            document.getElementById('total-commits').textContent = data.total_commits;
            document.getElementById('total-files').textContent = data.total_file_changes;

            // Render Activity Chart
            const activityCtx = document.getElementById('activityChart').getContext('2d');
            
            const dates = data.daily_stats.map(d => {
                const date = new Date(d.date);
                return `${date.getMonth()+1}/${date.getDate()}`;
            });
            const counts = data.daily_stats.map(d => d.count);

            new Chart(activityCtx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Commands Executed',
                        data: counts,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#8b5cf6',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: '#8b5cf6',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });

            // Populate Table — latest 5 only
            const tbody = document.getElementById('activity-body');
            tbody.innerHTML = '';
            
            const latest5 = data.recent_activity.slice(0, 5);
            latest5.forEach(activity => {
                const tr = document.createElement('tr');
                
                const date = new Date(activity.timestamp);
                const timeStr = date.toLocaleString();
                
                tr.innerHTML = `
                    <td>${timeStr}</td>
                    <td><span class="type-badge">${activity.type.replace('_', ' ')}</span></td>
                    <td><code>${activity.command}</code></td>
                `;
                tbody.appendChild(tr);
            });

        } catch (e) {
            console.error('Error fetching analytics:', e);
        }
    };

    loadAnalytics();
});
