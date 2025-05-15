# 数据库定义
from sqlalchemy import UnicodeText
from sqlalchemy.orm import relationship
from hashlib import md5
from datetime import datetime
from sqlalchemy import ForeignKey
from .import db

class User(db.Model):

    user_id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum('super', 'normal', name='user_type'), nullable=False)
    name = db.Column(UnicodeText(), nullable=False)
    job_num = db.Column(db.String(6), unique=True, nullable=False)
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'other', name='gender'), nullable=False)
    age = db.Column(db.Integer, db.CheckConstraint('age >= 0'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = md5(password.encode()).hexdigest()

    def check_password(self, password):
        return self.password_hash == md5(password.encode()).hexdigest()


class Book(db.Model):

    book_id = db.Column(db.Integer, primary_key=True)
    ISBN = db.Column(db.String(13), unique=True, nullable=False, index=True)
    book_name = db.Column(UnicodeText(), nullable=False, index=True)
    publisher = db.Column(UnicodeText(), nullable=False, index=True)
    author = db.Column(UnicodeText(), nullable=False, index=True)
    retail_price = db.Column(db.Numeric(5, 2), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    book_status = db.Column(db.Enum('normal', 'delete', 'offstage', name='book_status'), default='offstage', nullable=False)
    # 购买时候如果需要撤销的时候检查是否为之前没有的book的回滚函数

    def rollback_if_empty(self):
        if self.book_status == 'offstage':
            self.book_status = 'delete'
            db.session.commit()


    def to_dic(self):
        book = {
            'book_id': self.book_id,
            'ISBN': self.ISBN,
            'book_name': self.book_name,
            'publisher': self.publisher,
            'author': self.author,
            'retail_price': self.retail_price,
            'quantity': self.quantity
        }

        return book


class Purchase(db.Model):

    purchase_id = db.Column(db.Integer(), primary_key=True)
    book_id = db.Column(db.Integer(), ForeignKey('book.book_id'))
    purchase_price = db.Column(db.Numeric(5, 2), nullable=False)
    purchase_amount = db.Column(db.Integer(), nullable=False)
    purchase_status = db.Column(db.Enum('unpaid', 'paid', 'returned', name='purchase_status'), nullable=False, default='unpaid')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    operator_id = db.Column(db.Integer(), ForeignKey('user.user_id'), nullable=False)
    onstage = db.Column(db.Enum('no', 'yes', name='onstage'), nullable=False, default='no')
    book = relationship('Book', lazy='joined')

    def to_dict(self):
        return {
            'purchase_id': self.purchase_id,
            'book_id': self.book_id,
            'purchase_price': self.purchase_price,
            'purchase_amount': self.purchase_amount,
            'purchase_status': self.purchase_status,
            'create_time': self.create_time,
            'operator_id': self.operator_id,
            'onstage': self.onstage,
            'book': self.book.to_dic() 
        }


class Sale(db.Model):

    sale_id = db.Column(db.Integer(), primary_key=True)
    book_id = db.Column(db.Integer(), ForeignKey('book.book_id'), nullable=False)
    sale_amount = db.Column(db.Integer(), nullable=False)
    sale_time = db.Column(db.DateTime, default=datetime.utcnow)


class FinanceSaleBill(db.Model):

    fsbill_id = db.Column(db.Integer(), primary_key=True)
    sale_id = db.Column(db.Integer(), ForeignKey('sale.sale_id'))


class FinancePurchaseBill(db.Model):

    fpbill_id = db.Column(db.Integer(), primary_key=True)
    purchase_id = db.Column(db.Integer(), ForeignKey('purchase.purchase_id'))
