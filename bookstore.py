# 经典的，痛苦的，一针见血的，边学边开发

from flask import Flask
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
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()


with app.app_context():
    db.create_all()
    init_super()


@app.route('/')
def index():
    return "欢迎使用本书籍管理系统！"


if __name__ == '__main__':
    app.run(debug=True)
