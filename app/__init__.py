from flask import Flask, redirect, url_for
from flask_mail import Mail
from flask_login import LoginManager
from dotenv import load_dotenv
from app.models import db, User  # db ve User birlikte import
from app.admin.routes import admin_bp
from app.shop.routes import shop_bp


mail = Mail()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Uzantıları başlat
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # Giriş yapılmamışsa yönlendirilecek view
    login_manager.login_view = 'auth.login'

    # Kullanıcı yükleyici
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Ana sayfa yönlendirmesi
    @app.route('/')
    def home():
        return redirect(url_for('shop.index'))

    # Blueprint'leri kaydet
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.shop.routes import shop_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(shop_bp)

    return app
