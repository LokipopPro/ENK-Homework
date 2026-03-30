// 初始化页面
if (!initPage()) {
    // 未登录，已跳转到登录页面
    return;
}

let homeworkRecords = [];
let students = [];
let homeworkTypes = [];
let homeworkCycles = [];

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', async function() {
    try {
        // 加载学生列表
        await loadStudents();
        
        // 加载作业类型
        await loadHomeworkTypes();
        
        // 加载作业周期
        await loadHomeworkCycles();
        
        // 加载作业记录
        await loadHomeworkRecords();
        
        // 设置默认日期为今天
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('homeworkDate').value = today;
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
        const studentSelects = [
            document.getElementById('homeworkStudent'),
            document.getElementById('editHomeworkStudent')
        ];
        
        studentSelects.forEach(select => {
            if (select) {
                select.innerHTML = '';
                students.forEach(student => {
                    const option = document.createElement('option');
                    option.value = student.id;
                    option.textContent = student.name;
                    select.appendChild(option);
                });
            }
        });
    } catch (error) {
        console.error('加载学生列表失败:', error);
        throw error;
    }
}

// 加载作业类型
async function loadHomeworkTypes() {
    try {
        homeworkTypes = await apiRequest('/homework/types');
        
        // 填充作业类型下拉框
        const typeSelects = [
            document.getElementById('homeworkType'),
            document.getElementById('editHomeworkType'),
            document.getElementById('typeFilter')
        ];
        
        typeSelects.forEach(select => {
            if (select) {
                if (select.id !== 'typeFilter') {
                    select.innerHTML = '';
                } else {
                    select.innerHTML = '<option value="">所有作业类型</option>';
                }
                homeworkTypes.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.id;
                    option.textContent = type.name;
                    select.appendChild(option);
                });
            }
        });
    } catch (error) {
        console.error('加载作业类型失败:', error);
        throw error;
    }
}

// 加载作业周期
async function loadHomeworkCycles() {
    try {
        homeworkCycles = await apiRequest('/homework/cycles');
        
        // 填充作业周期下拉框
        const cycleSelects = [
            document.getElementById('homeworkCycle'),
            document.getElementById('editHomeworkCycle')
        ];
        
        cycleSelects.forEach(select => {
            if (select) {
                select.innerHTML = '';
                homeworkCycles.forEach(cycle => {
                    const option = document.createElement('option');
                    option.value = cycle.id;
                    option.textContent = cycle.name;
                    select.appendChild(option);
                });
            }
        });
    } catch (error) {
        console.error('加载作业周期失败:', error);
        throw error;
    }
}

// 加载作业记录
async function loadHomeworkRecords() {
    try {
        const container = document.getElementById('homeworkBody');
        const loadingElement = showLoading(container);
        
        // 获取作业记录
        homeworkRecords = await apiRequest('/homework/records/my-records');
        
        // 填充作业记录表格
        container.innerHTML = '';
        
        homeworkRecords.forEach(record => {
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
                <td>${record.total_questions}</td>
                <td>${record.correct_questions}</td>
                <td>${record.accuracy}%</td>
                <td>${formatDate(record.grading_date)}</td>
                <td>
                    <span class="badge ${isOverdue ? 'bg-danger' : (record.accuracy >= 60 ? 'bg-success' : 'bg-warning')}">
                        ${isOverdue ? '逾期' : (record.accuracy >= 60 ? '已完成' : '未完成')}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-primary me-2" onclick="editHomework(${record.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteHomework(${record.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
            
            container.appendChild(row);
        });
        
        hideLoading(loadingElement);
    } catch (error) {
        console.error('加载作业记录失败:', error);
        throw error;
    }
}

// 搜索作业记录
function searchHomework() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#homeworkBody tr');
    
    rows.forEach(row => {
        const studentName = row.cells[0].textContent.toLowerCase();
        row.style.display = studentName.includes(searchTerm) ? '' : 'none';
    });
}

// 按作业类型筛选
function filterByType() {
    const typeId = document.getElementById('typeFilter').value;
    const rows = document.querySelectorAll('#homeworkBody tr');
    
    rows.forEach(row => {
        const typeName = row.cells[1].textContent;
        if (!typeId) {
            row.style.display = '';
        } else {
            const selectedType = homeworkTypes.find(type => type.id == typeId);
            if (selectedType && typeName === selectedType.name) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

// 按周次筛选
function filterByWeek() {
    const week = document.getElementById('weekFilter').value;
    const rows = document.querySelectorAll('#homeworkBody tr');
    
    rows.forEach(row => {
        const rowWeek = row.cells[2].textContent;
        if (!week) {
            row.style.display = '';
        } else if (rowWeek == week) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// 添加作业记录
async function addHomework() {
    try {
        const student_id = document.getElementById('homeworkStudent').value;
        const homework_type_id = document.getElementById('homeworkType').value;
        const cycle_id = document.getElementById('homeworkCycle').value;
        const week_number = document.getElementById('homeworkWeek').value;
        const total_questions = document.getElementById('homeworkTotal').value;
        const correct_questions = document.getElementById('homeworkCorrect').value;
        const grading_date = document.getElementById('homeworkDate').value;
        const remark = document.getElementById('homeworkRemark').value;
        
        // 验证表单
        if (!student_id || !homework_type_id || !cycle_id || !week_number || !total_questions || !correct_questions || !grading_date) {
            showToast('请填写所有必填字段', 'danger');
            return;
        }
        
        // 验证正确题数不能超过总题数
        if (parseInt(correct_questions) > parseInt(total_questions)) {
            showToast('正确题数不能超过总题数', 'danger');
            return;
        }
        
        // 调用API添加作业记录
        await apiRequest('/homework/records', 'POST', {
            student_id: parseInt(student_id),
            homework_type_id: parseInt(homework_type_id),
            cycle_id: parseInt(cycle_id),
            week_number: parseInt(week_number),
            total_questions: parseInt(total_questions),
            correct_questions: parseInt(correct_questions),
            grading_date: grading_date,
            remark: remark
        });
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('addHomeworkModal'));
        modal.hide();
        
        // 重置表单
        document.getElementById('addHomeworkForm').reset();
        
        // 重新加载作业记录
        await loadHomeworkRecords();
        
        showToast('作业记录添加成功', 'success');
    } catch (error) {
        console.error('添加作业记录失败:', error);
        showToast(`添加作业记录失败: ${error.message}`, 'danger');
    }
}

// 编辑作业记录
async function editHomework(recordId) {
    try {
        // 查找作业记录
        const record = homeworkRecords.find(r => r.id === recordId);
        if (!record) {
            showToast('作业记录不存在', 'danger');
            return;
        }
        
        // 填充表单
        document.getElementById('editHomeworkId').value = record.id;
        document.getElementById('editHomeworkStudent').value = record.student_id;
        document.getElementById('editHomeworkType').value = record.homework_type_id;
        document.getElementById('editHomeworkCycle').value = record.cycle_id;
        document.getElementById('editHomeworkWeek').value = record.week_number;
        document.getElementById('editHomeworkTotal').value = record.total_questions;
        document.getElementById('editHomeworkCorrect').value = record.correct_questions;
        document.getElementById('editHomeworkDate').value = formatDate(record.grading_date);
        document.getElementById('editHomeworkRemark').value = record.remark || '';
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('editHomeworkModal'));
        modal.show();
    } catch (error) {
        console.error('编辑作业记录失败:', error);
        showToast(`编辑作业记录失败: ${error.message}`, 'danger');
    }
}

// 更新作业记录
async function updateHomework() {
    try {
        const id = document.getElementById('editHomeworkId').value;
        const total_questions = document.getElementById('editHomeworkTotal').value;
        const correct_questions = document.getElementById('editHomeworkCorrect').value;
        const grading_date = document.getElementById('editHomeworkDate').value;
        const remark = document.getElementById('editHomeworkRemark').value;
        
        // 验证表单
        if (!total_questions || !correct_questions || !grading_date) {
            showToast('请填写所有必填字段', 'danger');
            return;
        }
        
        // 验证正确题数不能超过总题数
        if (parseInt(correct_questions) > parseInt(total_questions)) {
            showToast('正确题数不能超过总题数', 'danger');
            return;
        }
        
        // 调用API更新作业记录
        await apiRequest(`/homework/records/${id}`, 'PUT', {
            total_questions: parseInt(total_questions),
            correct_questions: parseInt(correct_questions),
            grading_date: grading_date,
            remark: remark
        });
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('editHomeworkModal'));
        modal.hide();
        
        // 重新加载作业记录
        await loadHomeworkRecords();
        
        showToast('作业记录更新成功', 'success');
    } catch (error) {
        console.error('更新作业记录失败:', error);
        showToast(`更新作业记录失败: ${error.message}`, 'danger');
    }
}

// 删除作业记录
async function deleteHomework(recordId) {
    if (!confirm('确定要删除这个作业记录吗？')) {
        return;
    }
    
    try {
        // 调用API删除作业记录
        await apiRequest(`/homework/records/${recordId}`, 'DELETE');
        
        // 重新加载作业记录
        await loadHomeworkRecords();
        
        showToast('作业记录删除成功', 'success');
    } catch (error) {
        console.error('删除作业记录失败:', error);
        showToast(`删除作业记录失败: ${error.message}`, 'danger');
    }
}

// 复制上周作业
async function copyLastWeekHomework() {
    try {
        const weekNumber = prompt('请输入要复制的上周周次:', '');
        if (!weekNumber || isNaN(weekNumber)) {
            return;
        }
        
        const targetWeekNumber = parseInt(weekNumber) + 1;
        if (targetWeekNumber > 53) {
            showToast('目标周次超出范围', 'danger');
            return;
        }
        
        // 获取上周的作业记录
        const records = homeworkRecords.filter(r => r.week_number == weekNumber);
        if (records.length === 0) {
            showToast('上周没有作业记录', 'danger');
            return;
        }
        
        // 复制作业记录
        let successCount = 0;
        const today = new Date().toISOString().split('T')[0];
        
        for (const record of records) {
            try {
                await apiRequest('/homework/records', 'POST', {
                    student_id: record.student_id,
                    homework_type_id: record.homework_type_id,
                    cycle_id: record.cycle_id,
                    week_number: targetWeekNumber,
                    total_questions: record.total_questions,
                    correct_questions: 0, // 重置正确题数
                    grading_date: today,
                    remark: '' // 清空备注
                });
                successCount++;
            } catch (error) {
                console.error(`复制作业记录失败: ${error.message}`);
            }
        }
        
        // 重新加载作业记录
        await loadHomeworkRecords();
        
        showToast(`成功复制 ${successCount} 条作业记录到第 ${targetWeekNumber} 周`, 'success');
    } catch (error) {
        console.error('复制上周作业失败:', error);
        showToast(`复制上周作业失败: ${error.message}`, 'danger');
    }
}