# HELPER FUNCTIONS
import os
from flask import session, redirect
import requests
from functools import wraps

from models import Products

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def login_required(f):
    @wraps(f)
    def dec_funct(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return dec_funct

def admin_required(f):
    @wraps(f)
    def dec_funct(*args, **kwargs):
        if session.get("user_role") != "admin" or session["user_id"] != "admin":
            return redirect("/login")
        return f(*args, **kwargs)

    return dec_funct

def first_letter(name):
    return name[0]

def addToCart(id):
    if "cart" not in session:
        session["cart"] = []

    if len(session["cart"]) != 0:
        for item in session["cart"]:
            if item["id"] == id:
                item["amount"] = item["amount"] + 1
                return
    session["cart"].append({"id": id, "amount": 1})

def search(id):
    return Products.query.filter_by(id=id).first()

def lookup_picture(element):
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        'q': f"{element} white background",
        'cx': SEARCH_ENGINE_ID,
        'key': GOOGLE_API_KEY,
        'searchType': 'image',
        'num': 1,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # chek for valid response from gooogle
        if response.status_code == 200:
            if 'items' in data:
                return data['items'][0]['link']
        elif response.status_code == 429:
            return f"https://placehold.jp/300x200.png?text=Limit+of+daily+requests"
        else:
            return f"https://placehold.jp/300x200.png?text=Image+not+found"

    except:
        return "https://placehold.jp/300x300.png?text=Image+not+available"
