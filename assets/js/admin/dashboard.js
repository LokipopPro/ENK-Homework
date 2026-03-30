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
        
        // 获取SA老师统计数据
        const saStats = await apiRequest('/statistics/sa');
        document.getElementById('totalSA').textContent = saStats.length;
        
        // 计算总作业记录数和逾期记录数
        let totalRecords = 0;
        let overdueRecords = 0;
        
        studentStats.forEach(stat => {
            totalRecords += stat.total_records;
            overdueRecords += stat.overdue_records;
        });
        
        document.getElementById('totalRecords').textContent = totalRecords;
        document.getElementById('overdueRecords').textContent = overdueRecords;
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
        
        // 加载作业类型分布图表
        await loadTypeChart();
    } catch (error) {
        console.error('加载图表失败:', error);
        throw error;
    }
}

// 加载学生正确率趋势图表
async function loadAccuracyChart() {
    try {
        // 获取作业记录数据
        const records = await apiRequest('/homework/records');
        
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

// 加载作业类型分布图表
async function loadTypeChart() {
    try {
        // 获取作业类型数据
        const types = await apiRequest('/homework/types');
        
        // 获取作业记录数据
        const records = await apiRequest('/homework/records');
        
        // 按作业类型分组统计
        const typeData = {};
        
        types.forEach(type => {
            typeData[type.id] = {
                name: type.name,
                count: 0
            };
        });
        
        records.forEach(record => {
            if (typeData[record.homework_type_id]) {
                typeData[record.homework_type_id].count++;
            }
        });
        
        // 转换为图表数据
        const labels = Object.values(typeData).map(item => item.name);
        const data = Object.values(typeData).map(item => item.count);
        
        // 创建图表
        const ctx = document.getElementById('typeChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#0d6efd',
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#6f42c1',
                        '#fd7e14'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    } catch (error) {
        console.error('加载作业类型分布图表失败:', error);
        throw error;
    }
}

// 加载最近作业记录
async function loadRecentRecords() {
    try {
        // 获取最近的作业记录
        const records = await apiRequest('/homework/records');
        
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
                    <span class="badge ${isOverdue ? 'bg-danger' : 'bg-success'}">
                        ${isOverdue ? '逾期' : '正常'}
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