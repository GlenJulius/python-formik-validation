import os
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import Customer, db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)

db.init_app(app)

@app.route("/customers", methods=['GET', 'POST'])
def customers():
    if request.method == 'GET':
        try:
            customers_list = [customer.to_dict() for customer in Customer.query.all()]
            return make_response(jsonify(customers_list))
        except Exception as e:
            return make_response(jsonify({'error': 'Failed to fetch customers'}), 500)

    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data or not all(k in data for k in ('name', 'email', 'age')):
                return make_response(jsonify({'error': 'Missing required fields'}), 400)
            
            customer = Customer(name=data.get('name'), email=data.get('email'), age=data.get('age'))
            db.session.add(customer)
            db.session.commit()
            return make_response(
                jsonify(
                    {'id': customer.id, 'name': customer.name, 'email': customer.email, 'age': customer.age}))
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': 'Failed to create customer'}), 500)

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(port=int(os.getenv('FLASK_RUN_PORT', 5555)), debug=debug_mode)
