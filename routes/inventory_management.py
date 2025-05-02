# 数据库存管理模块

from flask import session, jsonify, request, Blueprint
from database.modules import Purchase, Book, FinancePurchaseBill, Sale, FinanceSaleBill
from database import db

purchase_bp = Blueprint('purchase', __name__)


# 根据ISBN选书购买
@purchase_bp.route('/buy/<string:isbn>', methods=['POST'])
def buy(isbn):
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    book = Book.query.filter_by(ISBN=isbn).first()

    if not book:
        return jsonify({'code': 1, 'msg': '该图书不存在，请新建购买信息！'}), 404

    data = request.json
    price = data.get('purchase_price')
    amount = data.get('purchase_amount')

    if not price or not amount:
        return jsonify({'code': 1, 'msg': '缺少价格或数量'}), 400
    # 在 buy 路由中添加：

    try:
        price = float(price)
        amount = int(amount)
    except (ValueError, TypeError):
        return jsonify({'code': 1, 'msg': '价格或数量格式错误'}), 400

    if amount <= 0 or price <= 0:
        return jsonify({'code': 1, 'msg': '数量或价格必须大于零'}), 400

    purchase = Purchase(
        book_id=book.book_id,
        purchase_price=price,
        purchase_amount=amount,
        purchase_status='unpaid',
        # create_time 会默认生成
        operator_id=session['user_id']
    )

    try:
        db.session.add(purchase)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '购买信息添加成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': '数据库错误', 'error': str(e)}), 500


# 要买的书不存在，先新建book信息再购买
@purchase_bp.route('/buy/add', methods=['POST'])
def buy_new():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    data = request.json
    isbn = data.get('ISBN')
    b_name = data.get('book_name')
    b_p = data.get('publisher')
    b_a = data.get('author')
    b_rp = data.get('retail_price')

    if not isbn or not b_name or not b_p or not b_a or not b_rp:
        return jsonify({'code': 1, 'msg': '请输入完整的书籍信息！'}), 400

    if len(isbn) != 13 or not isbn.isdigit():
        return jsonify({'code': 1, 'msg': 'ISBN必须为13位数字'}), 400

    if Book.query.filter_by(ISBN=isbn).first():
        return jsonify({'code': 1, 'msg': '该书籍信息已存在，请直接购买！'}), 400

    try:
        b_rp = float(b_rp)
    except ValueError:
        return jsonify({'code': 1, 'msg': '价格格式错误'}), 400

    book = Book(
        ISBN=isbn,
        book_name=b_name,
        publisher=b_p,
        author=b_a,
        retail_price=b_rp,
        quantity=0
    )

    # 新建购买信息：
    price = data.get('purchase_price')
    amount = data.get('purchase_amount')

    if not price or not amount:
        return jsonify({'code': 1, 'msg': '缺少购买价格或购买数量'}), 400

    try:
        price = float(price)
        amount = int(amount)
    except ValueError:
        return jsonify({'code': 1, 'msg': '购买价格或购买数量格式错误'}), 400

    try:
        db.session.add(book)
        db.session.flush()
        purchase = Purchase(
            book_id=book.book_id,
            purchase_price=price,
            purchase_amount=amount,
            purchase_status='unpaid',
            # create_time 会默认生成
            operator_id=session['user_id']
        )

        db.session.add(purchase)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '新书信息添加成功！进货信息添加成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': '数据库错误', 'error': str(e)}), 500


@purchase_bp.route('/pay/<int:purchase_id>', methods=['POST'])
def pay_by_id(purchase_id):
    if 'user_id' not in session:
        return jsonify({'code':1,'msg':'请先登录'}),401

    p = Purchase.query.get(purchase_id)
    if not p or p.purchase_status!='unpaid':
        return jsonify({'code':1,'msg':'订单状态不可支付'}),400

    p.purchase_status = 'paid'
    db.session.add(FinancePurchaseBill(purchase_id=purchase_id))
    db.session.commit()
    return jsonify({'code':0,'msg':'订单支付成功！'})


# 书籍退货
@purchase_bp.route('/return_by_id/<int:purchase_id>', methods=['POST'])
def return_by_id(purchase_id):
    if 'user_id' not in session:
        return jsonify({'code':1,'msg':'请先登录'}),401

    p = Purchase.query.get(purchase_id)
    if not p or p.purchase_status != 'unpaid':
        return jsonify({'code':1,'msg':'退货失败，记录不存在或不可退货'}),400

    p.purchase_status = 'returned'
    book = Book.query.get(p.book_id)
    book.rollback_if_empty()
    db.session.commit()
    return jsonify({'code':0,'msg':'退货成功！'})


# 书籍上架更新
@purchase_bp.route('/onstage/batch', methods=['POST'])
def onstage():
    data = request.json
    ids = data.get('purchase_ids', [])
    new_price = data.get('retail_price', None)

    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401
    if not ids:
        return jsonify({'code': 1, 'msg': '请选择要上架的书籍'}), 400
    if new_price is None:
        return jsonify({'code': 1, 'msg': '请提供新的零售价'}), 400

    try:
        new_price = float(new_price)
        if new_price <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({'code': 1, 'msg': '零售价格式错误'}), 400

    updated = 0
    for pid in ids:
        p = Purchase.query.get(pid)
        if p and p.purchase_status == 'paid' and p.onstage == 'no':
            book = Book.query.get(p.book_id)
            book.retail_price = new_price
            book.quantity = book.quantity + p.purchase_amount
            book.book_status = 'normal'
            p.onstage = 'yes'
            updated += 1

    try:
        db.session.commit()
        return jsonify({'code': 0, 'msg': f'{updated} 条订单书籍上架成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': '数据库错误', 'error': str(e)}), 500


# 书籍销售
@purchase_bp.route('/sale/<int:b_id>', methods=['POST'])
def sale(b_id):
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    data = request.json
    amount = data.get('sale_amount')

    if amount is None:
        return jsonify({'code': 1, 'msg': '请输入销售数量'}), 400
    try:
        amount = int(amount)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({'code': 1, 'msg': '销售数量必须为正整数'}), 400

    book = Book.query.get(b_id)
    if not book:
        return jsonify({'code': 1, 'msg': '该书籍不存在'}), 404
    if book.quantity < amount:
        return jsonify({'code': 1, 'msg': '库存不足'}), 400

    book.quantity -= amount
    s = Sale(
        book_id=b_id,
        sale_amount=amount
    )

    try:
        db.session.add(s)
        db.session.flush()
        sale_bill = FinanceSaleBill(sale_id=s.sale_id)
        db.session.add(sale_bill)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '出售记录更新成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': '数据库错误', 'error': str(e)}), 500


@purchase_bp.route('/unpaid', methods=['GET'])
def unpaid_books():
    if 'user_id' not in session:
        return jsonify({'code':1,'msg':'请先登录'}),401
    
    orders = Purchase.query.filter_by(purchase_status='unpaid').all()
    return jsonify({
        'code':0,
        'purchases': [o.to_dict() for o in orders]
    })


@purchase_bp.route('/paid', methods=['GET'])
def paid_books():
    if 'user_id' not in session:
        return jsonify({'code':1,'msg':'请先登录'}),401
    
    orders = Purchase.query.filter_by(purchase_status='paid').all()
    return jsonify({
        'code':0,
        'purchases': [o.to_dict() for o in orders]
    })


@purchase_bp.route('/purchases', methods=['GET'])
def list_purchases():
    if 'user_id' not in session:
        return jsonify({'code':1,'msg':'请先登录'}),401
    orders = Purchase.query.all()
    return jsonify({
        'code':0,
        'purchases': [o.to_dict() for o in orders]
    })