# init_db.py

from bookstore import app, db
from database.modules import User, Book, Purchase, Sale, FinancePurchaseBill, FinanceSaleBill  # 你自己的模型，可以根据需要添加
import sys

def init_data():
    with app.app_context():
        print("🔄 正在重建数据库...")
        db.drop_all()
        db.create_all()

        print("✅ 数据库表已重建，开始插入初始数据...")

        # 创建一个超级用户（示例）
        admin = User(
            user_type='super',
            name='超级用户',
            job_num='000000',
            user_name='admin',
            gender='other',
            age=0
        )
        admin.set_password('2345610')  # 注意使用你模型中的 set_password 方法
        db.session.add(admin)
        db.session.commit()

        xiaoming = User(
            user_type='normal',
            name='小明',
            job_num='234151',
            user_name='xiaoming',
            gender='male',
            age=27
        )
        xiaoming.set_password('2345610')  # 注意使用你模型中的 set_password 方法
        db.session.add(xiaoming)
        db.session.commit()

        # 示例图书（你可以自由扩展）
        book1 = Book(
            ISBN='9787302440192',
            book_name='信息论与编码',
            author='曹雪虹、张宗橙',
            publisher='清华大学出版社',
            retail_price=39.0,
            quantity=10,
            book_status='normal'
        )
        db.session.add(book1)
        db.session.commit()

        # 示例订单
        purchase1 = Purchase(
            book_id=book1.book_id,
            purchase_amount=10,
            purchase_price=15.0,
            purchase_status='paid',
            operator_id=admin.user_id,
            onstage='yes'
        )
        db.session.add(purchase1)
        db.session.commit()
        print("✅ 初始化完成！")

if __name__ == '__main__':
    init_data()
