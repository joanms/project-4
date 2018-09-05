from flask import Flask, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash

from key import db_name, uri, log_in_key
from helper import create_user

app = Flask(__name__)

# mongoDB config
app.config['MONGO_DBNAME'] = db_name()
app.config['MONGO_URI'] = uri()


mongo = PyMongo(app)

app.config['SECRET_KEY'] = log_in_key()


# Search classes


class SearchRecipes:
    recipes = mongo.db.recipes

    def __init__(self,  k="dishTypes", v="deserts", sort="aggregateLikes", order=-1, limit=21):
        self.k = k
        self.v = v
        self.sort = sort
        self.order = order
        self.limit = limit

    def find_one(self, recipe_id):
        return self.recipes.find_one({"_id": ObjectId(recipe_id)})

    def optional_filters(self):
        return self.recipes.find().sort([(f'recipes.{self.sort}', self.order)]).limit(self.limit)

    def by_all(self):
        return self.recipes.find({f"recipes.{self.k}": f"{self.v}"}).sort([(f'recipes.{self.sort}', self.order)]).limit(self.limit)

    def __str__(self):
        return f"Key to serch for: {self.k},\nValue to search for: {self.v},\nSorted by: {self.sort}, \nLimit recipes: {self.limit}"

    def __len__(self):
        return len([x for x in SearchRecipes(limit=50000).optional_filters()])




class Database:

    def users(self):
        return mongo.db.users.find()

    def update(self, key):
        result = set()
        for x in SearchRecipes().optional_filters():
            x = x['recipes'][0][f'{key}']
            for y in x:
                result.add(y)
        return result

    def update_db(self, key, form_name, form_keys):
        form = {f"{form_name}": {}}
        result = set()
        for x in key:
            for y in SearchRecipes().optional_filters():
                y = y['recipes'][0][x]
                for z in y:
                    result.add(z)
        for x in key:
            form[f"{form_name}"][f"{x}"] = []
            for y in self.update(x):
                form[f"{form_name}"][f"{x}"].append(y.capitalize())
        return form

    def update_search_form(self, key=["dishTypes", "cuisines", "diets"]):
        form = self.update_db(key, "search_form", key)
        form["search_form"]["popularity"] = ["Ascending", "Decreasing"]
        mongo.db.forms.insert_one(form)
        return redirect(url_for("index"))