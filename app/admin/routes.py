from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app.models import Product, Category, User
from app import db
from functools import wraps
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/change_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role not in ['admin', 'viewer']:
        flash('Geçersiz rol seçimi.', 'danger')
        return redirect(url_for('admin.users'))

    user.role = new_role
    db.session.commit()
    flash(f"{user.email} kullanıcısının rolü {new_role} olarak değiştirildi.", 'success')
    return redirect(url_for('admin.users'))



@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.all()
    categories = Category.query.all()

    return render_template('admin/products.html', products=products, categories=categories)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    categories = Category.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        category_id = int(request.form.get('category_id'))

        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_file.save(os.path.join(upload_folder, filename))
            image_filename = filename

        new_product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            image=image_filename
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Ürün başarıyla eklendi.', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/add_product.html', categories=categories)



@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.all()

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.category_id = int(request.form.get('category_id'))

        db.session.commit()
        flash('Ürün başarıyla güncellendi.', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/edit_product.html', product=product, categories=categories)

@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Ürün başarıyla silindi.', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Kategori adı boş olamaz.', 'warning')
            return redirect(url_for('admin.add_category'))
        
        if Category.query.filter_by(name=name).first():
            flash('Bu isimde zaten bir kategori var.', 'danger')
            return redirect(url_for('admin.add_category'))

        new_cat = Category(name=name)
        db.session.add(new_cat)
        db.session.commit()
        flash('Kategori başarıyla eklendi.', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/add_category.html')

@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Kategori adı boş olamaz.', 'warning')
            return redirect(url_for('admin.edit_category', category_id=category.id))
        
        existing_cat = Category.query.filter_by(name=name).first()
        if existing_cat and existing_cat.id != category.id:
            flash('Bu isimde başka bir kategori zaten var.', 'danger')
            return redirect(url_for('admin.edit_category', category_id=category.id))

        category.name = name
        db.session.commit()
        flash('Kategori başarıyla güncellendi.', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/edit_category.html', category=category)

@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Kategori başarıyla silindi.', 'success')
    return redirect(url_for('admin.categories'))
