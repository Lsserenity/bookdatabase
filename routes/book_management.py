# 书籍基本信息的数据库操作模块
from flask import session, jsonify, request, Blueprint
from database.modules import Book
from database import db

book_bp = Blueprint('book', __name__)

# 稍后在bookstore.py或routes/__init__.py中注册这个接口


# 或许可以改成post请求更加安全？
@book_bp.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    # 可以使用书籍编号、书籍ISBN号、书名、作者、出版社等方式查询库存的相关书籍。
    data = request.args  # 获取前端传来的JSON数据
    book_name = data.get('book_name')
    author = data.get('author')
    publisher = data.get('publisher')
    ISBN = data.get('ISBN')
    status = 'normal'

    filters = []
    if book_name:
        filters.append(Book.book_name.contains(book_name))
    if author:
        filters.append(Book.author.contains(author))
    if publisher:
        filters.append(Book.publisher.contains(publisher))
    if ISBN:
        filters.append(Book.ISBN.contains(ISBN))

    if not filters:
        return jsonify({
            'code': 1,
            'msg': '请至少输入一个正确的查询条件！'
        }), 400

    filters.append(Book.book_status == 'normal')
    books = Book.query.filter(*filters).all()

    if not books:
        return jsonify({
            'code': 1,
            'msg': '没有符合条件的书籍'
        }), 404

    return jsonify({
        'code': 0,
        'msg': '查询成功',
        'books': [b.to_dic() for b in books]
    })


@book_bp.route('/books/<int:book_id>', methods=['PUT'])
def modification(book_id):
    # 书籍名称、作者、出版社、零售价格
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    data = request.json

    b_name = data.get('book_name')
    b_author = data.get('author')
    b_publisher = data.get('publisher')
    b_retail_price = data.get('retail_price')

    target = Book.query.filter_by(book_id=book_id).first()

    if not target or target.book_status == 'delete':
        return jsonify({
            'code': 1,
            'msg': '没有修改目标，请输入中却的book_id'
        }), 404

    if b_name:
        target.book_name = b_name
    if b_author:
        target.author = b_author
    if b_publisher:
        target.publisher = b_publisher
    if b_retail_price:
        try:
            target.retail_price = float(b_retail_price)
        except ValueError:
            return jsonify({'code': 1, 'msg': '零售价格式错误'}), 400

    try:
        db.session.commit()
        return jsonify({'code': 0, 'msg': '修改成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': '数据库错误', 'error': str(e)}), 500
