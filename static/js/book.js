window.onload = () => {
    document.getElementById('search-btn').onclick = searchBooks;
    logoutInit();  // 挂载退出登录
    loadUserName(); // 展示用户名
};

// 获取当前用户名
async function loadUserName() {
    const res = await fetch('/api/user/me');
    const data = await res.json();
    if (data.code === 0) {
        document.getElementById('welcome-username').innerText = data.user_name;
    }
}

// 退出登录
async function logout() {
    await fetch('/api/user/logout', { method: 'POST' });
    window.location.href = '/';
}

function logoutInit() {
    window.logout = logout;
}

// 搜索书籍
async function searchBooks() {
    const params = new URLSearchParams();
    ['ISBN', 'book_name', 'author', 'publisher'].forEach(key => {
        const v = document.getElementById(key.toLowerCase()).value.trim();
        if (v) params.append(key, v);
    });

    const res = await fetch(`/api/book/search?${params}`);
    const data = await res.json();
    if (data.code === 0) {
        renderTable(data.books);
    } else {
        alert(data.msg);
        document.getElementById('book-table-body').innerHTML = '';
    }
}

// 渲染表格
function renderTable(books) {
    const tbody = document.getElementById('book-table-body');
    tbody.innerHTML = '';
    books.forEach(b => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
        <td>${b.book_id}</td>
        <td>${b.ISBN}</td>
        <td>${b.book_name}</td>
        <td>${b.author}</td>
        <td>${b.publisher}</td>
        <td>${b.retail_price}</td>
        <td>${b.quantity}</td>
        <td><button class="edit-btn" onclick="showEditModal(${b.book_id})">修改</button>
        <button class='sale-btn' onclick="showSaleModal(${b.book_id})">出售</button></td>
      `;
        tbody.appendChild(tr);
    });
}

// 弹出修改弹窗
function showEditModal(book_id) {
    const modalArea = document.getElementById('modal-area');
    modalArea.innerHTML = `
      <div class="modal-mask">
        <div class="modal">
          <h3>修改书籍信息</h3>
          <input id="edit-name" placeholder="书名"><br>
          <input id="edit-author" placeholder="作者"><br>
          <input id="edit-publisher" placeholder="出版社"><br>
          <input id="edit-price" type="number" placeholder="零售价"><br>
          <button onclick="submitEdit(${book_id})">提交</button>
          <button onclick="closeModal()">取消</button>
        </div>
      </div>`;
}

// 关闭弹窗
function closeModal() {
    document.getElementById('modal-area').innerHTML = '';
}

// 提交修改
async function submitEdit(book_id) {
    const payload = {
        book_name: document.getElementById('edit-name').value.trim(),
        author: document.getElementById('edit-author').value.trim(),
        publisher: document.getElementById('edit-publisher').value.trim(),
        retail_price: document.getElementById('edit-price').value.trim()
    };
    const res = await fetch(`/api/book/books/${book_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.code === 0) {
        alert('修改成功');
        closeModal();
        searchBooks(); // 重新搜索刷新表格
    } else {
        alert(data.msg);
    }
}

function showSaleModal(bid) {
    closeModal(); const modal = document.createElement('div'); modal.className = 'modal-mask';
    modal.innerHTML = `
      <div class="modal">
        <h3>销售 Book ID:${bid}</h3>
        <input id="sale-amt" type="number" placeholder="销售数量"><br>
        <button onclick="submitSale(${bid})">确定</button>
        <button onclick="closeModal()">取消</button>
      </div>
    `; document.getElementById('modal-area').appendChild(modal);
}

async function submitSale(bid) {
    const amt = document.getElementById('sale-amt').value;
    await action(`/api/purchase/sale/${bid}`, 'POST', () => loadOrders('/api/purchase/purchases'), { sale_amount: amt });
}

async function action(url, method, cb, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    const d = await res.json(); if (d.code !== 0) return alert(d.msg);
    alert(d.msg); closeModal(); cb();
}