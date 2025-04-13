# 经典的，痛苦的，一针见血的，边学边开发

from flask import Flask
from config import Config    # 从配置文件读取数据库URI
from database.__init__ import db
from database.modules import User, Book, Purchase, Sale, FinanceSaleBill, FinancePurchaseBill


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)    # 将数据库连接到Flask

with app.app_context():
    db.create_all()

    # 超级用户在数据库创建时就存在
    if not User.query.filter_by(user_name='admin').first():
        admin = User(
            user_id=0,
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

if __name__ == '__main__':
    app.run(debug=True)
