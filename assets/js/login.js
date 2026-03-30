// 登录表单提交处理
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        // 调用登录API - 使用表单数据格式
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `请求失败: ${response.status}`);
        }
        
        const loginData = await response.json();
        
        // 存储token和用户信息
        setToken(loginData.access_token);
        
        // 获取用户信息
        const userInfo = await apiRequest('/auth/me');
        setUser(userInfo);
        
        // 根据用户角色跳转到不同页面
        if (userInfo.role === 'admin') {
            navigateTo('pages/admin/dashboard.html');
        } else if (userInfo.role === 'sa') {
            navigateTo('pages/sa/dashboard.html');
        } else {
            showToast('未知用户角色', 'danger');
        }
    } catch (error) {
        showToast(`登录失败: ${error.message}`, 'danger');
    }
});