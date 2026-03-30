// 初始化页面
if (!initPage()) {
    // 未登录，已跳转到登录页面
    return;
}

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', async function() {
    try {
        // 加载统计数据
        await loadStatistics();
        
        // 加载图表
        await loadCharts();
        
        // 加载最近作业记录
        await loadRecentRecords();
    } catch (error) {
        console.error('加载数据失败:', error);
        showToast('加载数据失败', 'danger');
    }
});

// 加载统计数据
async function loadStatistics() {
    try {
        // 获取学生统计数据
        const studentStats = await apiRequest('/statistics/students');
        document.getElementById('totalStudents').textContent = studentStats.length;
        
        // 计算总作业记录数和平均正确率
        let totalRecords = 0;
        let totalAccuracy = 0;
        let recordCount = 0;
        
        studentStats.forEach(stat => {
            totalRecords += stat.total_records;
            if (stat.average_accuracy) {
                totalAccuracy += stat.average_accuracy;
                recordCount++;
            }
        });
        
        document.getElementById('totalRecords').textContent = totalRecords;
        
        const averageAccuracy = recordCount > 0 ? (totalAccuracy / recordCount).toFixed(2) : 0;
        document.getElementById('averageAccuracy').textContent = averageAccuracy + '%';
    } catch (error) {
        console.error('加载统计数据失败:', error);
        throw error;
    }
}

// 加载图表
async function loadCharts() {
    try {
        // 加载学生正确率趋势图表
        await loadAccuracyChart();
        
        // 加载作业完成情况图表
        await loadCompletionChart();
    } catch (error) {
        console.error('加载图表失败:', error);
        throw error;
    }
}

// 加载学生正确率趋势图表
async function loadAccuracyChart() {
    try {
        // 获取作业记录数据
        const records = await apiRequest('/homework/records/my-records');
        
        // 按周次分组计算平均正确率
        const weeklyData = {};
        
        records.forEach(record => {
            const week = record.week_number;
            if (!weeklyData[week]) {
                weeklyData[week] = {
                    total: 0,
                    sum: 0
                };
            }
            weeklyData[week].total++;
            weeklyData[week].sum += record.accuracy;
        });
        
        // 转换为图表数据
        const weeks = Object.keys(weeklyData).sort((a, b) => parseInt(a) - parseInt(b));
        const accuracies = weeks.map(week => {
            const data = weeklyData[week];
            return data.sum / data.total;
        });
        
        // 创建图表
        const ctx = document.getElementById('accuracyChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: weeks.map(week => `第${week}周`),
                datasets: [{
                    label: '平均正确率',
                    data: accuracies,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: '正确率 (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '周次'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('加载正确率趋势图表失败:', error);
        throw error;
    }
}

// 加载作业完成情况图表
async function loadCompletionChart() {
    try {
        // 获取作业记录数据
        const records = await apiRequest('/homework/records/my-records');
        
        // 统计完成和未完成的作业
        let completed = 0;
        let notCompleted = 0;
        let overdue = 0;
        
        records.forEach(record => {
            if (record.accuracy >= 60) {
                completed++;
            } else {
                notCompleted++;
            }
            if (record.is_overdue) {
                overdue++;
            }
        });
        
        // 创建图表
        const ctx = document.getElementById('completionChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['已完成', '未完成', '逾期'],
                datasets: [{
                    data: [completed, notCompleted, overdue],
                    backgroundColor: [
                        '#28a745',
                        '#ffc107',
                        '#dc3545'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    } catch (error) {
        console.error('加载作业完成情况图表失败:', error);
        throw error;
    }
}

// 加载最近作业记录
async function loadRecentRecords() {
    try {
        // 获取最近的作业记录
        const records = await apiRequest('/homework/records/my-records');
        
        // 按批改日期排序，取最近10条
        records.sort((a, b) => new Date(b.grading_date) - new Date(a.grading_date));
        const recentRecords = records.slice(0, 10);
        
        // 填充表格
        const tbody = document.getElementById('recentRecordsBody');
        tbody.innerHTML = '';
        
        recentRecords.forEach(record => {
            const row = document.createElement('tr');
            
            // 检查是否逾期
            const isOverdue = checkOverdue(record.grading_date);
            if (isOverdue) {
                row.classList.add('overdue');
            }
            
            row.innerHTML = `
                <td>${record.student_name}</td>
                <td>${record.homework_type_name}</td>
                <td>${record.week_number}</td>
                <td>${record.accuracy}%</td>
                <td>${formatDate(record.grading_date)}</td>
                <td>
                    <span class="badge ${isOverdue ? 'bg-danger' : (record.accuracy >= 60 ? 'bg-success' : 'bg-warning')}">
                        ${isOverdue ? '逾期' : (record.accuracy >= 60 ? '已完成' : '未完成')}
                    </span>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('加载最近作业记录失败:', error);
        throw error;
    }
}