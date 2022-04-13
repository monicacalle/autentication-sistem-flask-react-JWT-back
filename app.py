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
Migrate(app, db, render_as_batch=True)
db.init_app(app)
CORS(app)

#PARA VER SI LA APP ESTA FUNCIONANDO
@app.route("/")
def home():
    return "<h1>Hello Señora Pinchetti </h1>"

#ESTOS 4 ENDPOINT SON LOS DEL CRUD DEL USUARIO
# PARA CREAR USUARIO, NO BORRAR, NO MODIFICAR #PARA POSTEAR USUARIO
@app.route("/registro", methods=["POST"])
def registro():
    name = request.json.get("name")
    surname = request.json.get("surname")
    email = request.json.get("email")
    password = request.json.get("password")

    print(password)

# AUTENTICACION CONTRASENA
    if not password or password == " ":
        return jsonify({
            "msg" : "contraseña requerida", "success": False
        }),400

    is_valid = True    
    if len(password) <= 8 or len(password) >= 16:
        is_valid = False
        print("lenght")
    if not any(char.isdigit() for char in password):        
        is_valid = False       
        print("vegy")
    if not any(char.isupper() for char in password):       
        is_valid = False   
        print("upper")
    if not any(char.islower() for char in password):      
        is_valid = False
        print("lower")
    if not is_valid:      
        return jsonify({"msg":"la contraseña debe contener almenos de 8 a 16 caracteres, debe incluir numeros y mayusculas y minusculas ", "success": False}), 400
                

    password_hash = bcrypt.generate_password_hash(password) 

    user = User()
    user.name = name
    user.surname = surname
    user.email = email
    user.password = password_hash

    
    db.session.add(user)
    db.session.commit()
            
    return jsonify({ 
        "msg" : "usuario creado exitosamente",
        "success":True
        }), 200
#para enviar libros por ID

@app.route("/getbook/<int:id>", methods=["GET"])
def get_book(id):
    product = Product.query.filter_by(id=id).first()
    if product is not None:
        return jsonify(product.serialize()) 


#ENDPOINT PARA VER TODOS LOS USUARIOS
@app.route("/editdata", methods=["GET"])
def get_users():
     try:
         all_users = User.query.all()
         all_users = list(map(lambda editdata: user.serialize(), all_editdata))
     except Exception as error:
         print("Editar error : {error}")    
     return jsonify(all_users)

#ENDPOINT PARA EDITAR USUARIOS
#LISTO, FUNCIONANDO
@app.route("/edituser/<int:id>", methods=["PUT"])
def update_user(id):
    if id is not None:
        user = User.query.filter_by(id=id).first()
        if user is not None:
            user.name = request.json.get("name")
            user.surname = request.json.get("surname")
            user.password = bcrypt.generate_password_hash(request.json.get("password"))

            db.session.commit()
            return jsonify(user.serialize()), 200
        else:
            return jsonify({
                "msg": "Usuario no encontrado"
            }), 404
    else:
        return jsonify({
            "msg": "Usuario no existe"
        }), 400

#ENDPOINT PARA ELIMINAR USUARIO
# FUNCIONANDO
@app.route("/registro/<int:id>", methods=['DELETE'])
def delete_user(id):
    if id is not None:
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg" : "success"})
    else:
        return jsonify({"msg" : "User not found"}), 404

   
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
                "msg": "Email o contraseña inválida",
                "success":False
             }),400
    else:
        return jsonify({
            "msg": "Regístrate",
            "success":False
        }),404
        
# RUTA PROTEGIDA, NO TIENE METODO PORQUE ES GET POR DEFECTO
@app.route("/get_profile")
@jwt_required()
def get_profile():
    email=get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    return jsonify({
         "user":user.serialize()
     })

@app.route("/products", methods = ["GET"])
def get_products():
    products = Product.query.all()
    products = list(map(lambda product:   product.serialize(),products))

    return jsonify(products), 200

# para consultar por un libro en especial mediante ID #NOBORRAR
@app.route("/product/<int:id>", methods = ["GET"])
def get_product(id):
    product = Product.query.filter_by(id=id).first()
    return jsonify(
        product.serialize()
    )
# para consultar por los libros publicados por el usuario, SOLO el usuario filtrado por ID
@app.route("/userproducts/<int:id>", methods = ["GET"])
def get_mybooks(id):
    products = Product.query.filter_by(user_id=id).all()
    products = list(map(lambda product: product.serialize(),products))
    return jsonify(
        products
    )


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

    email = id_info.get("email")
    name = id_info.get("given_name")
    surname = id_info.get("family_name")
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User()
        user.name = name
        user.surname = surname
        user.email = email
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=email)
    return jsonify({
                 "access_token": access_token,
                 "user": user.serialize(),
                 "success":True
             }), 200
    
    
@app.route("/logout")
def logout():
    session.clear()
    return jsonify({
        "msg": "logout"
    })

#PARA CONECTAR LA BASE DE DATOS CON EL FLUX

#ENDPOINT PARA PRIMER POST ACERCA DEL ESTADO PENDING Y SOLICITUD DEL LIBRO

@app.route("/bookmatch", methods=["POST"])
def bookmatch():
    user_id = request.json.get("user_id")
    book = request.json.get("book")
    interested = request.json.get("interested")
    status = request.json.get("status")
    book_id = request.json.get("book_id")

    
    existingMatches = Match.query.filter_by(user_id=user_id).all()
    matches = 0
    for match in existingMatches:
        if match.interested == interested and match.book == book:
            matches = matches+1
            print(match.serialize())
            break

    print(matches)
    if matches >0:
        return jsonify({
            "msg": "ya exite una solicitud para este libro"
        }), 400

    user = Match()
    user.user_id = user_id
    user.book = book
    user.interested = interested
    user.status = status
    user.book_id = book_id

    db.session.add(user)
    db.session.commit()

    return jsonify({ 
        "msg" : "BookMatch ha enviado tu solicitud correctamente, buena suerte"}), 200

#CAMBIO DE ESTADO A ACCEPTED EN MATCH

app.route("/match/<int:id>", methods=["PUT"])
def matchaccepted(id):
    match = Match.query.filter_by(id=id).first()
    if match is not None:
        match.status = request.json.get("status")

    db.session.commit()

    return jsonify({ 
        "msg" : "Felicitaciones haz aceptado el Match"}), 200

#ELIMINAR SOLICITUDES DE BOOKMATCH

@app.route("/bookmatch/<int:id>", methods=['DELETE'])
def delete_bookmatch(id):
    if id is not None:
        match = Match.query.filter_by(id=id).first()
        db.session.delete(match)
        db.session.commit()
        return jsonify({"msg" : "success"})
    else:
        return jsonify({"msg" : "Request not found"}), 404

#ENDPOINT PARA CONSULTAR LOS MATCH PENDIENTES AQUI DEBERIA EXISTIR UN FILTRO solo los productos con status pendiente
@app.route("/pendingreceive", methods=['GET'])
def pendingreceive():
        matching = Match.query.all()
        matching = list(map(lambda allmatching: allmatching.serialize(), matching))
        return jsonify(
                matching)
    

# @app.route("/pendingreceive/<int:id>", methods=['PUT'])
# def pendingreceive():
#         user_id = request.json.get("user_id")
#         book = request.json.get("book")
#         interested = request.json.get("interested")
#         status = request.json.get("status")

#         user = Match()
#         user.user_id = user_id
#         user.book = book
#         user.interested = interested
#         user.status = status

#         db.session.add(user)
#         db.session.commit()

#         return jsonify({ 
#         "msg" : "Felicitaciones haz aceptado el Match"}), 200




    
#ENDPOINT PARA CONSULTAR LOS MATCH ACEPTADOS
@app.route("/pendingsend", methods=["GET"])
def pendingsend():      
        pendingsend = Match.query.filter_by(status=accepted).first()
        return jsonify(
        Match.serialize()
    )
#ENDPOINT PARA CONSULTAR TODOS LOS LIBROS PUBLICADOS MENOS LOS MIOS 
@app.route("/publishedproduct", methods=["GET"])
def publishedbooks(): 

    200

#ENDPOINT PARA POSTEAR CAMBIO DE STATUS ACEPTADO
@app.route("/statusaccepted", methods=["PUT"])
def statusaccepted(): 200

#ENDPOINT PARA POSTEAR CAMBIO DE ESTADO RECHAZADO
@app.route("/statusrejected", methods=["PUT"])
def pstatusrejected(): 200



if __name__ == "__main__":
    app.run(host="localhost",port="5000")
