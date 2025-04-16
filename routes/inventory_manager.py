# 进货，退货，添加图书
# 图书进货：对于需要进货的书籍，
# 如果库存中曾经有这本书的信息的话，则直接将这本书的ID列入进货清单，
# 否则需要输入进货书籍的相关信息，包括ISBN号，书名，作者，出版社等。
# 此外，每种书都要指定其进货价格和购买数量。
# 对于刚列入进货清单的书籍给予未付款状态。

# purchase_list(purchase_id, book_id, purchase_price,
# purchase_amount, purchase_status, create_time, operator_id);

from flask import session, jsonify, request, Blueprint
from database.modules import Purchase, Book
from database import db

purchase_bp = Blueprint('purchase', __name__)


@purchase_bp.route('/buy/<int:book_id>', methods=['POST'])
def buy(book_id):
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    book = Book.query.get(book_id)

    if not book:
        return jsonify({'code': 1, 'msg': '该图书不存在，请新建购买信息！'}), 404

    data = request.json
    price = data.get('purchase_price')
    amount = data.get('purchase_amount')

    if not price or not amount:
        return jsonify({'code': 1, 'msg': '缺少价格或数量'}), 400

    try:
        price = float(price)
        amount = int(amount)
    except ValueError:
        return jsonify({'code': 1, 'msg': '价格或数量格式错误'}), 400

    purchase = Purchase(
        book_id=book_id,
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
        return jsonify({'code': 1, 'msg': '请输入完整的书籍信息！'})

    if Book.query.filter_by(ISBN=isbn).first():
        return jsonify({'code': 1, 'msg': '该书籍信息已存在，请直接购买！'})

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

    purchase = Purchase(
        book_id=book.book_id,
        purchase_price=price,
        purchase_amount=amount,
        purchase_status='unpaid',
        # create_time 会默认生成
        operator_id=session['user_id']
    )

    try:
        db.session.add(book)
        db.session.flush()
        db.session.add(purchase)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '新书信息添加成功！\n进货信息添加成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': '数据库错误', 'error': str(e)}), 500
