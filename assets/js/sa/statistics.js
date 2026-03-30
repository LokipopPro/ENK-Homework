// 初始化页面
if (!initPage()) {
    // 未登录，已跳转到登录页面
    return;
}

let students = [];
let homeworkRecords = [];
let accuracyChart = null;
let typeChart = null;
let weeklyChart = null;
let completionChart = null;

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', async function() {
    try {
        // 加载学生列表
        await loadStudents();
        
        // 加载作业记录
        await loadHomeworkRecords();
        
        // 加载统计数据
        loadStats();
        
        // 加载图表
        loadCharts();
    } catch (error) {
        console.error('加载数据失败:', error);
        showToast('加载数据失败', 'danger');
    }
});

// 加载学生列表
async function loadStudents() {
    try {
        // 获取SA老师名下的学生
        students = await apiRequest('/students/my-students');
        
        // 填充学生下拉框
        const studentSelect = document.getElementById('studentSelect');
        if (studentSelect) {
            studentSelect.innerHTML = '<option value="">所有学生</option>';
            students.forEach(student => {
                const option = document.createElement('option');
                option.value = student.id;
                option.textContent = student.name;
                studentSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载学生列表失败:', error);
        throw error;
    }
}

// 加载作业记录
async function loadHomeworkRecords() {
    try {
        // 获取作业记录
        homeworkRecords = await apiRequest('/homework/records/my-records');
    } catch (error) {
        console.error('加载作业记录失败:', error);
        throw error;
    }
}

// 加载学生统计数据
async function loadStudentStats() {
    try {
        const studentId = document.getElementById('studentSelect').value;
        
        // 重新加载作业记录
        await loadHomeworkRecords();
        
        // 加载统计数据
        loadStats(studentId);
        
        // 加载图表
        loadCharts(studentId);
    } catch (error) {
        console.error('加载学生统计数据失败:', error);
        showToast('加载学生统计数据失败', 'danger');
    }
}

// 加载统计数据
function loadStats(studentId = '') {
    try {
        // 过滤作业记录
        let filteredRecords = homeworkRecords;
        if (studentId) {
            filteredRecords = homeworkRecords.filter(record => record.student_id == studentId);
        }
        
        // 计算统计数据
        const totalRecords = filteredRecords.length;
        const completedRecords = filteredRecords.filter(record => record.accuracy >= 60).length;
        const overdueRecords = filteredRecords.filter(record => record.is_overdue).length;
        const averageAccuracy = totalRecords > 0 ? 
            (filteredRecords.reduce((sum, record) => sum + record.accuracy, 0) / totalRecords).toFixed(2) : 0;
        
        // 更新统计卡片
        document.getElementById('totalRecords').textContent = totalRecords;
        document.getElementById('completedRecords').textContent = completedRecords;
        document.getElementById('averageAccuracy').textContent = averageAccuracy + '%';
        document.getElementById('overdueRecords').textContent = overdueRecords;
    } catch (error) {
        console.error('加载统计数据失败:', error);
        throw error;
    }
}

// 加载图表
function loadCharts(studentId = '') {
    try {
        // 过滤作业记录
        let filteredRecords = homeworkRecords;
        if (studentId) {
            filteredRecords = homeworkRecords.filter(record => record.student_id == studentId);
        }
        
        // 加载正确率趋势图
        loadAccuracyChart(filteredRecords);
        
        // 加载作业类型分布图
        loadTypeChart(filteredRecords);
        
        // 加载周完成情况图
        loadWeeklyChart(filteredRecords);
        
        // 加载完成率统计图
        loadCompletionChart(filteredRecords);
    } catch (error) {
        console.error('加载图表失败:', error);
        throw error;
    }
}

// 加载正确率趋势图
function loadAccuracyChart(records) {
    try {
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
        
        // 创建或更新图表
        const ctx = document.getElementById('accuracyChart').getContext('2d');
        if (accuracyChart) {
            accuracyChart.destroy();
        }
        
        accuracyChart = new Chart(ctx, {
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
        console.error('加载正确率趋势图失败:', error);
        throw error;
    }
}

// 加载作业类型分布图
function loadTypeChart(records) {
    try {
        // 按作业类型分组统计
        const typeData = {};
        
        records.forEach(record => {
            const typeName = record.homework_type_name;
            if (!typeData[typeName]) {
                typeData[typeName] = 0;
            }
            typeData[typeName]++;
        });
        
        // 转换为图表数据
        const labels = Object.keys(typeData);
        const data = Object.values(typeData);
        
        // 创建或更新图表
        const ctx = document.getElementById('typeChart').getContext('2d');
        if (typeChart) {
            typeChart.destroy();
        }
        
        typeChart = new Chart(ctx, {
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
        console.error('加载作业类型分布图失败:', error);
        throw error;
    }
}

// 加载周完成情况图
function loadWeeklyChart(records) {
    try {
        // 按周次分组统计完成情况
        const weeklyData = {};
        
        records.forEach(record => {
            const week = record.week_number;
            if (!weeklyData[week]) {
                weeklyData[week] = {
                    total: 0,
                    completed: 0
                };
            }
            weeklyData[week].total++;
            if (record.accuracy >= 60) {
                weeklyData[week].completed++;
            }
        });
        
        // 转换为图表数据
        const weeks = Object.keys(weeklyData).sort((a, b) => parseInt(a) - parseInt(b));
        const completedData = weeks.map(week => weeklyData[week].completed);
        const totalData = weeks.map(week => weeklyData[week].total);
        
        // 创建或更新图表
        const ctx = document.getElementById('weeklyChart').getContext('2d');
        if (weeklyChart) {
            weeklyChart.destroy();
        }
        
        weeklyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: weeks.map(week => `第${week}周`),
                datasets: [{
                    label: '已完成',
                    data: completedData,
                    backgroundColor: '#28a745'
                }, {
                    label: '未完成',
                    data: weeks.map((week, index) => totalData[index] - completedData[index]),
                    backgroundColor: '#dc3545'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '作业数'
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
        console.error('加载周完成情况图失败:', error);
        throw error;
    }
}

// 加载完成率统计图
function loadCompletionChart(records) {
    try {
        // 计算完成率
        const total = records.length;
        const completed = records.filter(record => record.accuracy >= 60).length;
        const completionRate = total > 0 ? (completed / total) * 100 : 0;
        
        // 创建或更新图表
        const ctx = document.getElementById('completionChart').getContext('2d');
        if (completionChart) {
            completionChart.destroy();
        }
        
        completionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['已完成', '未完成'],
                datasets: [{
                    data: [completed, total - completed],
                    backgroundColor: ['#28a745', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: `总完成率: ${completionRate.toFixed(2)}%`
                    }
                }
            }
        });
    } catch (error) {
        console.error('加载完成率统计图失败:', error);
        throw error;
    }
}