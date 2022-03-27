import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session
import google.auth.transport.requests
from google.oauth2 import id_token
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User, Categories, Favorite, Match, Product
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv()
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


@app.route("/product", methods = ["POST"])
def create_product():
    product = Product()
    title = request.json.get("title")
    autor = request.json.get("autor")
    editorial = request.json.get("editorial")
    review = request.json.get("review")
    user_id = request.json.get("user_id")

    product.title = title
    product.autor = autor 
    product.editorial = editorial
    product.review = review
    product.user_id = user_id

    if title == "":
        return jsonify({
            "msg": "Title cannot be empty"
        }), 400
    
    db.session.add(product)
    db.session.commit()

    return jsonify(product.serialize()), 200

@app.route("/auth/google", methods=["POST"])
def authGoogle():
    token_request = google.auth.transport.requests.Request(session=session)
    token = request.json.get("token")
    id_info = id_token.verify_oauth2_token(
        id_token=token,
        audience=os.environ["GOOGLE_CLIENT_ID"],
        clock_skew_in_seconds=10,
        request=token_request,
    )
    print(id_info)
    print (type(id_info))

    email = id_info.get("email")
    # user = User.query.filter_by(email=email).first()
    # print(user)
 
    return jsonify({
                "msg": id_info
             }) 
    
@app.route("/logout")
def logout():
    session.clear()
    return jsonify({
        "msg": "logout"
    })



#PARA CONECTAR LA BASE DE DATOS CON EL FLUX

#@app.route("/bookmatch", methods=["POST"])
#def registro():
    # id = request.json.get("id")
    # user_id = request.json.get("book_id_from")
    # book_id_from = request.json.get("book_id_from")
    # book_id_to = request.json.get("book_id_to")
    # status = request.json.get(status)

    # user = Match()
    # user.id = id
    # user.user_id = user_id
    # user.book_id_from = book_id_to
    # user.book_id_to = book_id_to
    # user.status = status

    # db.session.add(user)
    # db.session.commit()

    # return jsonify({ 
    #     "msg" : "BookMatch ha enviado tu solicitud correctamente, buena suerte"}), 200




if __name__ == "__main__":
    app.run(host="localhost",port="5000")
