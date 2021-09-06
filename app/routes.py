from datetime import datetime

from flask import render_template, flash, redirect, request, url_for, make_response, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db, logging

import json
import jsonschema
from jsonschema import validate
from bson import json_util
from bson.objectid import ObjectId

headers = {"Content-Type": "application/json"}

def get_schema(filename: str):
    """This function loads the given schema available"""
    with open("app/"+filename, 'r') as file:
        schema = json.load(file)
    return schema


def validate_json(dict_data: dict, schema_name: str):
    """REF: https://json-schema.org/ """
    # Describe what kind of json you expect.
    execute_api_schema = get_schema(schema_name)

    try:
        validate(instance=dict_data, schema=execute_api_schema)
    except jsonschema.exceptions.ValidationError as err:
        return False

    return True

def make_message(message:str):
    return {"msg":message}

# @app.before_request
# def before_request():
#     """Función que actualiza periodicamente el valor de última conexión del usuario"""
#     if current_user.is_authenticated:
#         current_user.last_seen = datetime.utcnow()
#         db.session.commit()


# @app.route("/", methods=["GET", "POST"])
# @app.route("/index", methods=["GET", "POST"])
# def index():
#     """Función que maneja la lógica de la inserción de empresas tanto en 'enterprises'
#         como en 'values'enterprises', así como el despliegue de páginas y la paginación de las mismas

#     :return: Redireccionamiento a página principal
#     :rtype: None
#     """
    
#     return render_template(
#         "index.html",
#         title="Home",
#     )


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     """Función que direcciona a formulario que valida identidad del usuario

#     :return: Redireccionamiento a página principal
#     :rtype: None
#     """
#     if current_user.is_authenticated:
#         return redirect(url_for("main"))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash("Usuario y/o contraseña invàlidos")
#             return redirect(url_for("login"))
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get("next")
#         if not next_page or url_parse(next_page).netloc != "":
#             next_page = url_for("main")
#         return redirect(next_page)
#     return render_template("login.html", title="Ingresar", form=form)


# @app.route("/logout")
# def logout():
#     logout_user()
#     return redirect(url_for("index"))


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     """Función que permite direccionar a la página de registro de usuarios y
#         manejar la lógica de las peticiones

#     :return: redireccionamiento a página de registro
#     :rtype: None
#     """
#     if current_user.is_authenticated:
#         return redirect(url_for("index"))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash("Felicitaciones. Te has registrado con èxito")
#         return redirect(url_for("login"))
#     return render_template("register.html", title="Register", form=form)


# @app.route("/user/<username>")
# @login_required
# def user(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     return render_template("user.html", user=user)


# @app.route("/edit_profile", methods=["GET", "POST"])
# @login_required
# def edit_profile():
#     """Función que permite redireccionar a página de edición de perfiles de usuarios
#         y manejar la lógica de las peticiones

#     :return: redireccionamiento a página de edición de perfiles
#     :rtype: None
#     """
#     form = EditProfileForm(current_user.username)
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.about_me = form.about_me.data
#         db.session.commit()
#         flash("Tus cambios han sido guardados")
#         return redirect(url_for("edit_profile"))
#     elif request.method == "GET":
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template("edit_profile.html", title="Editar Perfil", form=form)


# @app.route("/main", methods=["GET", "POST"])
# @login_required
# def main():
#     return render_template("main.html", title="Página Principal")

# GET clients
# POST clients
# GET clients/{id}
# PUT clients/{id}
# DELETE clients/{id}
# GET clients/{id}/restaurants
# POST clients/{id}/restaurants
# DELETE clients/{id}/restaurants/{id}

# GET restaurants
# POST restaurants
# GET restaurants/{id}
# PUT restaurants/{id}
# DELETE restaurants/{id}
# GET restaurants/{id}/wines
# POST restaurants/{id}/wines
# DELETE restaurants/{id}/wines/{id}

# GET wines
# POST wines
# GET wines/{id}
# PUT wines/{id}
# DELETE wines/{id}


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    """Función que redirecciona a la pagina principal

    :return: Redireccionamiento a página principal
    :rtype: None
    """
    
    return "Hola mundo"

@app.route("/wines", methods=["GET", "POST"])
def read_create_wines():
    """ Function that redirects to the read and create functions for the wines

    :return: The HTTP response
    :rtype: Response with a body tag and a HTTPStatus code
    """
    if request.method == "GET":
        wines_cursor = db.wines.find()
        body = [wine for wine in json.loads(json_util.dumps(wines_cursor))]
        return make_response({"body":body}, 200, headers)
    elif request.method == "POST":
        dict_data = request.get_json()
        is_valid = validate_json(dict_data, "wine.json")
        if is_valid:
            existing_wine = db.wines.find_one({"name":dict_data["name"]})
            if not existing_wine:
                db.wines.insert_one(dict_data)
                return make_response(make_message("Agregado exitosamente"), 200, headers)
            else:
                logging.warning("Attempted to write duplicated registry in wines collection")
                return make_response(make_message("Registro duplicado"), 409, headers)
        return make_response(make_message("Parámetros inválidos o faltantes"), 400, headers)


@app.route("/wines/<string:id>", methods=["GET","PUT","PATCH","DELETE"])
def update_delete_wines(id: str):
    """ Function that redirects to the update and delete functions for the wines

    :param id: The id of the wine to be either updated or deleted
    :type id: str
    :return: The HTTP response
    :rtype: Response with a body tag and a HTTPStatus code
    """
    if request.method == "GET":
        try:
            selected_wine = db.wines.find_one({"_id": ObjectId(id)})
            if selected_wine:
                return make_response({"body":json.loads(json_util.dumps(selected_wine))},200,headers)
            return make_response(make_message("Recurso no encontrado"),404, headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)
    elif request.method in ("PUT","PATCH"):
        try:
            dict_data = request.get_json()
            is_valid = validate_json(dict_data, "wine.json")
            if is_valid:
                conflicting_wine = db.wines.find_one({"name":dict_data["name"]})
                if conflicting_wine:
                    return make_response(make_message("Conflcito entre registros. Otro vino ya tiene ese nombre"), 409, headers)
                result = db.wines.replace_one({"_id": ObjectId(id)},dict_data)
                return make_response({"body":result.raw_result},200,headers)
            return make_response(make_message("Parámetros inválidos o faltantes"), 400, headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)
    elif request.method == "DELETE":
        try:
            result = db.wines.delete_one({"_id": ObjectId(id)})
            return make_response({"body":result.raw_result},200,headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)


@app.route("/restaurants", methods=["GET", "POST"])
def read_create_restaurants():
    """Function that redirects to the create and read functions

    :return: The HTTP response
    :rtype: Response with a body tag and a HTTPStatus code
    """
    if request.method == "GET":
        restaurants_cursor = db.restaurants.find()
        body = [restaurant for restaurant in json.loads(json_util.dumps(restaurants_cursor))]
        return make_response({"body":body}, 200, headers)
    elif request.method == "POST":
        dict_data = request.get_json()
        print(type(dict_data))
        is_valid = validate_json(dict_data, "restaurant.json")
        if is_valid:
            existing_restaurant = db.restaurants.find_one({"name":dict_data["name"]})
            if not existing_restaurant:
                dict_data["wines"]=[]
                #manager = db.clients.find_one({"_id":ObjectId(dict_data["manager_id"])})
                #if not manager:
                #    return make_response(make_message("The manager doesn't exist"), 400, headers)            
                db.restaurants.insert_one(dict_data)
                return make_response(make_message("Agregado exitosamente"), 200, headers)
            else:
                logging.warning("Attempted to write duplicated registry in restaurants collection")
                return make_response(make_message("Registro duplicado"), 409, headers)
        return make_response(make_message("Bad request"), 400, headers)


@app.route("/restaurants/<string:id>", methods=["PUT","PATCH","DELETE"])
def update_delete_restaurants(id: str):
    """ Function that redirects to the update and delete actions

    :param id: The id of the restaurant to be either deleted or updated
    :type id: str
    :return: The HTTP response
    :rtype: Response with a body tag and a HTTPStatus
    """
    if request.method in ("PUT","PATCH"):
        try:
            dict_data = request.get_json()
            is_valid = validate_json(dict_data, "restaurant.json")
            if is_valid:
                conflicting_restaurant = db.restaurants.find_one({"name":dict_data["name"]})
                if conflicting_restaurant:
                    return make_response(make_message("Conflicto entre registros. Otro restaurante ya tiene ese nombre asignado"), 409, headers)
                #manager = db.clients.find_one({"_id":ObjectId(dict_data["manager_id"])})
                #if not manager:
                #    return make_response(make_message("The manager doesn't exist"), 400, headers)  
                result = db.restaurants.replace_one({"_id": ObjectId(id)},dict_data)
                return make_response({"body":result.raw_result},200,headers)
            return make_response(make_message("Parámetros inválidos o faltantes"), 400, headers)
        except:
            return make_response(make_message("No se pudo procesar la solicitud. Confirme que el id sea válido"), 400, headers)
    elif request.method == "DELETE":
        try:
            result = db.restaurants.delete_one({"_id": ObjectId(id)})
            return make_response({"body":result.raw_result},200,headers)
        except:
            return make_response(make_message("No se pudo procesar la solicitud"), 400, headers)

# jsonData = json.loads('{"id" : "10","name": "DonOfDen","contact_number":1234567890}')

# # validate it
# is_valid = validate_json(jsonData, "wine.json")
# print(is_valid)

# jsonData = json.loads('{"name":"Nombre","country":"Spain","year":2010,"type":"Blue"}')
# is_valid = validate_json(jsonData,"wine.json")
# print(is_valid)

# jsonData = json.loads('{"name":"Nombre","country":"Spain","year":2010}')
# is_valid = validate_json(jsonData,"wine.json")
# print(is_valid)
