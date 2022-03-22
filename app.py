import os 
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User, Categories, Favorite, Match, Product
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt


BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASEDIR, "app.db")
app.config["SECRET_KEY"] = "secret-key"
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
Migrate(app, db)
db.init_app(app)
CORS(app)

#PARA VER SI LA APP ESTA FUNCIONANDO
@app.route("/")
def home():
    return "<h1>Hello Señora Pinchetti </h1>"


# PARA CREAR USUARIO, NO BORRAR, NO MODIFICAR
@app.route("/registro", methods=["POST"])
def registro():
    name = request.json.get("name")
    surname = request.json.get("surname")
    email = request.json.get("email")
    password = request.json.get("password")

    password_hash = bcrypt.generate_password_hash(password)

    user = User()
    user.name = name
    user.surname = surname
    user.email = email
    user.password = password_hash

    db.session.add(user)
    db.session.commit()

    return jsonify({ 
        "msg" : "usuario creado exitosamente"}), 200

   
# Iniciar Sesión, NO BORRAR, NO MODIFICAR
@app.route("/login", methods=["POST"])
def login():
    password = request.json.get("password")
    email = request.json.get("email")

    user = User.query.filter_by(email=email).first()

    if user is not None:
        if bcrypt.check_password_hash(user.password, password):
             access_token = create_access_token(identity=email)
             return jsonify({
                 "access_token": access_token,
                 "user": user.serialize(),
                 "success":True
             }), 200
        else:
             return jsonify({
                "msg": "Email o contraseña inválida"
             }) 
    else:
        return jsonify({
            "msg": "Regístrate"
        })
        
# RUTA PROTEGIDA, NO TIENE METODO PORQUE ES GET POR DEFECTO
@app.route("/get_profile")
@jwt_required()
def get_profile():
     user = User.query.get()
     return jsonify({
         "user":user.serialize()
     })

# @app.route("/users", methods=["GET"])
# def get_users():
#     all_users = User.query.all()
#     users = list(map(lambda user: user.serialize(), all_users))

#     return jsonify(users), 200

# @app.route("/user/<int:id>", methods=["PUT"])
# def update_user(id):
#         user = User.query.get(id)
#         if user is not None:
#             user.nickname = request.json.get("nickname")
#             db.session.commit()
#             return jsonify(user.serialize()), 200
#         else: return jsonify({"msg": "User not found"}), 404

# #FALTA EL DELETE PARA ELIMINAR USUARIO


@app.route("/products", methods = ["GET"])
def get_products():
    products = Product.query.all()
    products = list(map(lambda product:   product.serialize(),products))

    return jsonify(products), 200

@app.route("/product/<int:id>", methods = ["PUT", "DELETE"])
def update_product(id):
    if request.method == "PUT":
        product = Product.query.get(id)
        if product is not None:
            product.title = request.json.get("title")
            db.session.commit()
            return jsonify(product.serialize()), 200
        else: return jsonify({"msg":"Not found"}), 404
    else:
        product = Product.query.get(id)
        if product is not None:
            db.session.delete(product)
            db.session.commit()
            return jsonify({"msg": "done"})
        else: return jsonify({"msg":"Not found"}), 404

if __name__ == "__main__":
    app.run(host="localhost",port="5000")
