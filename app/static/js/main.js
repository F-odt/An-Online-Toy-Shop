// Cart functionality
let cart = JSON.parse(localStorage.getItem('cart')) || [];

function addToCart(productId, name, price) {
    const existingItem = cart.find(item => item.id === productId);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ id: productId, name, price, quantity: 1 });
    }
    updateCart();
    alert('Item added to cart!');
}

function updateCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
    if (document.getElementById('cart-items')) {
        displayCart();
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCart();
}

function displayCart() {
    const cartItemsDiv = document.getElementById('cart-items');
    const cartTotalSpan = document.getElementById('cart-total-amount');

    cartItemsDiv.innerHTML = '';
    let total = 0;

    cart.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'cart-item';
        itemDiv.innerHTML = `
            <span>${item.name}</span>
            <span>$${item.price.toFixed(2)} x ${item.quantity}</span>
            <button onclick="removeFromCart(${item.id})">Remove</button>
        `;
        cartItemsDiv.appendChild(itemDiv);
        total += item.price * item.quantity;
    });

    cartTotalSpan.textContent = `$${total.toFixed(2)}`;
}

function displayCartSummary() {
    const cartSummaryDiv = document.getElementById('cart-summary');
    let total = 0;

    cartSummaryDiv.innerHTML = '<h2>Order Summary</h2>';
    cart.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'cart-summary-item';
        itemDiv.innerHTML = `
            <span>${item.name}</span>
            <span>$${item.price.toFixed(2)} x ${item.quantity}</span>
        `;
        cartSummaryDiv.appendChild(itemDiv);
        total += item.price * item.quantity;
    });

    const totalDiv = document.createElement('div');
    totalDiv.className = 'cart-summary-total';
    totalDiv.innerHTML = `<strong>Total: $${total.toFixed(2)}</strong>`;
    cartSummaryDiv.appendChild(totalDiv);
}

// Stripe payment processing
let stripe;
let elements;

async function initializeStripe() {
    const response = await fetch('/api/create-payment-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: calculateTotal(), currency: 'USD' })
    });
    const { clientSecret } = await response.json();

    stripe = Stripe('your_stripe_public_key');
    elements = stripe.elements();

    const card = elements.create('card');
    card.mount('#card-element');

    card.addEventListener('change', function(event) {
        const displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });

    const form = document.getElementById('payment-form');
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: document.getElementById('name').value
                }
            }
        });

        if (error) {
            const errorElement = document.getElementById('card-errors');
            errorElement.textContent = error.message;
        } else {
            // Payment successful, redirect or show success message
            alert('Payment successful!');
            cart = [];
            updateCart();
            window.location.href = '/';
        }
    });
}

function calculateTotal() {
    return cart.reduce((total, item) => total + item.price * item.quantity, 0);
}

// Initialize cart display on cart page load
if (document.getElementById('cart-items')) {
    displayCart();
}

// Initialize Stripe and cart summary on the checkout page
if (document.getElementById('payment-form')) {
    displayCartSummary();
    initializeStripe();
}