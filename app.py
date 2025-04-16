from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, SharePurchase, ShareSale, Dividend, IPOShares, BonusShares, User
from forms import BuyForm, SellForm, DividendForm, EditBuyForm, EditSellForm, EditDividendForm, IPOForm, BonusForm, \
    RegistrationForm, LoginForm, ChangePasswordForm
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key

# Initialize Flask-Login and Bcrypt
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Custom template filter for date formatting
def format_date(value, format='%d-%m-%Y'):
    if value is None:
        return ""
    return value.strftime(format)


app.jinja_env.filters['format_date'] = format_date

# Initialize database and create admin user
with app.app_context():
    db.create_all()
    # Create admin if not exists
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", is_admin=True)
        admin.set_password("admin123")  # Change this password!
        db.session.add(admin)
        db.session.commit()
        # Assign all existing data to admin
        for model in [SharePurchase, ShareSale, Dividend, IPOShares, BonusShares]:
            for record in model.query.filter_by(user_id=None).all():
                record.user_id = admin.id
            db.session.commit()

# ========================
# AUTHENTICATION ROUTES
# ========================

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

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Current password is incorrect.', 'danger')
    return render_template('change_password.html', form=form)

# ========================
# TRANSACTION ROUTES (ALL UPDATED)
# ========================

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy_share():
    form = BuyForm()
    # Get only current user's items
    existing_items = set()
    purchases = SharePurchase.query.filter_by(user_id=current_user.id).all()
    sales = ShareSale.query.filter_by(user_id=current_user.id).all()
    dividends = Dividend.query.filter_by(user_id=current_user.id).all()
    ipos = IPOShares.query.filter_by(user_id=current_user.id).all()

    for entry in purchases + sales + dividends + ipos:
        existing_items.add(entry.item_name)
    form.item_selection.choices = [(item, item) for item in existing_items]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_entry = SharePurchase(
            user_id=current_user.id,
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


@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell_share():
    form = SellForm()
    # Get only current user's items
    existing_items = set()
    purchases = SharePurchase.query.filter_by(user_id=current_user.id).all()
    sales = ShareSale.query.filter_by(user_id=current_user.id).all()
    dividends = Dividend.query.filter_by(user_id=current_user.id).all()
    ipos = IPOShares.query.filter_by(user_id=current_user.id).all()

    for entry in purchases + sales + dividends + ipos:
        existing_items.add(entry.item_name)
    form.item_selection.choices = [(item, item) for item in sorted(existing_items)]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_entry = ShareSale(
            user_id=current_user.id,
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
    # Get only current user's items
    existing_items = set()
    purchases = SharePurchase.query.filter_by(user_id=current_user.id).all()
    sales = ShareSale.query.filter_by(user_id=current_user.id).all()
    dividends = Dividend.query.filter_by(user_id=current_user.id).all()
    ipos = IPOShares.query.filter_by(user_id=current_user.id).all()

    for entry in purchases + sales + dividends + ipos:
        existing_items.add(entry.item_name)
    form.item_selection.choices = [(item, item) for item in sorted(existing_items)]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_entry = Dividend(
            user_id=current_user.id,
            item_name=item_name,
            dividend_amount=form.dividend_amount.data,
            dividend_date=form.dividend_date.data
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Dividend added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('dividend.html', form=form)


@app.route('/ipo', methods=['GET', 'POST'])
@login_required
def add_ipo():
    form = IPOForm()
    # Get only current user's items
    existing_items = set()
    purchases = SharePurchase.query.filter_by(user_id=current_user.id).all()
    sales = ShareSale.query.filter_by(user_id=current_user.id).all()
    dividends = Dividend.query.filter_by(user_id=current_user.id).all()
    ipos = IPOShares.query.filter_by(user_id=current_user.id).all()

    for entry in purchases + sales + dividends + ipos:
        existing_items.add(entry.item_name)
    form.item_selection.choices = [(item, item) for item in existing_items]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_ipo = IPOShares(
            user_id=current_user.id,
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
    # Get only current user's items
    existing_items = set()
    purchases = SharePurchase.query.filter_by(user_id=current_user.id).all()
    sales = ShareSale.query.filter_by(user_id=current_user.id).all()
    dividends = Dividend.query.filter_by(user_id=current_user.id).all()
    ipos = IPOShares.query.filter_by(user_id=current_user.id).all()
    bonuses = BonusShares.query.filter_by(user_id=current_user.id).all()

    for entry in purchases + sales + dividends + ipos + bonuses:
        existing_items.add(entry.item_name)
    form.item_selection.choices = [(item, item) for item in sorted(existing_items)]

    if form.validate_on_submit():
        item_name = form.item_selection.data if form.item_selection.data else form.item_name.data
        new_entry = BonusShares(
            user_id=current_user.id,
            item_name=item_name,
            bonus_date=form.bonus_date.data,
            bonus_quantity=form.bonus_quantity.data
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Bonus shares added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('bonus.html', form=form)


# ========================
# EDIT/DELETE ROUTES (UPDATED)
# ========================

@app.route('/edit_buy/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_buy(id):
    entry = SharePurchase.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = EditBuyForm(obj=entry)
    if form.validate_on_submit():
        form.populate_obj(entry)
        db.session.commit()
        flash('Purchase updated successfully!', 'success')
        return redirect(url_for('report'))
    return render_template('edit_buy.html', form=form, entry=entry)


@app.route('/edit_sell/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_sell(id):
    entry = ShareSale.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = EditSellForm(obj=entry)
    if form.validate_on_submit():
        form.populate_obj(entry)
        db.session.commit()
        flash('Sale updated successfully!', 'success')
        return redirect(url_for('report'))
    return render_template('edit_sell.html', form=form, entry=entry)


@app.route('/edit_dividend/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_dividend(id):
    entry = Dividend.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = EditDividendForm(obj=entry)
    if form.validate_on_submit():
        form.populate_obj(entry)
        db.session.commit()
        flash('Dividend updated successfully!', 'success')
        return redirect(url_for('report'))
    return render_template('edit_dividend.html', form=form, entry=entry)


@app.route('/edit_ipo/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ipo(id):
    entry = IPOShares.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = IPOForm(obj=entry)
    if form.validate_on_submit():
        form.populate_obj(entry)
        db.session.commit()
        flash('IPO shares updated successfully!', 'success')
        return redirect(url_for('report'))
    return render_template('edit_ipo.html', form=form, entry=entry)


@app.route('/edit_bonus/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_bonus(id):
    entry = BonusShares.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = BonusForm(obj=entry)
    if form.validate_on_submit():
        form.populate_obj(entry)
        db.session.commit()
        flash('Bonus shares updated successfully!', 'success')
        return redirect(url_for('report'))
    return render_template('edit_bonus.html', form=form, entry=entry)


@app.route('/delete_buy/<int:id>', methods=['POST'])
@login_required
def delete_buy(id):
    entry = SharePurchase.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash('Purchase deleted successfully!', 'success')
    return redirect(url_for('report'))


@app.route('/delete_sell/<int:id>', methods=['POST'])
@login_required
def delete_sell(id):
    entry = ShareSale.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash('Sale deleted successfully!', 'success')
    return redirect(url_for('report'))


@app.route('/delete_dividend/<int:id>', methods=['POST'])
@login_required
def delete_dividend(id):
    entry = Dividend.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash('Dividend deleted successfully!', 'success')
    return redirect(url_for('report'))


@app.route('/delete_ipo/<int:id>', methods=['POST'])
@login_required
def delete_ipo(id):
    entry = IPOShares.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash('IPO shares deleted successfully!', 'success')
    return redirect(url_for('report'))


@app.route('/delete_bonus/<int:id>', methods=['POST'])
@login_required
def delete_bonus(id):
    entry = BonusShares.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash('Bonus shares deleted successfully!', 'success')
    return redirect(url_for('report'))


# ========================
# ADMIN ROUTES
# ========================

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete admin!', 'danger')
    else:
        # Delete user's data
        for model in [SharePurchase, ShareSale, Dividend, IPOShares, BonusShares]:
            model.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash('User deleted!', 'success')
    return redirect(url_for('admin_users'))


# ========================
# REPORT ROUTE (FULLY UPDATED)
# ========================

@app.route('/report')
@login_required
def report():
    item_name = request.args.get('item_name', 'all')
    report_type = request.args.get('report_type', 'all')

    # Fetch data based on user role
    if current_user.is_admin:
        all_purchases = SharePurchase.query.order_by(SharePurchase.buy_date.asc()).all()
        all_sales = ShareSale.query.order_by(ShareSale.sell_date.asc()).all()
        all_dividends = Dividend.query.all()
        all_ipos = IPOShares.query.order_by(IPOShares.ipo_date.asc()).all()
        all_bonuses = BonusShares.query.order_by(BonusShares.bonus_date.asc()).all()
    else:
        all_purchases = SharePurchase.query.filter_by(user_id=current_user.id).order_by(
            SharePurchase.buy_date.asc()).all()
        all_sales = ShareSale.query.filter_by(user_id=current_user.id).order_by(ShareSale.sell_date.asc()).all()
        all_dividends = Dividend.query.filter_by(user_id=current_user.id).all()
        all_ipos = IPOShares.query.filter_by(user_id=current_user.id).order_by(IPOShares.ipo_date.asc()).all()
        all_bonuses = BonusShares.query.filter_by(user_id=current_user.id).order_by(BonusShares.bonus_date.asc()).all()

    # Apply item filter
    if item_name != "all":
        purchases = [p for p in all_purchases if p.item_name == item_name]
        sales = [s for s in all_sales if s.item_name == item_name]
        dividends = [d for d in all_dividends if d.item_name == item_name]
        ipos = [i for i in all_ipos if i.item_name == item_name]
        bonuses = [b for b in all_bonuses if b.item_name == item_name]
    else:
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

    # Calculate item summary (same as before but user-specific)
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
        item_summary[purchase.item_name][
            'total_buy_cost_with_commission'] += purchase.buy_quantity * purchase.buy_rate * 1.004

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

    # Get unique items for dropdown
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


# ========================
# ADDITIONAL ROUTES
# ========================

@app.route('/get_previous_records')
def get_previous_records():
    item_name = request.args.get('item_name')
    purchases = SharePurchase.query.filter_by(item_name=item_name, user_id=current_user.id).all()
    sales = ShareSale.query.filter_by(item_name=item_name, user_id=current_user.id).all()
    dividends = Dividend.query.filter_by(item_name=item_name, user_id=current_user.id).all()

    previous_records = {
        'purchases': [{'buy_date': p.buy_date, 'buy_quantity': p.buy_quantity, 'buy_rate': p.buy_rate} for p in
                      purchases],
        'sales': [{'sell_date': s.sell_date, 'sell_quantity': s.sell_quantity, 'sell_rate': s.sell_rate} for s in
                  sales],
        'dividends': [{'dividend_amount': d.dividend_amount} for d in dividends]
    }

    return jsonify(previous_records)

@app.route('/static/sw.js')
def serve_sw():
    return app.send_static_file('sw.js'), 200, {'Content-Type': 'application/javascript'}

@app.route('/static/manifest.json')
def serve_manifest():
    return app.send_static_file('manifest.json'), 200, {'Content-Type': 'application/json'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)