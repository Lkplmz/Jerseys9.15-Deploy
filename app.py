import os
from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQLAlchemy(app)

from models import Users, Products, Transactions, ADMIN_ACCOUNT
from helpers import login_required, admin_required, first_letter, addToCart, search, lookup_picture
app.jinja_env.filters["first_letter"] = first_letter
app.app_context().push()

if Users.query.filter_by(name = ADMIN_ACCOUNT["name"]).first() == None:
    admin = Users(name=ADMIN_ACCOUNT["name"], password_hash=ADMIN_ACCOUNT["password_hash"])
    db.session.add(admin)
    db.session.commit()

@app.route("/", methods=["GET", "POST"])
def index():
    recently_added = Products.query.order_by(Products.id.desc()).limit(3).all()
    
    results = (db.session.query(Products, func.count(Transactions.id))
        .join(Transactions, Products.id == Transactions.product_id)
        .group_by(Products.id)\
        .order_by(func.count(Transactions.id).desc()).all())

    bestsellers = [{"name": p[0].name, "image_link": p[0].image_link} for p in results]

    for r in recently_added:
        if r.image_link in ["https://placehold.jp/300x200.png?text=Limit+of+daily+requests", "https://placehold.jp/300x200.png?text=Image+not+found", "https://placehold.jp/300x300.png?text=Image+not+available"]:
            r.image_link = lookup_picture(r.name)
            db.session.commit()

    return render_template("index.html", recently_added=recently_added, bestsellers=bestsellers)

@app.route("/filter", methods=["POST"])
def filter():
    if request.method == 'POST':
        data = request.get_json()
        filter = data.get("filter")    
        query = data.get("query")

        if query == None:
            if filter == None:
                filtered = Products.query.all()
            else:
             filtered = Products.query.filter_by(category=filter).all()

        else:
            filtered = Products.query.filter(or_(Products.name.like(f"%{query}%"), Products.club.like(f"%{query}%"))).all()
        
        return jsonify([{"name": item.name, "price": item.price, "stock": item.stock, "image_link": item.image_link, "category": item.category, "club": item.club, "description": item.description} for item in filtered])


@app.route("/store/checkout", methods=["GET", "POST"])
@login_required
def checkout(): 

    final_products = []
    total = 0
    if 'cart' in session:
        for p in session["cart"]:
            query = Products.query.filter_by(id=p["id"]).first()
            p_total = p["amount"] * query.price
            total = total + p_total
            final_products.append({"name": query.name , "amount": p["amount"], "price" : query.price, "link": query.image_link, "total": p_total})
    else:
        return render_template('error.html', message="Cannot purchase no products. Go back and add some to the cart first")
    if request.method == "POST":
        username = request.form.get("username")
        credit_card = request.form.get("credit_card")
        cvc = request.form.get("cvc") 
        expiry_date = request.form.get("expiry")

        if not username or not credit_card or not cvc or not expiry_date:
            return render_template("error.html", message="blank field are not valid")

        if username != Users.query.filter_by(name=username).first().name:
            return render_template("error.html", message="username is not valid")
        if username != session["user_id"]:
            return render_template("error.html", message="this is not your username, if you're buying for someone else, log-in with their account")
        
        if credit_card.replace(" ", "").isdigit == False:
            return render_template("error.html", message="credit card value is not valid")
        if len(cvc) > 3:
            return render_template("error.html", message="cvc is not valid")
        
        for item in session['cart']:
            date = datetime.now()
            date = date.strftime("%m/%d/%Y - %I:%M%p")

            transaction = Transactions(product_id = item["id"], user_id = Users.query.filter_by(name=username).first().id, price = item["amount"] * Products.query.filter_by(id=item["id"]).first().price, date = date)

            product = Products.query.filter_by(id=item["id"]).first()
            if product.stock - item["amount"] >= 0:
                product.stock = product.stock - item["amount"]

            if product.stock == 0:
                db.session.delete(product)
            
            db.session.add(transaction)
            db.session.commit()
        
        session["cart"] = []
        return redirect("/")

    return render_template("checkout.html", products_in_cart=final_products, total=total)

@app.route("/clear")
def clear():
    session["cart"] = []
    return redirect("/store")

@app.route("/get_cart", methods=["GET","POST"])
def get_cart():
    if request.method == "POST":
        data = request.get_json()
        product_id = data.get('id')
        action = data.get('action')
        item = None

        for p in session["cart"]:
            if p["id"] == product_id:
                item = p
        
        if action == 'add' and item["amount"] < Products.query.filter_by(id=product_id).first().stock:
            item["amount"] = item["amount"] + 1
        elif action == 'remove' and item["amount"] > 0:
            item["amount"] = item["amount"] - 1
        
        if item["amount"] == 0:
            for i, p in enumerate(session["cart"]):
                if p["id"] == item["id"]:
                    session["cart"].pop(i)
                    break

        return jsonify({
            "success": True, 
            "amount": item["amount"]
        })
  
    if 'cart' in session:
        return jsonify(session["cart"])
    else:
        return jsonify([])

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    to_lookup = data.get('look_for')

    if to_lookup != None:
        element = search(to_lookup)
        return jsonify({"name": element.name, "price": element.price, "stock": element.stock, "image_link": element.image_link, "description": element.description})
    
    return jsonify({"name" : "undefined"})

@app.route("/store", methods=["GET", "POST"])
def store():
    if request.method == "POST":
        product_id = request.form.get("id")
        if product_id != None:
            if product_id.isdigit:
                product_id = int(product_id)
                addToCart(product_id)
                return jsonify(session['cart'])
        else:
            return jsonify(session['cart'])
        
    products = Products.query.all()
    for p in products:
        if p.image_link in ["https://placehold.jp/300x200.png?text=Limit+of+daily+requests", "https://placehold.jp/300x200.png?text=Image+not+found", "https://placehold.jp/300x300.png?text=Image+not+available"]:
            p.image_link = lookup_picture(p.name)
            db.session.commit()

    return render_template("store.html", products=products)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("error.html", message="The password or the username field is blank")

        if username == "Admin" and check_password_hash(ADMIN_ACCOUNT["password_hash"], password):
            session["user_role"] = "admin"
            session["user_id"] = "admin"
            return redirect("/admin")
        
        else:
            user_query = Users.query.filter_by(name=username).first()
            if user_query == None or not check_password_hash(user_query.password_hash, password):
                return render_template("error.html", message="Invalid username and/or passsword")
            
            session["user_id"] = username
            session["user_role"] = "user"

            return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/account")
@login_required
def account():
    return render_template("account.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if request.method == "POST":
        if not username or not password or not confirmation:
            return render_template("error.html", message="Blank inputs are not valid")
        elif password != confirmation:
            return render_template("error.html", message="Passwords not match")
        
        try:
            user = Users(name=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()

            session["user_id"] = username

            return redirect("/")

        except IntegrityError:
            return render_template("error.html", message="Username already taken")


    return render_template("register.html")

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    if session.get("user_role") != "admin" or session.get("user_id") != "admin":
        return redirect("/login")

    dashboard = {
        "sales": db.session.query(func.count(Transactions.id)).scalar(),
        "users": db.session.query(func.count(Users.name)).scalar(),
        "earnings": db.session.query(func.sum(Transactions.price)).scalar() if db.session.query(func.sum(Transactions.price)).scalar() != None else 0,
    }

       
    users = Users.query.all()
    #remove the admin from the customerss section.
    users.pop(0)
    transactions = Transactions.query.all()
    stock = Products.query.all()
        
    chart_data = [0] * 12
    for t in transactions:
        date = datetime.strptime(t.date, "%m/%d/%Y - %I:%M%p")
        month = date.month - 1
        chart_data[month] += t.price

    return render_template("/admin/admin.html", dashboard=dashboard, transactions=transactions, products=stock, users=users, server_chart_data=chart_data)

@app.route("/admin/manage", methods=["GET", "POST"])
@admin_required
def management():
    actionType = request.args.get("actionType")
    if request.method == "POST":
        actionType = request.form.get("actionType")
    
        if actionType == "Edit":
            product = request.form.get("product")
            if product != "Select":
                try:
                    db_product = Products.query.filter_by(name=product).first()

                    new_name = request.form.get("name")
                    new_price = request.form.get("price")
                    new_stock = request.form.get("stock")
                    new_image_link = request.form.get("image_link")
                    new_category = request.form.get("category")
                    new_club = request.form.get("club")
                    new_description = request.form.get("description")

                    if new_price.isdigit == False or new_stock.isdigit == False:
                        return render_template("error.html", message="Number fields must be numbers")
                
                    if new_name:
                        db_product.name = new_name

                    if new_category:
                        db_product.category = new_category

                    if new_club:
                        db_product.club = new_club

                    if new_price:
                        db_product.price = new_price

                    if new_stock:
                        db_product.stock = new_stock

                    if new_image_link:
                        db_product.image_link = new_image_link

                    if new_description:
                        db_product.description = new_description
                    
                    db.session.commit()
                    
                    return redirect("/admin")
                except:
                    return render_template("error", message="Something went wront. Please check everything is input correctly")
            return render_template("error.html", message="Invalid input")

        elif actionType == "Remove":
            product = request.form.get("product")
           
            if product != "Select":
                password = request.form.get("password")

                if not product or not password:
                    return render_template("error.html", message="Missing required field")
                
                if check_password_hash("scrypt:32768:8:1$Aps1NED876hzVR3L$155ab2b47152928507562a289d8a4aa59ce2524428a6d7e69f62d51e17aa7910d0448a80b9ff093606abc1424a864ad956ebeee353fa98fde7ab8f68bd5b6430", password ):
                    productToErase = Products.query.filter_by(name=product).first()
                    
                    db.session.delete(productToErase)
                    db.session.commit()
                    return redirect("/admin")
            return render_template("error.html", message="Invalid input")
        
        elif actionType == "Add":
            name = request.form.get("name")
            price = request.form.get("price")
            stock = request.form.get("stock")
            image_link = request.form.get("image_link")
            category = request.form.get("category")
            club = request.form.get("club")
            description = request.form.get("description")
            
            if not name or not price or not stock or not category or not club:
                return render_template("error.html", message="Missing required field")
            elif len(description) > 120 or len(name) > 40 or len(club) > 60 or len(category) > 80:
                return render_template("error.html", message="Some fields are too long")

            try:
                price = price.replace('$', '')
                

                price = float(price)
                stock = int(stock)

            except:
                return render_template("error.html", message="Number fields must be numbers")
            
            if price <= 0 or stock <= 0:
                return render_template("error.html", message="Number fields must be valid numbers. <br> Numbers must be higher than 0")
            
            if image_link == None or image_link.strip() == "":
                image_link = lookup_picture(name)

            if not description:
                description = f"No hay una descripcion de este producto."

            category = category.lower()
            club = club.lower()

            try:
                newProduct = Products(name=name, price=price, stock=stock, image_link=image_link, category=category, club=club, description=description)
                db.session.add(newProduct)
                db.session.commit()
            
            except:
                return render_template("error.html", message="Product already exist. To change something from it, go to edit section or delete it first.")

            return redirect("/admin")
        else:
            return render_template("error.html", message="Invalid action")

    return render_template("/admin/manage.html", actionType=actionType, products=Products.query.all())

if __name__ == '__main__':
    app.run()