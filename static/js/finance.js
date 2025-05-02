// finance.js

window.onload = async () => {
    await loadUser();
    bindLogout();

    document.getElementById('show-expenditure')
        .onclick = showExpenditureForm;
    document.getElementById('show-income')
        .onclick = showIncomeForm;
};

// 加载当前用户名
async function loadUser() {
    const res = await fetch('/api/user/me');
    const d = await res.json();
    if (d.code === 0) {
        document.getElementById('welcome-username').innerText = d.user_name;
    }
}

// 绑定退出登录
function bindLogout() {
    window.logout = async () => {
        await fetch('/api/user/logout', { method: 'POST' });
        window.location.href = '/';
    };
}

// —— 展示“支出”查询表单 —— 
function showExpenditureForm() {
    const formArea = document.getElementById('finance-form');
    formArea.innerHTML = `
      <div class="search-fields">
        <input id="exp-start" type="datetime-local" placeholder="开始时间" step="1">
        <input id="exp-end"   type="datetime-local" placeholder="结束时间" step="1">
        <button onclick="submitExpenditure()">查询支出</button>
      </div>
    `;
    document.getElementById('finance-table-container').innerHTML = '';
}

// 提交“支出”查询
async function submitExpenditure() {
    const start = document.getElementById('exp-start').value.replace('T', ' ');
    const end = document.getElementById('exp-end').value.replace('T', ' ');

    if (!start || !end) {
        return alert('请填写起止时间');
    }
    const params = new URLSearchParams({
        start_time: `${start}`,
        end_time: `${end}`
    });
    const res = await fetch(`/api/finance/purchase?${params}`);
    const d = await res.json();
    if (d.code !== 0) return alert(d.msg);
    renderFinanceTable(d.sales, 'out');
}

// —— 展示“收入”查询表单 —— 
function showIncomeForm() {
    const formArea = document.getElementById('finance-form');
    formArea.innerHTML = `
      <div class="search-fields">
        <input id="inc-start" type="datetime-local" placeholder="开始时间" step="1">
        <input id="inc-end"   type="datetime-local" placeholder="结束时间" step="1">
        <button onclick="submitIncome()">查询收入</button>
      </div>
    `;
    document.getElementById('finance-table-container').innerHTML = '';
}

// 提交“收入”查询
async function submitIncome() {
    const start = document.getElementById('inc-start').value.replace('T', ' ');
    const end = document.getElementById('inc-end').value.replace('T', ' ');

    if (!start || !end) {
        return alert('请填写起止时间');
    }
    const params = new URLSearchParams({
        start_time: `${start}`,
        end_time: `${end}`
    });
    const res = await fetch(`/api/finance/sale?${params}`);
    const d = await res.json();
    if (d.code !== 0) return alert(d.msg);
    renderFinanceTable(d.sales, 'in');
}

// 渲染财务查询结果表格
// keyField: 'in'  或 'out'
function renderFinanceTable(list, keyField) {
    const container = document.getElementById('finance-table-container');
    if (!list.length) {
        container.innerHTML = `<p>没有符合条件的记录</p>`;
        return;
    }

    // 表头
    const headers = ['Book ID', 'ISBN', '书名', '出版社', '单价', '数量', keyField === 'in' ? '收入' : '支出'];
    let html = `<table><thead><tr>`;
    headers.forEach(h => html += `<th>${h}</th>`);
    html += `</tr></thead><tbody>`;

    // 行数据
    list.forEach(row => {
        html += `<tr>
        <td>${row.book_id}</td>
        <td>${row.ISBN}</td>
        <td>${row.book_name}</td>
        <td>${row.publisher}</td>
        <td>${keyField === 'in' ? row.retail_price : row.purchase_price}</td>
        <td>${keyField === 'in' ? row.sale_amount : row.purchase_amount}</td>
        <td>${row[keyField]}</td>
      </tr>`;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}
