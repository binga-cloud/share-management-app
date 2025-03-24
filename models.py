from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SharePurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    buy_date = db.Column(db.Date, nullable=False)  # Change to db.Date
    buy_quantity = db.Column(db.Integer, nullable=False)
    buy_rate = db.Column(db.Float, nullable=False)

class ShareSale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    sell_date = db.Column(db.Date, nullable=False)  # Change to db.Date
    sell_quantity = db.Column(db.Integer, nullable=False)
    sell_rate = db.Column(db.Float, nullable=False)

class Dividend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    dividend_amount = db.Column(db.Float, nullable=False)
    dividend_date = db.Column(db.Date, nullable=False)

class IPOShares(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    ipo_date = db.Column(db.Date, nullable=False)  # IPO purchase date
    ipo_quantity = db.Column(db.Integer, nullable=False)  # IPO share quantity
    ipo_rate = db.Column(db.Float, nullable=False)  # IPO share rate

class BonusShares(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    bonus_date = db.Column(db.Date, nullable=False)  # Date of bonus shares
    bonus_quantity = db.Column(db.Integer, nullable=False)  # Quantity of bonus shares

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
