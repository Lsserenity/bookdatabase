# 经典的，痛苦的，一针见血的，边学边开发

from flask import Flask, render_template, redirect, session
from config import Config    # 从配置文件读取数据库URI
from database import db

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'a_random_secret_key_!@#536187253'  # 可以自己换成更复杂更安全的
db.init_app(app)    # 将数据库连接到Flask

from database.modules import User
from routes import user_bp, book_bp, purchase_bp, finance_bp

app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(book_bp, url_prefix='/api/book')
app.register_blueprint(purchase_bp, url_prefix='/api/purchase')
app.register_blueprint(finance_bp, url_prefix='/api/finance')

print(f"[bookstore] db id: {id(db)}")


def init_super():
    with app.app_context():
        if not User.query.filter_by(user_name='admin').first():
            admin = User(
                user_type='super',
                name='超级用户',
                job_num='000000',
                user_name='admin',
                gender='other',
                age=0
            )
            admin.set_password('2345610')
            db.session.add(admin)
            db.session.commit()


with app.app_context():
    db.create_all()
    init_super()


@app.route('/')
def login_page():
    return render_template('login.html')


# 主页路由
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/')  # 如果没登录，跳回登录页
    # 取用户名传给模板
    username = session.get('user_name', '未知用户')
    return render_template('home.html', username=username)


@app.route('/user')
def user_page():
    return render_template('user.html')

@app.route('/books')
def book_page():
    return render_template('book.html')

@app.route('/inventory')
def inventory_page():
    return render_template('inventory.html')

if __name__ == '__main__':
    app.run(debug=True)
