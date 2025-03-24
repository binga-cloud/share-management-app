from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, DateField, SelectField, PasswordField
from wtforms.validators import DataRequired, Optional, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class BuyForm(FlaskForm):
    item_selection = SelectField('Select Item', choices=[], validators=[Optional()])  # Dropdown for existing items
    item_name = StringField('Or Enter New Item Name', validators=[Optional()])  # Manual entry for new items
    buy_date = DateField('Buy Date', format='%Y-%m-%d', validators=[DataRequired()])
    buy_quantity = IntegerField('Buy Quantity', validators=[DataRequired()])
    buy_rate = FloatField('Buy Rate', validators=[DataRequired()])
    submit = SubmitField('Buy')

class IPOForm(FlaskForm):
    item_selection = SelectField('Select Item', choices=[], validators=[Optional()])  # Dropdown for existing items
    item_name = StringField('Or Enter New Item Name', validators=[Optional()])  # Manual entry for new items
    ipo_date = DateField('IPO Date', format='%Y-%m-%d', validators=[DataRequired()])
    ipo_quantity = IntegerField('IPO Quantity', validators=[DataRequired()])
    ipo_rate = FloatField('IPO Rate', validators=[DataRequired()])
    submit = SubmitField('Add IPO Shares')

class SellForm(FlaskForm):
    item_selection = SelectField('Select Item', choices=[], validators=[Optional()])  # Dropdown for existing items
    item_name = StringField('Or Enter New Item Name', validators=[Optional()])  # Manual entry for new items
    sell_date = DateField('Sell Date', format='%Y-%m-%d', validators=[DataRequired()])
    sell_quantity = IntegerField('Sell Quantity', validators=[DataRequired()])
    sell_rate = FloatField('Sell Rate', validators=[DataRequired()])
    submit = SubmitField('Sell')

class DividendForm(FlaskForm):
    item_selection = SelectField('Select Item', choices=[], validators=[Optional()])  # Dropdown for existing items
    item_name = StringField('Or Enter New Item Name', validators=[Optional()])  # Manual entry for new items
    dividend_amount = FloatField('Dividend Amount', validators=[DataRequired()])
    dividend_date = DateField('Dividend Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Add Dividend')

class EditBuyForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    buy_date = DateField('Buy Date', format='%Y-%m-%d', validators=[DataRequired()])  # Ensure DateField
    buy_quantity = IntegerField('Buy Quantity', validators=[DataRequired()])
    buy_rate = FloatField('Buy Rate', validators=[DataRequired()])
    submit = SubmitField('Update')

class EditSellForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    sell_date = DateField('Sell Date', format='%Y-%m-%d', validators=[DataRequired()])  # Ensure DateField
    sell_quantity = IntegerField('Sell Quantity', validators=[DataRequired()])
    sell_rate = FloatField('Sell Rate', validators=[DataRequired()])
    submit = SubmitField('Update')

class EditDividendForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    dividend_amount = FloatField('Dividend Amount', validators=[DataRequired()])
    submit = SubmitField('Update')

class BonusForm(FlaskForm):
    item_selection = SelectField('Select Item', choices=[], validators=[Optional()])  # Dropdown for existing items
    item_name = StringField('Or Enter New Item Name', validators=[Optional()])  # Manual entry for new items
    bonus_date = DateField('Bonus Date', format='%Y-%m-%d', validators=[DataRequired()])  # Date of bonus shares
    bonus_quantity = IntegerField('Bonus Quantity', validators=[DataRequired()])  # Quantity of bonus shares
    submit = SubmitField('Add Bonus Shares')

class EditBonusForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    bonus_date = DateField('Bonus Date', format='%Y-%m-%d', validators=[DataRequired()])  # ISO format
    bonus_quantity = IntegerField('Bonus Quantity', validators=[DataRequired()])
    submit = SubmitField('Update')
