from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Vuelo Class/Model
class Vuelo(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  codigo = db.Column(db.String(10), unique=True)
  origen = db.Column(db.String(30))
  destino = db.Column(db.String(30))
  precio = db.Column(db.Float)
  asientos = db.Column(db.Integer)

  def __init__(self, codigo, origen, destino, precio, asientos):
    self.codigo = codigo
    self.origen = origen
    self.destino = destino
    self.precio = precio
    self.asientos = asientos

# Vuelo Schema
class VueloSchema(ma.Schema):
  class Meta:
    fields = ('id', 'codigo', 'origen', 'destino', 'precio', 'asientos')

# Init schema
vuelo_schema = VueloSchema()
vuelos_schema = VueloSchema(many=True)


with app.app_context():
    db.create_all()


# Create a Vuelo
@app.route('/vuelo', methods=['POST'])
def add_vuelo():
  codigo = request.json['codigo']
  origen = request.json['origen']
  destino = request.json['destino']
  precio = request.json['precio']
  asientos = request.json['asientos']

  new_vuelo = Vuelo(codigo, origen, destino, precio, asientos)

  db.session.add(new_vuelo)
  db.session.commit()

  return vuelo_schema.jsonify(new_vuelo)

# Get All Vuelos
@app.route('/vuelo', methods=['GET'])
def get_vuelos():
  all_vuelos = Vuelo.query.all()
  result = vuelos_schema.dump(all_vuelos)
  return jsonify(result)

# Get Single Vuelos
@app.route('/vuelo/<id>', methods=['GET'])
def get_vuelo(id):
  vuelo = Vuelo.query.get(id)
  return vuelo_schema.jsonify(vuelo)

# Update a Vuelo
@app.route('/vuelo/<id>', methods=['PUT'])
def update_vuelo(id):
  vuelo = Vuelo.query.get(id)

  codigo = request.json['codigo']
  origen = request.json['origen']
  destino = request.json['destino']
  precio = request.json['precio']
  asientos = request.json['asientos']

  vuelo.codigo = codigo
  vuelo.origen = origen
  vuelo.destino = destino
  vuelo.precio = precio
  vuelo.asientos = asientos

  db.session.commit()

  return vuelo_schema.jsonify(vuelo)

# Delete Vuelo
@app.route('/vuelo/<id>', methods=['DELETE'])
def delete_vuelo(id):
  vuelo = Vuelo.query.get(id)
  db.session.delete(vuelo)
  db.session.commit()

  return vuelo_schema.jsonify(vuelo)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision)

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
