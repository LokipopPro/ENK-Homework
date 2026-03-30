// API基础URL
let API_BASE_URL = '/api';

// 检查是否在本地开发环境
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    API_BASE_URL = 'http://localhost:8001/api';
}

// 存储token到本地存储
function setToken(token) {
    localStorage.setItem('token', token);
}

// 从本地存储获取token
function getToken() {
    return localStorage.getItem('token');
}

// 从本地存储移除token
function removeToken() {
    localStorage.removeItem('token');
}

// 存储用户信息到本地存储
function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

// 从本地存储获取用户信息
function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// 从本地存储移除用户信息
function removeUser() {
    localStorage.removeItem('user');
}

// 检查用户是否已登录
function isLoggedIn() {
    return getToken() !== null;
}

// 检查用户是否为管理员
function isAdmin() {
    const user = getUser();
    return user && user.role === 'admin';
}

// 检查用户是否为SA老师
function isSA() {
    const user = getUser();
    return user && user.role === 'sa';
}

// 通用API请求函数
async function apiRequest(endpoint, method = 'GET', data = null) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        method,
        headers,
        credentials: 'include'
    };
    
    if (data) {
        config.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `请求失败: ${response.status}`);
        }
        
        // 对于204 No Content响应，直接返回null
        if (response.status === 204) {
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

// 显示提示信息
function showToast(message, type = 'success') {
    const toastContainer = document.createElement('div');
    toastContainer.className = `toast show bg-${type} text-white`;
    toastContainer.role = 'alert';
    toastContainer.ariaLive = 'assertive';
    toastContainer.ariaAtomic = 'true';
    
    toastContainer.innerHTML = `
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    document.body.appendChild(toastContainer);
    
    setTimeout(() => {
        toastContainer.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toastContainer);
        }, 300);
    }, 3000);
}

// 显示加载动画
function showLoading(container) {
    const loadingElement = document.createElement('div');
    loadingElement.className = 'd-flex justify-content-center py-4';
    loadingElement.innerHTML = '<div class="loading"></div>';
    container.appendChild(loadingElement);
    return loadingElement;
}

// 隐藏加载动画
function hideLoading(loadingElement) {
    if (loadingElement) {
        loadingElement.remove();
    }
}

// 格式化日期
function formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toISOString().split('T')[0];
}

// 格式化时间
function formatDateTime(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleString('zh-CN');
}

// 计算正确率
function calculateAccuracy(correct, total) {
    if (total === 0) return 0;
    return Math.round((correct / total) * 100 * 100) / 100;
}

// 检查是否逾期
function checkOverdue(date) {
    const today = new Date();
    const gradingDate = new Date(date);
    const diffTime = Math.abs(today - gradingDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 3;
}

// 导航到指定页面
function navigateTo(page) {
    window.location.href = page;
}

// 退出登录
function logout() {
    removeToken();
    removeUser();
    navigateTo('index.html');
}

// 初始化页面
function initPage() {
    // 检查登录状态
    if (!isLoggedIn()) {
        navigateTo('index.html');
        return false;
    }
    
    // 设置用户名显示
    const user = getUser();
    if (user) {
        const usernameElement = document.getElementById('username');
        if (usernameElement) {
            usernameElement.textContent = user.name;
        }
    }
    
    return true;
}

// 侧边栏切换
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
        if (mainContent) {
            mainContent.classList.toggle('expanded');
        }
    }
}

// 移动端菜单切换
function toggleMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

// 表格排序
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // 检查当前排序状态
    const currentSort = table.getAttribute('data-sort') || 'asc';
    const newSort = currentSort === 'asc' ? 'desc' : 'asc';
    table.setAttribute('data-sort', newSort);
    
    // 排序
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        if (!isNaN(aValue) && !isNaN(bValue)) {
            return newSort === 'asc' ? parseFloat(aValue) - parseFloat(bValue) : parseFloat(bValue) - parseFloat(aValue);
        }
        
        return newSort === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
    });
    
    // 重新排列行
    rows.forEach(row => tbody.appendChild(row));
    
    // 更新排序图标
    table.querySelectorAll('th').forEach((th, index) => {
        th.innerHTML = th.innerHTML.replace(/ <i class="bi .*?<\/i>/g, '');
        if (index === columnIndex) {
            th.innerHTML += newSort === 'asc' ? ' <i class="bi bi-sort-down"></i>' : ' <i class="bi bi-sort-up"></i>';
        }
    });
}

// 搜索功能
function searchTable(input, table) {
    const filter = input.value.toLowerCase();
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
    });
}