document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
    const errorDiv = document.getElementById('error-message');

    form.addEventListener('submit', async function (e) {
        e.preventDefault(); // 阻止表单默认提交行为

        const formData = new FormData(form);
        const data = {
            user_name: formData.get('user_name'),
            password: formData.get('password')
        };

        try {
            const response = await fetch('/api/user/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.code === 0) {
                // 登录成功，跳转到首页（我们等下写）
                window.location.href = '/home';
            } else {
                // 登录失败，显示错误信息
                errorDiv.textContent = result.msg;
            }
        } catch (error) {
            console.error('请求出错:', error);
            errorDiv.textContent = '服务器错误，请稍后重试。';
        }
    });
});
