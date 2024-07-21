from app import create_app, db
from app.models import User, Product, Order, OrderItem

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Order': Order,
        'OrderItem': OrderItem
    }


if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()

        # Add some sample products if the database is empty
        if not Product.query.first():
            sample_products = [
                Product(name='Teddy Bear', description='A cute and cuddly teddy bear', price_usd=19.99,
                        image_url='https://example.com/teddy.jpg'),
                Product(name='LEGO Set', description='A fun LEGO building set', price_usd=49.99,
                        image_url='https://example.com/lego.jpg'),
                Product(name='Toy Car', description='A colorful toy car', price_usd=9.99,
                        image_url='https://example.com/car.jpg'),
                Product(name='Doll House', description='A beautiful doll house', price_usd=79.99,
                        image_url='https://example.com/dollhouse.jpg'),
            ]
            db.session.add_all(sample_products)
            db.session.commit()

    # Run the application
    app.run(debug=True)