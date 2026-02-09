import os
from app import db

ADMIN_ACCOUNT = {
    "name": os.getenv("ADMIN_ACCOUNT_NAME"),
    "password_hash": os.getenv("ADMIN_ACCOUNT_PASW")
}

# DB STRUCTURES
class Users(db.Model):
    # Column 1: ID
    id = db.Column(db.Integer, primary_key=True)
    # Column 2: Name
    name = db.Column(db.String(120), nullable=False, unique=True)
    # Column 3: Passwrd
    password_hash = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<User: {self.name}, Password: {self.password_hash}>'

class Products(db.Model):
    # Column 1: ID
    id = db.Column(db.Integer, unique=True, primary_key=True)
    # Column 2: Name
    name = db.Column(db.String(40), nullable=False, unique=True)
    # Column 3: Price
    price = db.Column(db.Float, nullable=False)
    # Column 4: Stock
    stock = db.Column(db.Integer, nullable=False)
    # Column 5: Image Link
    image_link = db.Column(db.String)
    # Column 6: Category
    category = db.Column(db.String(80))
    # Column 7: Club
    club = db.Column(db.String(60))
    # Column 8: Description
    description = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<name: {self.name}, descr: {self.description}>'

class Transactions(db.Model):
    # Column 1: ID
    id = db.Column(db.Integer, unique=True, primary_key=True)
    # Column 2: Product_id
    product_id = db.Column(db.Integer, nullable=False)
    # Column 3: User_id
    user_id = db.Column(db.Integer, nullable=False)
    # COlumn 4: price
    price = db.Column(db.Float(), nullable=False)
    # COlumn 5: Date
    date = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<user: {self.user_id}, amount: {self.amount},  date: {self.date}>'
