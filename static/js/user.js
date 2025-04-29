window.onload = async function() {
    try {
        const res = await fetch('/api/user/me');
        const data = await res.json();

        if (data.code === 0) {
            document.getElementById('welcome-username').innerText = data.user_name;
            const isSuper = (data.user_type === 'super');

            await loadUserTable(isSuper); // 等表格加载完成

            if (isSuper) {
                const addBtn = document.createElement('button');
                addBtn.innerText = '添加新用户';
                addBtn.onclick = showAddUserForm;
                document.getElementById('user-operations').appendChild(addBtn);
            }

        } else {
            alert('请先登录');
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('加载用户信息失败', error);
        alert('加载失败，请重试');
    }
};

async function loadUserTable(isSuper) {
    const thead = document.getElementById('user-table-head');
    const tbody = document.getElementById('user-table-body');

    thead.innerHTML = `
        <tr>
            <th>用户名</th>
            <th>姓名</th>
            <th>工号</th>
            <th>性别</th>
            <th>年龄</th>
            ${isSuper ? '<th>操作</th>' : '<th>修改我的信息</th>'}
        </tr>
    `;

    tbody.innerHTML = '';

    const url = isSuper ? '/api/user/all_users' : '/api/user/me';

    const res = await fetch(url);
    const data = await res.json();

    if (data.code === 0) {
        let users = [];

        if (isSuper) {
            users = data.users;
        } else {
            users = [{
                user_id: data.user_id,
                user_name: data.user_name,
                name: data.name,
                job_num: data.job_number,
                gender: data.gender,
                age: data.age
            }];
        }

        users.forEach(user => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${user.user_name}</td>
                <td>${user.name}</td>
                <td>${user.job_num}</td>
                <td>${user.gender}</td>
                <td>${user.age}</td>
                <td>
                    <button onclick="editUser(${user.user_id})">修改</button>
                    ${isSuper ? `<button onclick="deleteUser(${user.user_id})">删除</button>` : ''}
                </td>
            `;
            tbody.appendChild(tr);
        });
    } else {
        alert('获取用户信息失败');
    }
}

