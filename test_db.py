# from app import create_app
# from app.models import db

# app = create_app()

# with app.app_context():
#     db.create_all()  # Modellerden tabloları oluşturur
#     print("✅ Tablolar oluşturuldu.")

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    admin = User(
        email='admin@example.com',
        name='Admin',
        password=generate_password_hash('admin123'),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin kullanıcı oluşturuldu.")
