from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.models import Product, Order, OrderItem
from app import db

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

@shop_bp.route('/')
@login_required
def index():
    products = Product.query.all()
    role = current_user.role if current_user.is_authenticated else 'viewer'
    return render_template('shop/index.html', products=products, role=role)

@shop_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']

    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity

    session['cart'] = cart
    flash('Ürün sepete eklendi.', 'success')
    return redirect(url_for('shop.index'))

@shop_bp.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': quantity
            })
            total_price += item_total

    return render_template('shop/cart.html', cart_items=cart_items, total_price=total_price)

@shop_bp.route('/increase_quantity/<int:product_id>')
@login_required
def increase_quantity(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    session['cart'] = cart
    return redirect(url_for('shop.view_cart'))

@shop_bp.route('/decrease_quantity/<int:product_id>')
@login_required
def decrease_quantity(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        if cart[product_id_str] > 1:
            cart[product_id_str] -= 1
        else:
            cart.pop(product_id_str)  # Miktar 1 ise ürünü tamamen sil

    session['cart'] = cart
    flash('Ürün miktarı güncellendi.', 'success')
    return redirect(url_for('shop.view_cart'))


@shop_bp.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    return redirect(url_for('shop.view_cart'))


@shop_bp.route('/complete_order', methods=['POST'])
@login_required
def complete_order():
    cart = session.get('cart', {})
    if not cart:
        flash('Sepetiniz boş, sipariş veremezsiniz.', 'warning')
        return redirect(url_for('shop.view_cart'))

    total_price = 0
    order_items = []

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if not product:
            continue
        total_price += product.price * quantity
        order_items.append({
            'product': product,
            'quantity': quantity,
            'price': product.price
        })

    new_order = Order(user_id=current_user.id, total_price=total_price)
    db.session.add(new_order)
    db.session.commit()  # order.id almak için commit gerekli

    for item in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item['product'].id,
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)

    db.session.commit()

    session.pop('cart', None)

    flash('Siparişiniz başarıyla kaydedildi. Teşekkürler!', 'success')
    return redirect(url_for('shop.index'))
