from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Giriş başarılı!', 'success')

            # Rol bazlı yönlendirme
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('shop.index'))

        else:
            flash('Geçersiz e-posta veya şifre!', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        if not email or not name or not password:
            flash('Lütfen tüm alanları doldurun!', 'warning')
            return redirect(url_for('auth.register'))

        try:
            hashed_password = generate_password_hash(password)
            new_user = User(email=email, name=name, password=hashed_password, role='viewer')

            db.session.add(new_user)
            db.session.commit()
            flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('Bu e-posta zaten kayıtlı!', 'danger')
            return redirect(url_for('auth.register'))
        except Exception as e:
            db.session.rollback()
            flash(f'Beklenmeyen hata: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')
