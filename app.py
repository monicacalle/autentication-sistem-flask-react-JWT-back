import os
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt

BASEDIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASEDIR, "app.db")
app.config["SECRET_KEY"] = "secret-key"
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
Migrate(app, db)
db.init_app(app)
CORS(app)



@app.route("/signup", methods=["POST"])
def signup():
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

    access_token = create_access_token(identity=email)
            
    return jsonify({ 
        "msg" : "usuario creado exitosamente",
        "access_token": access_token,
        "success":True
        }), 200


@app.route("/registro/<int:id>", methods=['DELETE'])
def delete_user(id):
    if id is not None:
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg" : "success"})
    else:
        return jsonify({"msg" : "User not found"}), 404


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

@app.route("/get_profile")
@jwt_required()
def get_profile():
    email=get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    return jsonify({
         "user":user.serialize(),
         "success":True
     })

    
@app.route("/logout")
def logout():
    session.clear()
    return jsonify({
        "msg": "logout"
    })


if __name__ == "__main__":
    app.run(host="localhost",port="5000")
