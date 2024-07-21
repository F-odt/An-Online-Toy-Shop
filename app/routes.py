import os

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Product, Order, OrderItem
from werkzeug.security import generate_password_hash
import stripe
from datetime import datetime
import config

main = Blueprint('main', __name__)

stripe.api_key = config.Config.STRIPE_SECRET_KEY


@main.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@main.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)


@main.route('/cart')
def cart():
    cart_items = []
    total = 0
    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(product_id)
            if product:
                item_total = product.price_usd * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
    return render_template('cart.html', cart_items=cart_items, total=total)


@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Process the checkout
        # Create a Stripe PaymentIntent
        # Save the order to the database
        # Clear the cart
        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('checkout.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'], email=request.form['email'])
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/api/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    try:
        data = request.json
        intent = stripe.PaymentIntent.create(
            amount=int(data['amount'] * 100),  # Stripe expects amounts in cents
            currency=data['currency'],
        )
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return jsonify(error=str(e)), 403


@main.route('/order-history')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_ordered.desc()).all()
    return render_template('order_history.html', orders=orders)


@main.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    try:
        if 'cart' not in session:
            session['cart'] = {}

        cart = session['cart']

        # Convert product_id to string as dictionary keys in session are strings
        product_id = str(product_id)

        if product_id in cart:
            cart[product_id] += 1
        else:
            cart[product_id] = 1

        session.modified = True

        # Log the cart contents for debugging
        current_app.logger.debug(f"Cart contents: {cart}")

        return jsonify({'success': True, 'cart': cart})
    except Exception as e:
        current_app.logger.error(f"Error adding to cart: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@main.route('/get_cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', {})
    cart_data = {}
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(product_id)
        if product:
            item_total = product.price_usd * quantity
            cart_data[product_id] = {
                'name': product.name,
                'quantity': quantity,
                'price': product.price_usd,
                'total': item_total
            }
            total += item_total

    return jsonify({
        'cart': cart_data,
        'total': total
    })
