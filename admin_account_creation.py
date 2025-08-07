from bookstore import app, db
from bookstore.models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('qwerty1234'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Аккаунт с администраторскими привилегиями был успешно создан.")
    else:
        print("Аккаунт с администраторскими привилегиями уже существует в системе.")

# python admin_account_creation.py