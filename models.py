from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250),nullable=False)
    surname = db.Column(db.String(250),nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=True)
#   favorite = db.relationship('Favorite', backref='user', lazy=True)
#   products = db.relationship('Products', backref='user', lazy=True)

    def _repr_ (self):
        return '<User %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
        }

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250),nullable=False)
    description = db.Column(db.String(250),nullable=False)
    

    def _repr_ (self):
        return '<User %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

#class Books(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(250),nullable=False)
#     size = db.Column(db.String(250),nullable=False)
#     description = db.Column(db.String(250),nullable=False)
#     categories = db.Column(db.String(250),nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

#     def _repr_ (self):
#         return '<User %r>' % self.name

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "size": self.size,
#             "description": self.description,
#             "Categories": self.categories,
#             "user.id": self.user_id,
#        }
    
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    favorite = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
 #   categories = db.relationship('Category', secondary=categories, lazy='subquery',
 #       backref=db.backref('favorites', lazy=True))
   

    def _repr_ (self):
        return '<Favorite %r>' % self.favorite

    def serialize(self):
        return {
            "id": self.id,
            "favorite": self.favorite
            }


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(250),nullable=False)
    book = db.Column(db.String(250),nullable=False)
    interested = db.Column(db.String(250),nullable=False)
    status = db.Column(db.String(15), nullable=False)


    def _repr_ (self):
        return '<Match %r>' % self.match

    def serialize(self):
        return  {
    "id" : self.id,
    "user_id": self.user_id,
    "book": self.book,
    "interested" : self.interested,
    "status" : self.status
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(30), nullable=False)
    editorial = db.Column(db.String(30), nullable=False)
    review = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

    
    def _repr_(self):
        return "<Product %r>" % self.title

    def serialize(self):
        return {
            "id":self.id,
            "title": self.title,
            "autor":self.autor,
            "editorial": self.editorial,
            "review": self.review,
            "user_id": self.user_id 
        }

# Usuario, categorias, favorite, match, Product
#relacion de usuarios a usuarios, uno a muchos
#relacion de usuarios a productos (books)
#relacion de usuario a favoritos
# productos a match
# categorias a favoritos