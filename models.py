from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250),nullable=False)
    surname = db.Column(db.String(250),nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    
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
#             "categories": self.categories,
#             "user.id": self.user_id,
#        }
    
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    favorite = db.Column(db.String(250))

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
    book_id = db.Column(db.String(250),nullable=False)

    def _repr_ (self):
        return '<Match %r>' % self.match

    def serialize(self):
        return {
    "id" : self.id,
    "user_id": self.user_id,
    "book:id": self.book_id
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(10), nullable=False)
    editorial = db.Column(db.String(10), nullable=False)
    
    def _repr_(self):
        return "<Product %r>" % self.title

    def serialize(self):
        return {
            "id":self.id,
            "title": self.title,
            "autor":self.autor,
            "editorial": self.editorial
        }

