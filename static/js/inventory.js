window.onload = async () => {
    await loadUser();
    bindLogout();
    document.getElementById('add-order-btn').onclick = showAddOrderModal;
    document.getElementById('show-unpaid').onclick = () => loadOrders('/api/purchase/unpaid');
    document.getElementById('show-paid').onclick = () => loadOrders('/api/purchase/paid');
    document.getElementById('show-all').onclick = () => loadOrders('/api/purchase/purchases');
    // 默认加载已支付
    loadOrders('/api/purchase/purchases');
};

async function loadUser() {
    const res = await fetch('/api/user/me');
    const d = await res.json();
    if (d.code === 0) document.getElementById('welcome-username').innerText = d.user_name;
}
function bindLogout() {
    window.logout = async () => {
        await fetch('/api/user/logout', { method: 'POST' });
        location.href = '/';
    };
}

// 加载订单列表
async function loadOrders(url) {
    const res = await fetch(url);
    const d = await res.json();
    if (d.code !== 0) return alert(d.msg);
    renderTable(d.purchases);
}

// 渲染表格
function renderTable(list) {
    const tbody = document.getElementById('order-tbody');
    tbody.innerHTML = '';
    list.forEach(o => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
        <td>${o.purchase_id}</td>
        <td>${o.book.ISBN || ''}</td>
        <td>${o.book_id}</td>
        <td>${o.purchase_amount}</td>
        <td>${o.purchase_price}</td>
        <td>${o.purchase_status}</td>
        <td>${o.onstage}</td>
        <td>${actionButtons(o)}</td>
      `;
        tbody.appendChild(tr);
    });
}

// 根据状态生成操作按钮
function actionButtons(o) {
    let btns = '';
    if (o.purchase_status === 'unpaid') {
        btns += `<button onclick="payOrder(${o.purchase_id})">付款</button>`;
        btns += `<button onclick="returnOrder('${o.purchase_id}')">退货</button>`;
    }
    if (o.purchase_status === 'paid' && o.onstage === 'no') {
        btns += `<button onclick="showOnstageModal(${o.purchase_id}, '${o.book.ISBN}')">上架</button>`;
    }
    return btns;
}

// 1. 添加订单弹窗
function showAddOrderModal() {
    const modal = document.createElement('div');
    modal.id = 'add-order-modal';
    modal.className = 'modal-mask';
    modal.innerHTML = `
      <div class="modal">
        <h3>添加新订单</h3>
        <input id="modal-isbn" placeholder="ISBN"><br>
        <input id="modal-price" type="number" placeholder="价格"><br>
        <input id="modal-amount" type="number" placeholder="数量"><br>
        <button onclick="submitAddOrder()">确定</button>
        <button onclick="closeModal()">取消</button>
      </div>
    `;
    document.getElementById('modal-area').appendChild(modal);
}

async function submitAddOrder() {
    const isbn = document.getElementById('modal-isbn').value.trim();
    const price = document.getElementById('modal-price').value;
    const amt = document.getElementById('modal-amount').value;
    // 先尝试 /buy/<isbn>
    let res = await fetch(`/api/purchase/buy/${isbn}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ purchase_price: price, purchase_amount: amt })
    });
    if (res.status === 404) {
        // 弹出新建书籍表单
        showNewBookModal(isbn, price, amt);
        return;
    }
    const d = await res.json();
    if (d.code !== 0) return alert(d.msg);
    alert('添加订单成功');
    closeModal(); loadOrders('/api/purchase/unpaid');
}

// 新建书籍后进货
function showNewBookModal(isbn, price, amt) {
    closeModal();
    const modal = document.createElement('div');
    modal.id = 'add-book-modal'; modal.className = 'modal-mask';
    modal.innerHTML = `
      <div class="modal">
        <h3>新建书籍信息</h3>
        <input id="book-isbn" value="${isbn}" disabled><br>
        <input id="book-name" placeholder="书名"><br>
        <input id="book-author" placeholder="作者"><br>
        <input id="book-pub" placeholder="出版社"><br>
        <input id="book-rp" type="number" placeholder="零售价"><br>
        <button onclick="submitNewBook(${price},${amt})">确定</button>
        <button onclick="closeModal()">取消</button>
      </div>
    `;
    document.getElementById('modal-area').appendChild(modal);
}


async function submitNewBook(price, amt) {
    const payload = {
        ISBN: document.getElementById('book-isbn').value,
        book_name: document.getElementById('book-name').value.trim(),
        author: document.getElementById('book-author').value.trim(),
        publisher: document.getElementById('book-pub').value.trim(),
        retail_price: document.getElementById('book-rp').value,
        purchase_price: price,
        purchase_amount: amt
    };
    const res = await fetch('/api/purchase/buy/add', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const d = await res.json(); if (d.code !== 0) return alert(d.msg);
    alert('新增并进货成功'); closeModal(); loadOrders('/api/purchase/unpaid');
}

// 付款、退货、上架、销售逻辑
async function payOrder(id) { await action(`/api/purchase/pay/${id}`, 'POST', () => loadOrders('/api/purchase/unpaid')); }
async function returnOrder(purchaseId) {
    await action(`/api/purchase/return_by_id/${purchaseId}`, 'POST',
        () => loadOrders('/api/purchase/unpaid'));
}

function showOnstageModal(pid, isbn) {
    closeModal(); const modal = document.createElement('div'); modal.className = 'modal-mask';
    modal.innerHTML = `
      <div class="modal">
        <h3>上架 ISBN:${isbn}</h3>
        <input id="onstage-price" type="number" placeholder="零售价"><br>
        <button onclick="submitOnstage(${pid})">确定</button>
        <button onclick="closeModal()">取消</button>
      </div>
    `; document.getElementById('modal-area').appendChild(modal);
}
async function submitOnstage(pid) {
    const price = document.getElementById('onstage-price').value.trim();
    if (!price) {
        return alert('请填写零售价');
    }
    const ids = [pid];
    await action('/api/purchase/onstage/batch', 'POST', () => loadOrders('/api/purchase/paid'), { purchase_ids: ids, retail_price: price });
}

async function action(url, method, cb, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    const d = await res.json(); if (d.code !== 0) return alert(d.msg);
    alert(d.msg); closeModal(); cb();
}

function closeModal() { document.getElementById('modal-area').innerHTML = ''; }