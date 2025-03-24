from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, SharePurchase, ShareSale, Dividend, IPOShares, BonusShares, User
from forms import BuyForm, SellForm, DividendForm, EditBuyForm, EditSellForm, EditDividendForm, IPOForm, BonusForm, RegistrationForm, LoginForm
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key

# Initialize Flask-Login and Bcrypt
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if unauthorized
db.init_app(app)
bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom template filter for date formatting
def format_date(value, format='%d-%m-%Y'):
    if value is None:
        return ""
    return value.strftime(format)

# Register the custom filter with Jinja2
app.jinja_env.filters['format_date'] = format_date

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html', current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy_share():
    form = BuyForm()
    # Fetch existing items from the database (including IPO items)
    existing_items = set()
    purchases = SharePurchase.query.all()
    sales = ShareSale.query.all()
    dividends = Dividend.query.all()
    ipos = IPOShares.query.all()  # Include IPO items
    for entry in purchases + sales + dividends + ipos:
        existing_items.add(entry.item_name)
    form.item_selection.choices = [(item, item) for item in existing_items]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_entry = SharePurchase(
            item_name=item_name,
            buy_date=form.buy_date.data,
            buy_quantity=form.buy_quantity.data,
            buy_rate=form.buy_rate.data
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Purchase added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('buy.html', form=form)

@app.route('/ipo', methods=['GET', 'POST'])
@login_required
def add_ipo():
    form = IPOForm()
    # Fetch existing items from the database
    existing_items = set()
    purchases = SharePurchase.query.all()
    sales = ShareSale.query.all()
    dividends = Dividend.query.all()
    ipos = IPOShares.query.all()
    for entry in purchases + sales + dividends + ipos:
        existing_items.add(entry.item_name)
    form.item_selection.choices = [(item, item) for item in existing_items]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_ipo = IPOShares(
            item_name=item_name,
            ipo_date=form.ipo_date.data,
            ipo_quantity=form.ipo_quantity.data,
            ipo_rate=form.ipo_rate.data
        )
        db.session.add(new_ipo)
        db.session.commit()
        flash('IPO shares added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('ipo.html', form=form)


@app.route('/bonus', methods=['GET', 'POST'])
@login_required
def add_bonus():
    form = BonusForm()
    # Fetch existing items from the database (including IPO items)
    existing_items = set()
    purchases = SharePurchase.query.all()
    sales = ShareSale.query.all()
    dividends = Dividend.query.all()
    ipos = IPOShares.query.all()
    bonuses = BonusShares.query.all()
    for entry in purchases + sales + dividends + ipos + bonuses:
        existing_items.add(entry.item_name)

    # Sort items alphabetically
    sorted_items = sorted(existing_items)
    form.item_selection.choices = [(item, item) for item in sorted_items]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_entry = BonusShares(
            item_name=item_name,
            bonus_date=form.bonus_date.data,
            bonus_quantity=form.bonus_quantity.data
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Bonus shares added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('bonus.html', form=form)

@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell_share():
    form = SellForm()
    # Fetch existing items from the database (including IPO items)
    existing_items = set()
    purchases = SharePurchase.query.all()
    sales = ShareSale.query.all()
    dividends = Dividend.query.all()
    ipos = IPOShares.query.all()  # Include IPO items
    for entry in purchases + sales + dividends + ipos:
        existing_items.add(entry.item_name)

    # Sort items alphabetically
    sorted_items = sorted(existing_items)
    form.item_selection.choices = [(item, item) for item in sorted_items]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_entry = ShareSale(
            item_name=item_name,
            sell_date=form.sell_date.data,
            sell_quantity=form.sell_quantity.data,
            sell_rate=form.sell_rate.data
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Sale added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('sell.html', form=form)


@app.route('/dividend', methods=['GET', 'POST'])
@login_required
def add_dividend():
    form = DividendForm()
    # Fetch existing items from the database (including IPO items)
    existing_items = set()
    purchases = SharePurchase.query.all()
    sales = ShareSale.query.all()
    dividends = Dividend.query.all()
    ipos = IPOShares.query.all()  # Include IPO items
    for entry in purchases + sales + dividends + ipos:
        existing_items.add(entry.item_name)

    # Sort items alphabetically
    sorted_items = sorted(existing_items)
    form.item_selection.choices = [(item, item) for item in sorted_items]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_entry = Dividend(
            item_name=item_name,
            dividend_amount=form.dividend_amount.data,
            dividend_date=form.dividend_date.data
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Dividend added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('dividend.html', form=form)

@app.route('/edit_buy/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_buy(id):
    entry = SharePurchase.query.get_or_404(id)  # Fetch the entry from the database
    form = EditBuyForm(obj=entry)  # Populate the form with the entry data
    if form.validate_on_submit():
        form.populate_obj(entry)  # Update the entry with form data
        db.session.commit()
        flash('Purchase updated successfully!', 'success')
        return redirect(url_for('report'))
    return render_template('edit_buy.html', form=form, entry=entry)  # Pass 'entry' to the template

@app.route('/edit_ipo/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ipo(id):
    entry = IPOShares.query.get_or_404(id)  # Fetch the IPO entry from the database
    form = IPOForm(obj=entry)  # Populate the form with the entry data

    if form.validate_on_submit():
        form.populate_obj(entry)  # Update the entry with form data
        db.session.commit()
        flash('IPO shares updated successfully!', 'success')
        return redirect(url_for('report'))

    return render_template('edit_ipo.html', form=form, entry=entry)

@app.route('/edit_sell/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_sell(id):
    entry = ShareSale.query.get_or_404(id)  # Fetch the entry from the database
    form = EditSellForm(obj=entry)  # Populate the form with the entry data
    if form.validate_on_submit():
        form.populate_obj(entry)  # Update the entry with form data
        db.session.commit()
        flash('Sale updated successfully!', 'success')
        return redirect(url_for('report'))
    return render_template('edit_sell.html', form=form, entry=entry)  # Pass 'entry' to the template

@app.route('/edit_dividend/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_dividend(id):
    entry = Dividend.query.get_or_404(id)  # Fetch the entry from the database
    form = EditDividendForm(obj=entry)  # Populate the form with the entry data
    if form.validate_on_submit():
        form.populate_obj(entry)  # Update the entry with form data
        db.session.commit()
        flash('Dividend updated successfully!', 'success')
        return redirect(url_for('report'))
    return render_template('edit_dividend.html', form=form, entry=entry)  # Pass 'entry' to the template

@app.route('/delete_buy/<int:id>', methods=['POST'])
@login_required
def delete_buy(id):
    entry = SharePurchase.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash('Purchase deleted successfully!', 'success')
    return redirect(url_for('report'))

@app.route('/delete_ipo/<int:id>', methods=['POST'])
@login_required
def delete_ipo(id):
    entry = IPOShares.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash('IPO shares deleted successfully!', 'success')
    return redirect(url_for('report'))

@app.route('/delete_sell/<int:id>', methods=['POST'])
@login_required
def delete_sell(id):
    entry = ShareSale.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash('Sale deleted successfully!', 'success')
    return redirect(url_for('report'))

@app.route('/delete_dividend/<int:id>', methods=['POST'])
@login_required
def delete_dividend(id):
    entry = Dividend.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash('Dividend deleted successfully!', 'success')
    return redirect(url_for('report'))

@app.route('/edit_bonus/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_bonus(id):
    entry = BonusShares.query.get_or_404(id)  # Fetch the bonus entry from the database
    form = BonusForm(obj=entry)  # Populate the form with the entry data

    if form.validate_on_submit():
        form.populate_obj(entry)  # Update the entry with form data
        db.session.commit()
        flash('Bonus shares updated successfully!', 'success')
        return redirect(url_for('report'))
    return render_template('edit_bonus.html', form=form, entry=entry)

@app.route('/delete_bonus/<int:id>', methods=['POST'])
@login_required
def delete_bonus(id):
    entry = BonusShares.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash('Bonus shares deleted successfully!', 'success')
    return redirect(url_for('report'))

@app.route('/get_previous_records')
def get_previous_records():
    item_name = request.args.get('item_name')
    purchases = SharePurchase.query.filter_by(item_name=item_name).all()
    sales = ShareSale.query.filter_by(item_name=item_name).all()
    dividends = Dividend.query.filter_by(item_name=item_name).all()

    previous_records = {
        'purchases': [{'buy_date': p.buy_date, 'buy_quantity': p.buy_quantity, 'buy_rate': p.buy_rate} for p in purchases],
        'sales': [{'sell_date': s.sell_date, 'sell_quantity': s.sell_quantity, 'sell_rate': s.sell_rate} for s in sales],
        'dividends': [{'dividend_amount': d.dividend_amount} for d in dividends]
    }

    return jsonify(previous_records)

@app.route('/report')
@login_required
def report():
    item_name = request.args.get('item_name', 'all')  # Default to 'all' if no item is selected
    report_type = request.args.get('report_type', 'all')  # Default to 'all' if no report type is selected

    # Fetch all purchases, sales, dividends, IPOs, and bonus shares
    all_purchases = SharePurchase.query.order_by(SharePurchase.buy_date.asc()).all()
    all_sales = ShareSale.query.order_by(ShareSale.sell_date.asc()).all()
    all_dividends = Dividend.query.all()
    all_ipos = IPOShares.query.order_by(IPOShares.ipo_date.asc()).all()
    all_bonuses = BonusShares.query.order_by(BonusShares.bonus_date.asc()).all()

    # Initialize filtered lists
    purchases = []
    sales = []
    dividends = []
    ipos = []
    bonuses = []

    # Apply item filter
    if item_name != "all":
        # Filter by item name
        purchases = [p for p in all_purchases if p.item_name == item_name]
        sales = [s for s in all_sales if s.item_name == item_name]
        dividends = [d for d in all_dividends if d.item_name == item_name]
        ipos = [i for i in all_ipos if i.item_name == item_name]
        bonuses = [b for b in all_bonuses if b.item_name == item_name]
    else:
        # If no item is selected, use all data
        purchases = all_purchases
        sales = all_sales
        dividends = all_dividends
        ipos = all_ipos
        bonuses = all_bonuses

    # Apply report type filter
    if report_type != "all":
        if report_type == "purchases":
            sales, dividends, ipos, bonuses = [], [], [], []
        elif report_type == "sales":
            purchases, dividends, ipos, bonuses = [], [], [], []
        elif report_type == "dividends":
            purchases, sales, ipos, bonuses = [], [], [], []
        elif report_type == "ipos":
            purchases, sales, dividends, bonuses = [], [], [], []
        elif report_type == "bonuses":
            purchases, sales, dividends, ipos = [], [], [], []
        elif report_type == "item_summary":
            # Show only Item Summary (no need to filter other data)
            pass
        elif report_type == "profit_loss":
            # Show only Profit/Loss Summary (no need to filter other data)
            pass

    # Calculate totals with commission for purchases and without commission for IPOs
    item_summary = {}
    for purchase in purchases:
        if purchase.item_name not in item_summary:
            item_summary[purchase.item_name] = {
                'total_buy_quantity': 0,
                'total_buy_cost_with_commission': 0,
                'total_sell_quantity': 0,
                'total_sell_cost_with_commission': 0,
                'total_dividend': 0,
                'total_ipo_quantity': 0,
                'total_ipo_cost': 0,
                'total_bonus_quantity': 0
            }
        item_summary[purchase.item_name]['total_buy_quantity'] += purchase.buy_quantity
        item_summary[purchase.item_name]['total_buy_cost_with_commission'] += purchase.buy_quantity * purchase.buy_rate * 1.004

    for ipo in ipos:
        if ipo.item_name not in item_summary:
            item_summary[ipo.item_name] = {
                'total_buy_quantity': 0,
                'total_buy_cost_with_commission': 0,
                'total_sell_quantity': 0,
                'total_sell_cost_with_commission': 0,
                'total_dividend': 0,
                'total_ipo_quantity': 0,
                'total_ipo_cost': 0,
                'total_bonus_quantity': 0
            }
        item_summary[ipo.item_name]['total_ipo_quantity'] += ipo.ipo_quantity
        item_summary[ipo.item_name]['total_ipo_cost'] += ipo.ipo_quantity * ipo.ipo_rate

    for sale in sales:
        if sale.item_name not in item_summary:
            item_summary[sale.item_name] = {
                'total_buy_quantity': 0,
                'total_buy_cost_with_commission': 0,
                'total_sell_quantity': 0,
                'total_sell_cost_with_commission': 0,
                'total_dividend': 0,
                'total_ipo_quantity': 0,
                'total_ipo_cost': 0,
                'total_bonus_quantity': 0
            }
        item_summary[sale.item_name]['total_sell_quantity'] += sale.sell_quantity
        item_summary[sale.item_name]['total_sell_cost_with_commission'] += sale.sell_quantity * sale.sell_rate * 0.996

    for dividend in dividends:
        if dividend.item_name not in item_summary:
            item_summary[dividend.item_name] = {
                'total_buy_quantity': 0,
                'total_buy_cost_with_commission': 0,
                'total_sell_quantity': 0,
                'total_sell_cost_with_commission': 0,
                'total_dividend': 0,
                'total_ipo_quantity': 0,
                'total_ipo_cost': 0,
                'total_bonus_quantity': 0
            }
        item_summary[dividend.item_name]['total_dividend'] += dividend.dividend_amount

    for bonus in bonuses:
        if bonus.item_name not in item_summary:
            item_summary[bonus.item_name] = {
                'total_buy_quantity': 0,
                'total_buy_cost_with_commission': 0,
                'total_sell_quantity': 0,
                'total_sell_cost_with_commission': 0,
                'total_dividend': 0,
                'total_ipo_quantity': 0,
                'total_ipo_cost': 0,
                'total_bonus_quantity': 0
            }
        item_summary[bonus.item_name]['total_bonus_quantity'] += bonus.bonus_quantity

    # Get unique item names for the dropdown (always fetch all unique items)
    unique_items = set()
    for entry in all_purchases + all_sales + all_dividends + all_ipos + all_bonuses:
        unique_items.add(entry.item_name)
    unique_items = sorted(unique_items)

    return render_template(
        'report.html',
        purchases=purchases,
        sales=sales,
        dividends=dividends,
        ipos=ipos,
        bonuses=bonuses,
        item_summary=item_summary,
        unique_items=unique_items,
        selected_item=item_name,
        selected_report_type=report_type
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)