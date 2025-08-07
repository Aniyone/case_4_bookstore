from flask import render_template, redirect, url_for, flash, request
from bookstore import app, db
from bookstore.forms import RegistrationForm, LoginForm, BookForm, RentalForm
from bookstore.models import User, Book, Rental
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Аккаунт создан!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard' if user.is_admin else 'user_dashboard'))
        flash('Неверные данные пользователя.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/dashboard')
@login_required
def user_dashboard():
    category = request.args.get('category')
    author = request.args.get('author')
    year = request.args.get('year', type=int)
    query = Book.query
    if category:
        query = query.filter_by(category=category)
    if author:
        query = query.filter_by(author=author)
    if year:
        query = query.filter_by(year=year)
    books = query.all()

    categories = db.session.query(Book.category).distinct().all()
    authors = db.session.query(Book.author).distinct().all()
    years = db.session.query(Book.year).distinct().all()
    categories = [c[0] for c in categories]
    authors = [a[0] for a in authors]
    years = sorted([y[0] for y in years], reverse=True)
    return render_template('user_dashboard.html', books=books,
                           categories=categories,
                           authors=authors,
                           years=years,
                           selected_category=category,
                           selected_author=author,
                           selected_year=year)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    books = Book.query.all()
    return render_template('admin_dashboard.html', books=books)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            category=form.category.data,
            year=form.year.data,
            price=form.price.data,
            available=form.available.data
        )
        db.session.add(book)
        db.session.commit()
        flash('Книга добавлена в каталог.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('book_addedit.html', form=form)

@app.route('/admin/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.category = form.category.data
        book.year = form.year.data
        book.price = form.price.data
        book.available = form.available.data
        db.session.commit()
        flash('Книга обновлена.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('book_addedit.html', form=form, book=book)

@app.route('/admin/delete/<int:book_id>')
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Книга удалена.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)

    if not book.available:
        flash('Эта книга сейчас недоступна для аренды.', 'warning')
        return render_template('book_detail.html', book=book, form=None)
    form = RentalForm()
    if form.validate_on_submit():
        duration = int(form.duration.data)
        rental = Rental(
            user_id=current_user.id,
            book_id=book.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=duration)
        )
        db.session.add(rental)
        db.session.commit()
        flash('Книга успешно арендована!', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('book_detail.html', book=book, form=form)

@app.route('/reminders')
@login_required
def reminders():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    rentals = Rental.query.filter_by(user_id=current_user.id).all()
    expired_rentals = [r for r in rentals if r.is_expired()]
    active_rentals = [r for r in rentals if not r.is_expired()]
    return render_template(
        'reminders.html',
        expired_rentals=expired_rentals,
        active_rentals=active_rentals
    )

@app.route('/admin/rentals')
@login_required
def admin_rentals():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    all_rentals = Rental.query.order_by(Rental.end_date.desc()).all()
    return render_template('admin_reminders.html', rentals=all_rentals)


@app.before_request
def check_expired_rentals():
    if current_user.is_authenticated and request.endpoint in ['user_dashboard']: 
         rentals = Rental.query.filter_by(user_id=current_user.id).all()
         expired_rentals = [r for r in rentals if r.is_expired()]
         if expired_rentals:
            flash('У вас есть просроченные книги.', 'error')