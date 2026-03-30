// 初始化页面
if (!initPage()) {
    // 未登录，已跳转到登录页面
    return;
}

let students = [];
let saTeachers = [];

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', async function() {
    try {
        // 加载SA老师列表
        await loadSATeachers();
        
        // 加载学生列表
        await loadStudents();
    } catch (error) {
        console.error('加载数据失败:', error);
        showToast('加载数据失败', 'danger');
    }
});

// 加载SA老师列表
async function loadSATeachers() {
    try {
        // 获取所有用户
        const users = await apiRequest('/users');
        
        // 筛选出SA老师
        saTeachers = users.filter(user => user.role === 'sa' && user.status === 'active');
        
        // 填充SA老师下拉框
        const saSelects = [
            document.getElementById('studentSA'),
            document.getElementById('editStudentSA'),
            document.getElementById('saFilter')
        ];
        
        saSelects.forEach(select => {
            if (select) {
                // 清空现有选项（除了第一个选项）
                if (select.id !== 'saFilter') {
                    select.innerHTML = '';
                } else {
                    select.innerHTML = '<option value="">所有SA老师</option>';
                }
                
                // 添加SA老师选项
                saTeachers.forEach(sa => {
                    const option = document.createElement('option');
                    option.value = sa.id;
                    option.textContent = sa.name;
                    select.appendChild(option);
                });
            }
        });
    } catch (error) {
        console.error('加载SA老师列表失败:', error);
        throw error;
    }
}

// 加载学生列表
async function loadStudents() {
    try {
        const container = document.getElementById('studentsBody');
        const loadingElement = showLoading(container);
        
        // 获取学生列表
        students = await apiRequest('/students');
        
        // 填充学生表格
        container.innerHTML = '';
        
        students.forEach(student => {
            const row = document.createElement('tr');
            
            // 查找SA老师姓名
            const saTeacher = saTeachers.find(sa => sa.id === student.sa_id);
            const saName = saTeacher ? saTeacher.name : '未分配';
            
            row.innerHTML = `
                <td>${student.id}</td>
                <td>${student.name}</td>
                <td>${student.level}</td>
                <td>${student.class_}</td>
                <td>${saName}</td>
                <td>
                    <button class="btn btn-sm btn-primary me-2" onclick="editStudent(${student.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteStudent(${student.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
            
            container.appendChild(row);
        });
        
        hideLoading(loadingElement);
    } catch (error) {
        console.error('加载学生列表失败:', error);
        throw error;
    }
}

// 搜索学生
function searchStudents() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#studentsBody tr');
    
    rows.forEach(row => {
        const studentName = row.cells[1].textContent.toLowerCase();
        row.style.display = studentName.includes(searchTerm) ? '' : 'none';
    });
}

// 按SA老师筛选
function filterBySA() {
    const saId = document.getElementById('saFilter').value;
    const rows = document.querySelectorAll('#studentsBody tr');
    
    rows.forEach(row => {
        const saName = row.cells[4].textContent;
        if (!saId) {
            row.style.display = '';
        } else {
            const selectedSA = saTeachers.find(sa => sa.id == saId);
            if (selectedSA && saName === selectedSA.name) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

// 添加学生
async function addStudent() {
    try {
        const name = document.getElementById('studentName').value;
        const level = document.getElementById('studentLevel').value;
        const class_ = document.getElementById('studentClass').value;
        const sa_id = document.getElementById('studentSA').value;
        
        // 验证表单
        if (!name || !level || !class_ || !sa_id) {
            showToast('请填写所有必填字段', 'danger');
            return;
        }
        
        // 调用API添加学生
        await apiRequest('/students', 'POST', {
            name: name,
            level: level,
            class_: class_,
            sa_id: parseInt(sa_id)
        });
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('addStudentModal'));
        modal.hide();
        
        // 重置表单
        document.getElementById('addStudentForm').reset();
        
        // 重新加载学生列表
        await loadStudents();
        
        showToast('学生添加成功', 'success');
    } catch (error) {
        console.error('添加学生失败:', error);
        showToast(`添加学生失败: ${error.message}`, 'danger');
    }
}

// 编辑学生
async function editStudent(studentId) {
    try {
        // 查找学生
        const student = students.find(s => s.id === studentId);
        if (!student) {
            showToast('学生不存在', 'danger');
            return;
        }
        
        // 填充表单
        document.getElementById('editStudentId').value = student.id;
        document.getElementById('editStudentName').value = student.name;
        document.getElementById('editStudentLevel').value = student.level;
        document.getElementById('editStudentClass').value = student.class_;
        document.getElementById('editStudentSA').value = student.sa_id;
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('editStudentModal'));
        modal.show();
    } catch (error) {
        console.error('编辑学生失败:', error);
        showToast(`编辑学生失败: ${error.message}`, 'danger');
    }
}

// 更新学生
async function updateStudent() {
    try {
        const id = document.getElementById('editStudentId').value;
        const name = document.getElementById('editStudentName').value;
        const level = document.getElementById('editStudentLevel').value;
        const class_ = document.getElementById('editStudentClass').value;
        const sa_id = document.getElementById('editStudentSA').value;
        
        // 验证表单
        if (!name || !level || !class_ || !sa_id) {
            showToast('请填写所有必填字段', 'danger');
            return;
        }
        
        // 调用API更新学生
        await apiRequest(`/students/${id}`, 'PUT', {
            name: name,
            level: level,
            class_: class_,
            sa_id: parseInt(sa_id)
        });
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('editStudentModal'));
        modal.hide();
        
        // 重新加载学生列表
        await loadStudents();
        
        showToast('学生更新成功', 'success');
    } catch (error) {
        console.error('更新学生失败:', error);
        showToast(`更新学生失败: ${error.message}`, 'danger');
    }
}

// 删除学生
async function deleteStudent(studentId) {
    if (!confirm('确定要删除这个学生吗？')) {
        return;
    }
    
    try {
        // 调用API删除学生
        await apiRequest(`/students/${studentId}`, 'DELETE');
        
        // 重新加载学生列表
        await loadStudents();
        
        showToast('学生删除成功', 'success');
    } catch (error) {
        console.error('删除学生失败:', error);
        showToast(`删除学生失败: ${error.message}`, 'danger');
    }
}