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
                if result.modified_count:
                    return make_response(make_message("Exitosamente actualizado"),200,headers)
                return make_response(make_message("Vino no encontrado. Nada que actualizar"),404,headers)
            return make_response(make_message("Parámetros inválidos o faltantes"), 400, headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)
    elif request.method == "DELETE":
        try:
            result = db.wines.delete_one({"_id": ObjectId(id)})
            if result.deleted_count:
                return make_response(make_message("Exitosamente eliminado"),200,headers)
            return make_response(make_message("No se hallo el vino. Nada que eliminar"),404, headers)
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
        is_valid = validate_json(dict_data, "restaurant.json")
        if is_valid:
            existing_restaurant = db.restaurants.find_one({"name":dict_data["name"]})
            if not existing_restaurant:
                dict_data["wines"]=[]
                if dict_data.get("manager_id"):
                    try:
                        manager = db.clients.find_one({"_id":ObjectId(dict_data["manager_id"])})
                    except:
                        return make_response(make_message("Parametros invalidos o faltantes"), 400, headers)
                    if not manager:
                        return make_response(make_message("The manager doesn't exist"), 400, headers)
                else:
                    dict_data["manager_id"]=""
                db.restaurants.insert_one(dict_data)
                return make_response(make_message("Agregado exitosamente"), 200, headers)
            else:
                logging.warning("Attempted to write duplicated registry in restaurants collection")
                return make_response(make_message("Registro duplicado"), 409, headers)
        return make_response(make_message("Parámetros inválidos o faltantes"), 400, headers)


@app.route("/restaurants/<string:id>", methods=["GET","PUT","PATCH","DELETE"])
def update_delete_restaurants(id: str):
    """ Function that redirects to the update and delete actions

    :param id: The id of the restaurant to be either deleted or updated
    :type id: str
    :return: The HTTP response
    :rtype: Response with a body tag and a HTTPStatus
    """
    if request.method == "GET":
        try:
            selected_restaurant = db.restaurants.find_one({"_id": ObjectId(id)})
            if selected_restaurant:
                return make_response({"body":json.loads(json_util.dumps(selected_restaurant))},200,headers)
            return make_response(make_message("Recurso no encontrado"),404, headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)
    elif request.method in ("PUT","PATCH"):
        try:
            dict_data = request.get_json()
            is_valid = validate_json(dict_data, "restaurant.json")
            if is_valid:
                conflicting_restaurant = db.restaurants.find_one({"name":dict_data["name"]})
                if conflicting_restaurant:
                    return make_response(make_message("Conflicto entre registros. Otro restaurante ya tiene ese nombre asignado"), 409, headers)
                if dict_data.get("manager_id"):
                    manager = db.clients.find_one({"_id":ObjectId(dict_data["manager_id"])})
                    if not manager:
                        return make_response(make_message("The manager doesn't exist"), 400, headers)
                else:
                    dict_data["manager_id"]=""
                dict_data["wines"]=[]

                result = db.restaurants.replace_one({"_id": ObjectId(id)},dict_data)
                if result.modified_count:
                    return make_response(make_message("Actualizado exitosamente"),200,headers)
                return make_response(make_message("El restaurante no fue hallado. Nada que actualizar"), 404, headers)
            return make_response(make_message("Parámetros inválidos o faltantes"), 400, headers)
        except:
            return make_response(make_message("No se pudo procesar la solicitud. Confirme que el id sea válido"), 400, headers)
    elif request.method == "DELETE":
        try:
            result = db.restaurants.delete_one({"_id": ObjectId(id)})
            if result.deleted_count:
                return make_response(make_message("Eliminado exitosamente"),200,headers)
            return make_response(make_message("No se hallo el restaurante. Nada que eliminar"),404, headers)
        except:
            return make_response(make_message("No se pudo procesar la solicitud"), 400, headers)


@app.route("/restaurants/<string:id>/wines", methods=["GET","POST"])
def wines_restaurants(id):
    if request.method == "GET":
        try:
            selected_restaurant = db.restaurants.find_one({"_id": ObjectId(id)})
            if selected_restaurant:
                return make_response({"body":json.loads(json_util.dumps(selected_restaurant["wines"]))},200,headers)
            return make_response(make_message("Restaurante no encontrado"),404, headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)
    elif request.method == "POST":
        try:
            selected_restaurant = db.restaurants.find_one({"_id": ObjectId(id)})
            if selected_restaurant:
                dict_data = request.get_json()
                is_valid = validate_json(dict_data, "add_wine.json")
                if is_valid:
                    existing_wine = db.wines.find_one({"_id": ObjectId(dict_data["wine_id"])})
                    if existing_wine:
                        wine_object_id = json.loads(json_util.dumps(existing_wine["_id"]))
                        wine_id = wine_object_id["$oid"]
                        if wine_id not in selected_restaurant["wines"]:
                            selected_restaurant["wines"].append(wine_id)
                        else:
                            return make_response(make_message("Vino ya existente en restaurante"),409, headers)
                        result = db.restaurants.replace_one({"_id": ObjectId(id)},selected_restaurant)
                        if result.modified_count:
                            return make_response(make_message("Actualizado exitosamente"),200,headers)
                        return make_message(make_message("No se hallo el restaurante. Nada que actualizar"), 404, headers)
                    else:
                        return make_response(make_message("Could not add. Wine was not found"), 404, headers)      
                return make_response(make_message("Parametros invalidos o faltantes"),400,headers)
            return make_response(make_message("Restaurante no encontrado"),404, headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)


@app.route("/restaurants/<string:restaurant_id>/wines/<string:wine_id>", methods=["DELETE"])
def delete_wine_from_restaurant(restaurant_id:str, wine_id:str):
    if request.method == "DELETE":
        try:
            selected_restaurant = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
            if selected_restaurant:
                existing_wine = db.wines.find_one({"_id": ObjectId(wine_id)})
                if existing_wine:
                    if wine_id in selected_restaurant["wines"]:
                        selected_restaurant["wines"].remove(wine_id)
                        result = db.restaurants.replace_one({"_id": ObjectId(restaurant_id)},selected_restaurant)
                        if result.modified_count:
                            return make_response(make_message("Exitosamente actualizado"),200,headers)
                        return make_response(make_message("No se hallo el restaurante. Nada que actualizar"), 404, headers)
                    else:
                        return make_response(make_message("Vino no fue hallado en el restaurante. Nada que hacer"), 404, headers)
                else:
                    return make_response(make_message("Vino no hallado en la BD"), 404, headers) 
                return make_response()
            return make_response(make_message("Recurso no encontrado"),404, headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)


@app.route("/clients", methods=["GET", "POST"])
def read_create_clients():
    """Function that redirects to the create and read functions

    :return: The HTTP response
    :rtype: Response with a body tag and a HTTPStatus code
    """
    if request.method == "GET":
        clients_cursor = db.clients.find()
        body = [client for client in json.loads(json_util.dumps(clients_cursor))]
        return make_response({"body":body}, 200, headers)
    elif request.method == "POST":
        dict_data = request.get_json()
        is_valid = validate_json(dict_data, "client.json")
        if is_valid:
            existing_client = db.clients.find_one({"name":dict_data["name"]})
            if not existing_client:
                dict_data["restaurants"]=[]
                db.clients.insert_one(dict_data)
                return make_response(make_message("Agregado exitosamente"), 200, headers)
            else:
                logging.warning("Attempted to write duplicated registry in client collection")
                return make_response(make_message("Registro duplicado"), 409, headers)
        return make_response(make_message("Parámetros inválidos o faltantes"), 400, headers)


@app.route("/clients/<string:id>", methods=["GET","PUT","PATCH","DELETE"])
def update_delete_clients(id: str):
    """ Function that redirects to the update and delete actions

    :param id: The id of the client to be either deleted or updated
    :type id: str
    :return: The HTTP response
    :rtype: Response with a body tag and a HTTPStatus
    """
    if request.method == "GET":
        try:
            selected_client = db.clients.find_one({"_id": ObjectId(id)})
            if selected_client:
                return make_response({"body":json.loads(json_util.dumps(selected_client))},200,headers)
            return make_response(make_message("Recurso no encontrado"),404, headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)
    elif request.method in ("PUT","PATCH"):
        try:
            dict_data = request.get_json()
            is_valid = validate_json(dict_data, "client.json")
            if is_valid:
                conflicting_client = db.clients.find_one({"name":dict_data["name"]})
                if conflicting_client:
                    return make_response(make_message("Conflicto entre registros. Otro cliente ya tiene ese nombre asignado"), 409, headers)
                dict_data["restaurants"]=[]
                result = db.clients.replace_one({"_id": ObjectId(id)},dict_data)
                if result.modified_count:
                    return make_response(make_message("Actualizado exitosamente"),200,headers)
                return make_response(make_message("El restaurante no fue hallado. Nada que actualizar"), 404, headers)
            return make_response(make_message("Parámetros inválidos o faltantes"), 400, headers)
        except:
            return make_response(make_message("No se pudo procesar la solicitud. Confirme que el id sea válido"), 400, headers)
    elif request.method == "DELETE":
        try:
            result = db.clients.delete_one({"_id": ObjectId(id)})
            if result.deleted_count:
                return make_response(make_message("Eliminado exitosamente"),200,headers)
            return make_response(make_message("No se hallo el cliente. Nada que eliminar"),404, headers)
        except:
            return make_response(make_message("No se pudo procesar la solicitud"), 400, headers)


@app.route("/clients/<string:id>/restaurants", methods=["GET","POST"])
def clients_restaurants(id):
    if request.method == "GET":
        try:
            selected_client = db.clients.find_one({"_id": ObjectId(id)})
            if selected_client:
                return make_response({"body":json.loads(json_util.dumps(selected_client["restaurants"]))},200,headers)
            return make_response(make_message("Restaurante no encontrado"),404, headers)
        except:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)
    elif request.method == "POST":
        try:
            selected_client = db.clients.find_one({"_id": ObjectId(id)})
            if selected_client:
                dict_data = request.get_json()
                is_valid = validate_json(dict_data, "add_restaurant.json")
                if is_valid:
                    existing_restaurant = db.restaurants.find_one({"_id": ObjectId(dict_data["restaurant_id"])})
                    if existing_restaurant:
                        restaurant_object_id = json.loads(json_util.dumps(existing_restaurant["_id"]))
                        restaurant_id = restaurant_object_id["$oid"]
                        if restaurant_id not in selected_client["restaurants"]:
                            selected_client["restaurants"].append(restaurant_id)
                        else:
                            return make_response(make_message("Restaurante ya existente para el cliente"),409, headers)
                        result = db.clients.replace_one({"_id": ObjectId(id)},selected_client)
                        print(result.raw_result)
                        if result.modified_count:
                            return make_response(make_message("Actualizado exitosamente"),200,headers)
                        return make_response(make_message("No se hallo el cliente. Nada que actualizar"), 404, headers)
                    else:
                        return make_response(make_message("Could not add. Wine was not found"), 404, headers)      
                return make_response(make_message("Parametros invalidos o faltantes"),400,headers)
            return make_response(make_message("Restaurante no encontrado"),404, headers)
        except ZeroDivisionError as e:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que el id sea válido"), 400, headers)


@app.route("/clients/<string:client_id>/restaurants/<string:restaurant_id>", methods=["DELETE"])
def delete_restaurant_from_client(client_id:str, restaurant_id:str):
    if request.method == "DELETE":
        try:
            selected_client = db.clients.find_one({"_id": ObjectId(client_id)})
            if selected_client:
                existing_restaurant = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
                if existing_restaurant:
                    if restaurant_id in selected_client["restaurants"]:
                        selected_client["restaurants"].remove(restaurant_id)
                        result = db.clients.replace_one({"_id": ObjectId(client_id)},selected_client)
                        if result.modified_count:
                            return make_response(make_message("Exitosamente actualizado"),200,headers)
                        return make_response(make_message("No se hallo el cliente. Nada que actualizar"), 404, headers)
                    else:
                        return make_response(make_message("Restaurante no fue hallado en el cliente. Nada que hacer"), 404, headers)
                else:
                    return make_response(make_message("Restaurante no hallado en la BD"), 404, headers) 
                return make_response()
            return make_response(make_message("Recurso no encontrado"),404, headers)
        except ZeroDivisionError as e:
            return make_response(make_message("No se pudo procesar la solcitud. Confirme que los id's sean válido"), 400, headers)
