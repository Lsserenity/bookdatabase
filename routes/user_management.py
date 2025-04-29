from flask import session, jsonify, request, Blueprint
from database.modules import User
from database import db

user_bp = Blueprint('user', __name__)
# 稍后在bookstore.py或routes/__init__.py中注册这个接口


# 用户登录接口，将信息存入session
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json  # 获取前端传来的JSON数据

    # 获取用户名和密码
    username = data.get('user_name')
    password = data.get('password')

    # 在数据库中查找用户
    user = User.query.filter_by(user_name=username).first()

    if user and user.check_password(password):
        # 登录成功，写入session
        session['user_id'] = user.user_id
        # session['user_status'] = 'on'
        session['user_name'] = user.user_name
        session['user_type'] = user.user_type
        # 是否需要将该用户的所有信息都载入session？还是检测到查找需要再查找数据库，载入？

        return jsonify({
            'code': 0,
            'msg': "登录成功",
            'user_type': user.user_type,
            'user_id': user.user_id
        })
    else:
        # 登陆失败
        return jsonify({
            'code': 1,
            'msg': '用户名或密码错误'
        }), 401


# 检查当前登录的用户时super还是normal
@user_bp.route('/me', methods=['GET'])
def get_me():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '未登录'}), 401

    user = User.query.get(session['user_id'])

    return jsonify({
        'code': 0,
        'user_id': user.user_id,
        'user_name': user.user_name,
        'user_type': user.user_type,
        'name': user.name,
        'job_number': user.job_num,
        'gender': user.gender,
        'age': user.age,
        'created_time': user.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })


# 用户登出接口，清除session信息
@user_bp.route('/logout', methods=['POST'])
def logout():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    session.clear()

    return jsonify({
        'code': 0,
        'msg': '已退出登录！'
    })


# super用户注册新用户
@user_bp.route('/register', methods=['POST'])
def register():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    if session['user_type'] != 'super':
        return jsonify({'code': 1, 'msg': '用户权限不足'}), 402

    data = request.json  # 获取前端传来的JSON数据

    username = data.get('user_name')
    password = data.get('password')
    name = data.get('name')
    job_num = data.get('job_number')
    gender = data.get('gender')
    age = data.get('age')

    if User.query.filter_by(user_name=username).first():
        return jsonify({'code': 1, 'msg': '用户名已存在！'}), 400

    if len(job_num) != 6 or not job_num.isdigit():
        return jsonify({'code': 1, 'msg': '工号必须为6位数字'}), 400

    user = User(
        user_type='normal',
        name=name,
        job_num=job_num,
        user_name=username,
        gender=gender,
        age=age
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'code': 0, 'msg': '注册成功'})


# super用户查看所有用户的信息
@user_bp.route('/all_users', methods=['GET'])
def all_users():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    if session['user_type'] != 'super':
        return jsonify({'code': 1, 'msg': '用户权限不足'}), 402

    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            'user_id': user.user_id,
            'user_name': user.user_name,
            'user_type': user.user_type,
            'name': user.name,
            'job_num': user.job_num,
            'gender': user.gender,
            'age': user.age
        })

    return jsonify({
        'code': 0,
        'msg': '获取成功',
        'users': user_list
    })


# 根据用户类型分配对应的修改用户信息的权限
@user_bp.route('/update', methods=['POST'])
def update():

    data = request.json

    username = data.get('user_name')
    # password = data.get('password')
    name = data.get('name')
    job_num = data.get('job_number')
    gender = data.get('gender')
    age = data.get('age')
    userid = data.get('user_id')

    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录！'}), 401

    if userid != session['user_id'] and session['user_type'] != 'super':
        return jsonify({'code': 1, 'msg': '用户权限不足！'}), 402

    user = User.query.filter_by(user_id=userid).first()

    if not user:
        return jsonify({'code': 1, 'msg': '用户不存在！'}), 404

    user.user_name = username
    user.name = name
    user.job_num = job_num
    user.gender = gender
    user.age = age
    # user.set_password(password)

    db.session.commit()

    return jsonify({'code': 0, 'msg': '修改成功'})


# super用户删除某个用户
@user_bp.route('/delete_user', methods=['DELETE'])
def delete_user():

    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'}), 401

    if session['user_type'] != 'super':
        return jsonify({'code': 1, 'msg': '用户权限不足'}), 402

    data = request.json
    userid = data['user_id']

    user = User.query.filter_by(user_id=userid).first()

    if not user:
        return jsonify({'code': 1, 'msg': '用户不存在！'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'code': 0, 'msg': '删除成功'})


# 重置密码
@user_bp.route('/reset_password', methods=['POST'])
def reset_password():

    data = request.json

    username = data.get('user_name')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录！'}), 401

    user = User.query.filter_by(user_name=username).first()

    if not user:
        return jsonify({'code': 1, 'msg': '用户不存在！'}), 404

    if user.user_id != session['user_id'] and session['user_type'] != 'super':
        return jsonify({'code': 1, 'msg': '用户权限不足！'}), 402

    if user.check_password(old_password) and not user.check_password(new_password):
        user.set_password(new_password)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '密码修改成功！'})

    elif not user.check_password(old_password):
        return jsonify({'code': 1, 'msg': '请输入正确的旧密码！'}), 404
    else:
        return jsonify({'code': 1, 'msg': '新密码不可与原密码相同！'}), 400
