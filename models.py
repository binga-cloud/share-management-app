from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class SharePurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_purchase_user'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    buy_date = db.Column(db.Date, nullable=False)  # Change to db.Date
    buy_quantity = db.Column(db.Integer, nullable=False)
    buy_rate = db.Column(db.Float, nullable=False)

class ShareSale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_purchase_user'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    sell_date = db.Column(db.Date, nullable=False)  # Change to db.Date
    sell_quantity = db.Column(db.Integer, nullable=False)
    sell_rate = db.Column(db.Float, nullable=False)

class Dividend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_purchase_user'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    dividend_amount = db.Column(db.Float, nullable=False)
    dividend_date = db.Column(db.Date, nullable=False)

class IPOShares(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_purchase_user'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    ipo_date = db.Column(db.Date, nullable=False)  # IPO purchase date
    ipo_quantity = db.Column(db.Integer, nullable=False)  # IPO share quantity
    ipo_rate = db.Column(db.Float, nullable=False)  # IPO share rate

class BonusShares(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_purchase_user'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    bonus_date = db.Column(db.Date, nullable=False)  # Date of bonus shares
    bonus_quantity = db.Column(db.Integer, nullable=False)  # Quantity of bonus shares

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
