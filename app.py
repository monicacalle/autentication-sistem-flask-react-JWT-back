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
    return "<h1>Hello Api </h1>"


#Iniciar Sesión
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
                "msg": "Correo o email inválido"
            })
    else:
          return jsonify({
                "msg": "Registrate"
            })    
    


# OBTENER PERFIL
@app.route("/get_profile")
@jwt_required()
def get_profile():
    user = User.query.get()
    return jsonify({
        "user":user.serialize()
    })

# PARA CREAR USUARIO
@app.route("/user", methods = ["POST"])
def create_user():
    user = User()
    user.name = request.json.get("name")
    user.nickname = request.json.get("nickname")
    user.email = request.json.get("email")
    user.password = request.json.get("password")

    if user.name == "":
        return jsonify({
            "msg": "El campo nombre no puede estar vacío"
        }), 400 

    if user.email == "":
         return jsonify({
            "msg": "Este campo no puede estar vacío"
        }), 400 
    

    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize()), 200

@app.route("/users", methods=["GET"])
def get_users():
    all_users = User.query.all()
    users = list(map(lambda user: user.serialize(), all_users))

    return jsonify(users), 200

@app.route("/user/<int:id>", methods=["PUT"])
def update_user(id):
        user = User.query.get(id)
        if user is not None:
            user.nickname = request.json.get("nickname")
            db.session.commit()
            return jsonify(user.serialize()), 200
        else: return jsonify({"msg": "User not found"}), 404

#FALTA EL DELETE PARA ELIMINAR USUARIO


if __name__ == "__main__":
    app.run(host="localhost",port="5000")
