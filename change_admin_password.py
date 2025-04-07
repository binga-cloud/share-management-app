from app import app, db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    admin = User.query.filter_by(username="admin").first()
    if admin:
        new_password = input("Enter new admin password: ")
        admin.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        print("Admin password updated successfully!")
    else:
        print("Admin user not found")