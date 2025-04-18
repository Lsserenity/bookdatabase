from flask import session, jsonify, request, Blueprint
from datetime import datetime
from database.modules import Purchase, Book, FinancePurchaseBill, Sale, FinanceSaleBill
from database import db

finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/sale', methods=['GET'])
def sale_bill():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录!'}), 401

    data = request.args
    start_str = data.get('start_time')
    end_str = data.get('end_time')

    # 检查时间是否为空
    if not start_str or not end_str:
        return jsonify({'code': 1, 'msg': '请提供起止时间'}), 400

    try:
        start_time = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'code': 1, 'msg': '时间格式应为 YYYY-MM-DD HH:MM:SS'}), 400

    result = db.session.query(
        Book.book_id,
        Book.ISBN,
        Book.book_name,
        Book.publisher,
        Book.retail_price,
        (Book.retail_price * Sale.sale_amount).label("in")
    ).join(Sale, Sale.book_id == Book.book_id
    ).join(FinanceSaleBill, FinanceSaleBill.sale_id == Sale.sale_id
    ).filter(
        Sale.sale_time.between(start_time, end_time)
    ).all()

    return jsonify({
        'code': 0,
        'msg': '查询成功',
        'sales': [dict(zip(['book_id', 'ISBN', 'book_name', 'publisher', 'retail_price', 'in'], row)) for row in result]
    })


@finance_bp.route('/purchase', methods=['GET'])
def purchase_bill():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录!'}), 401

    data = request.args
    start_str = data.get('start_time')
    end_str = data.get('end_time')

    # 检查时间是否为空
    if not start_str or not end_str:
        return jsonify({'code': 1, 'msg': '请提供起止时间'}), 400

    try:
        start_time = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'code': 1, 'msg': '时间格式应为 YYYY-MM-DD HH:MM:SS'}), 400

    result = db.session.query(
        Book.book_id,
        Book.ISBN,
        Book.book_name,
        Book.publisher,
        Purchase.purchase_price
        (Purchase.purchase_price * Purchase.purchase_amount).label("out")
    ).join(Purchase, Purchase.book_id == Book.book_id
    ).join(FinancePurchaseBill, FinancePurchaseBill.purchase_id == Purchase.purchase_id
    ).filter(
        Purchase.create_time.between(start_time, end_time)
    ).all()

    return jsonify({
        'code': 0,
        'msg': '查询成功',
        'sales': [dict(zip(['book_id', 'ISBN', 'book_name', 'publisher', 'purchase_price', 'out'], row)) for row in result]
    })
