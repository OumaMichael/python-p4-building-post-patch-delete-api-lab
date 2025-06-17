#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if bakery:
        return make_response(bakery.to_dict(), 200)
    return make_response({"error": "Bakery not found"}, 404)

# PATCH - update bakery name
@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response({"error": "Bakery not found"}, 404)

    data = request.form
    if "name" in data:
        bakery.name = data["name"]
        db.session.commit()
    return make_response(bakery.to_dict(), 200)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    return make_response([bg.to_dict() for bg in baked_goods], 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if most_expensive:
        return make_response(most_expensive.to_dict(), 200)
    return make_response({"error": "No baked goods found"}, 404)

# POST - create new baked good
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.form
    try:
        new_baked_good = BakedGood(
            name=data['name'],
            price=float(data['price']),
            bakery_id=int(data['bakery_id'])
        )
        db.session.add(new_baked_good)
        db.session.commit()
        return make_response(new_baked_good.to_dict(), 201)
    except Exception as e:
        return make_response({"error": str(e)}, 400)

# DELETE - delete baked good by ID
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return make_response({"error": "Baked good not found"}, 404)
    db.session.delete(baked_good)
    db.session.commit()
    return make_response({"message": "Baked good deleted successfully"}, 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
