import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    # Güvenlik anahtarı
    SECRET_KEY = os.getenv("SECRET_KEY", "defaultkey")

    # Veritabanı URI
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # SQLAlchemy ayarları
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail ayarları
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("EMAIL_USER")
    MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
