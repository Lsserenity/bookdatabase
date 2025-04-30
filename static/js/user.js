window.onload = async function () {
    try {
        const res = await fetch('/api/user/me');
        const data = await res.json();

        if (data.code === 0) {
            document.getElementById('welcome-username').innerText = data.user_name;
            const isSuper = (data.user_type === 'super');

            await loadUserTable(isSuper); // 等表格加载完成

            if (isSuper) {
                const addBtn = document.createElement('button');
                addBtn.id = 'add-user-btn';
                addBtn.innerText = '添加新用户';
                addBtn.onclick = showAddUserForm;
                // document.getElementById('user-operations').appendChild(addBtn);
            }

        } else {
            alert('请先登录');
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('加载用户信息失败', error);
        alert('加载失败，请重试');
    }
}

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
            tr.setAttribute('data-user-id', user.user_id);
            tr.innerHTML = `
                <td>${user.user_name}</td>
                <td>${user.name}</td>
                <td>${user.job_num}</td>
                <td>${user.gender}</td>
                <td>${user.age}</td>
                <td>
                    <button onclick="editUser(${user.user_id}, ${isSuper})">修改</button>
                    ${isSuper ? `<button onclick="deleteUser(${user.user_id})">删除</button>` : ''}
                </td>
            `;
            tbody.appendChild(tr);
        });
    } else {
        alert('获取用户信息失败');
    }

    if (isSuper) {
        const formArea = document.getElementById('form-area');
        const existing = document.getElementById('add-user-btn');
        if (!existing) {
            const addBtn = document.createElement('button');
            addBtn.id = 'add-user-btn';
            addBtn.innerText = '添加新用户';
            addBtn.onclick = showAddUserForm;
            addBtn.className = 'btn-primary';
            formArea.appendChild(addBtn);
        }
    }
}

function showAddUserForm() {
    // 创建一个弹窗遮罩
    const modal = document.createElement('div');
    modal.id = 'add-user-modal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    // 弹窗内容
    modal.innerHTML = `
        <div style="background: white; padding: 20px; border-radius: 8px; width: 300px;">
            <h3>添加新用户</h3>
            <input id="new-username" placeholder="用户名" style="width: 100%; margin: 5px 0;"><br>
            <input id="new-password" type="password" placeholder="密码" style="width: 100%; margin: 5px 0;"><br>
            <input id="new-name" placeholder="姓名" style="width: 100%; margin: 5px 0;"><br>
            <input id="new-jobnum" placeholder="工号（6位数字）" style="width: 100%; margin: 5px 0;"><br>
            <input id="new-gender" placeholder="性别（male or female)" style="width: 100%; margin: 5px 0;"><br>
            <input id="new-age" type="number" placeholder="年龄" style="width: 100%; margin: 5px 0;"><br>
            <button onclick="submitNewUser()" style="margin-right: 10px;">提交</button>
            <button onclick="closeAddUserForm()">取消</button>
        </div>
    `;

    document.body.appendChild(modal);
}

// 提交新用户
async function submitNewUser() {
    const username = document.getElementById('new-username').value.trim();
    const password = document.getElementById('new-password').value.trim();
    const name = document.getElementById('new-name').value.trim();
    const job_num = document.getElementById('new-jobnum').value.trim();
    const gender = document.getElementById('new-gender').value.trim();
    const age = document.getElementById('new-age').value.trim();

    if (!username || !password || !name || !job_num || !gender || !age) {
        alert('请填写完整信息');
        return;
    }

    try {
        const res = await fetch('/api/user/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_name: username,
                password: password,
                name: name,
                job_number: job_num,
                gender: gender,
                age: parseInt(age)
            })
        });

        const data = await res.json();

        if (data.code === 0) {
            alert('添加成功！');
            closeAddUserForm();
            await loadUserTable(true); // 重新加载用户列表
        } else {
            alert(data.msg || '添加失败');
        }
    } catch (error) {
        console.error('添加用户失败', error);
        alert('添加用户失败');
    }
}

// 关闭弹窗
function closeAddUserForm() {
    const modal = document.getElementById('add-user-modal');
    if (modal) {
        document.body.removeChild(modal);
    }
}

function editUser(user_id, isSuper) {
    // 获取表格中该用户的现有数据
    const row = [...document.querySelectorAll(
        `#user-table-body tr[data-user-id="${user_id}"]`)][0];

    if (!row) {
        alert('找不到用户信息');
        return;
    }

    const cells = row.querySelectorAll('td');
    const username = cells[0].innerText;
    const name = cells[1].innerText;
    const job_num = cells[2].innerText;
    const gender = cells[3].innerText;
    const age = cells[4].innerText;

    const modal = document.createElement('div');
    modal.id = 'edit-user-modal';
    modal.style = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0,0,0,0.5); display: flex;
        justify-content: center; align-items: center; z-index: 1000;
    `;

    // 如果是 super，增加密码输入框
    const pwdInput = isSuper
        ? `<input id="edit-password" type="password" placeholder="新密码（留空不修改）" style="width:100%;margin:5px 0;"><br>`
        : '';

    modal.innerHTML = `
        <div style="background: white; padding: 20px; border-radius: 8px; width: 300px;">
            <h3>修改用户信息</h3>
            <input id="edit-username" value="${username}" placeholder="用户名" style="width: 100%; margin: 5px 0;"><br>
            <input id="edit-name" value="${name}" placeholder="姓名" style="width: 100%; margin: 5px 0;"><br>
            <input id="edit-jobnum" value="${job_num}" placeholder="工号" style="width: 100%; margin: 5px 0;"><br>
            <input id="edit-gender" value="${gender}" placeholder="性别" style="width: 100%; margin: 5px 0;"><br>
            <input id="edit-age" type="number" value="${age}" placeholder="年龄" style="width: 100%; margin: 5px 0;"><br>
            <input id="edit-age" value="${age}" type="number" placeholder="年龄" style="width:100%;margin:5px 0;"><br>
            ${pwdInput}
            <button onclick="submitEditUser(${user_id}, ${isSuper})" style="margin-right: 10px;">提交</button>
            <button onclick="closeEditUserForm()">取消</button>
        </div>
    `;
    document.body.appendChild(modal);
}

function closeEditUserForm() {
    const modal = document.getElementById('edit-user-modal');
    if (modal) {
        document.body.removeChild(modal);
    }
}

async function submitEditUser(user_id, isSuper) {
    // const user_name = document.getElementById('edit-username').value.trim();
    // const name = document.getElementById('edit-name').value.trim();
    // const job_number = document.getElementById('edit-jobnum').value.trim();
    // const gender = document.getElementById('edit-gender').value.trim();
    // const age = parseInt(document.getElementById('edit-age').value.trim());

    const payload = {
        user_id,
        user_name: document.getElementById('edit-username').value.trim(),
        name: document.getElementById('edit-name').value.trim(),
        job_number: document.getElementById('edit-jobnum').value.trim(),
        gender: document.getElementById('edit-gender').value.trim(),
        age: parseInt(document.getElementById('edit-age').value.trim(), 10)
    };

    if (isSuper) {
        const pwd = document.getElementById('edit-password').value.trim();
        if (pwd) payload.password = pwd;
    }

    // if (!user_name || !name || !job_number || !gender || !age) {
    //     alert('请填写完整信息');
    //     return;
    // }

    try {
        const res = await fetch('/api/user/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (data.code === 0) {
            alert('修改成功！');
            closeEditUserForm();
            // 重新加载，刷新表格
            const me = await fetch('/api/user/me').then(r => r.json());
            await loadUserTable(me.user_type === 'super');
        } else {
            alert(data.msg || '修改失败');
        }

    } catch (err) {
        console.error('修改失败', err);
        alert('网络错误');
    }
}

async function deleteUser(user_id) {
    const confirmed = confirm("确定要删除该用户吗？删除后无法恢复！");
    if (!confirmed) return;

    try {
        const res = await fetch('/api/user/delete_user', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id })
        });

        const data = await res.json();
        if (data.code === 0) {
            alert('删除成功！');
            const me = await fetch('/api/user/me').then(r => r.json());
            await loadUserTable(me.user_type === 'super');
        } else {
            alert(data.msg || '删除失败');
        }
    } catch (error) {
        console.error('删除用户失败', error);
        alert('删除失败，请重试');
    }
}

// ===== 新增：退出登录 =====
async function logout() {
    try {
        const res = await fetch('/api/user/logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (data.code === 0) {
            alert('已退出登录');
            window.location.href = '/';
        } else {
            alert(data.msg || '退出失败');
        }
    } catch (err) {
        console.error('退出登录失败', err);
        alert('网络错误');
    }
}


// ===== 新增：普通用户“修改密码”按钮渲染 =====
// 在页面加载完毕后，根据 isSuper 动态追加
// 建议在 window.onload 的末尾或 loadUserTable 调用之后加：
; (async function addNormalChangePwdBtn() {
    const me = await fetch('/api/user/me').then(r => r.json());
    if (me.code !== 0) return;
    if (me.user_type !== 'super') {
        // 普通用户在操作区加一个“修改密码”按钮
        const ops = document.getElementById('user-operations');
        const btn = document.createElement('button');
        btn.innerText = '修改密码';
        btn.className = 'btn-primary';
        btn.onclick = showChangePasswordForm;
        ops.appendChild(btn);
    }
})();


// ===== 新增：修改密码弹窗和提交逻辑 =====
function showChangePasswordForm() {
    const existing = document.getElementById('change-password-modal');
    if (existing) return;

    const modal = document.createElement('div');
    modal.id = 'change-password-modal';
    modal.style = `
        position: fixed; top:0; left:0; width:100%; height:100%;
        background: rgba(0,0,0,0.5); display:flex;
        justify-content:center; align-items:center; z-index:1000;
    `;
    modal.innerHTML = `
      <div style="background:white;padding:20px;border-radius:8px;width:300px;">
        <h3>修改密码</h3>
        <input id="old-pwd" type="password" placeholder="旧密码" style="width:100%;margin:5px 0;"><br>
        <input id="new-pwd" type="password" placeholder="新密码(≥6位)" style="width:100%;margin:5px 0;"><br>
        <input id="conf-pwd" type="password" placeholder="确认新密码" style="width:100%;margin:5px 0;"><br>
        <button onclick="submitChangePassword()" style="margin-right:10px;">提交</button>
        <button onclick="closeChangePasswordForm()">取消</button>
      </div>
    `;
    document.body.appendChild(modal);
}

function closeChangePasswordForm() {
    const mdl = document.getElementById('change-password-modal');
    if (mdl) document.body.removeChild(mdl);
}

async function submitChangePassword() {
    const oldPwd = document.getElementById('old-pwd').value.trim();
    const newPwd = document.getElementById('new-pwd').value.trim();
    const confPwd = document.getElementById('conf-pwd').value.trim();

    if (!oldPwd || !newPwd || !confPwd) {
        alert('请填写所有字段');
        return;
    }
    if (newPwd.length < 6) {
        alert('新密码至少 6 位');
        return;
    }
    if (newPwd !== confPwd) {
        alert('两次输入不一致');
        return;
    }

    try {
        const res = await fetch('/api/user/reset_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_name: document.getElementById('welcome-username').innerText,
                old_password: oldPwd,
                new_password: newPwd
            })
        });
        const data = await res.json();
        if (data.code === 0) {
            alert('密码修改成功，请重新登录');
            window.location.href = '/';
        } else {
            alert(data.msg || '修改失败');
        }
    } catch (err) {
        console.error('修改密码失败', err);
        alert('网络错误');
    }
}
