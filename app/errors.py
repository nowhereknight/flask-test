from flask import make_response
from app import app, db

headers = {"Content-Type": "application/json"}

@app.errorhandler(404)
def not_found_error(error):
    return make_response({"msg":'Recurso no encontrado'}, 404, headers)


@app.errorhandler(405)
def method_not_allowed(error):
    #db.session.rollback()
    return make_response({"msg":"Metodo no soportado"}, 405, headers)

@app.errorhandler(400)
def method_not_allowed(error):
    #db.session.rollback()
    return make_response({"msg":"Solicitud inválida"}, 405, headers)

@app.errorhandler(500)
def internal_error(error):
    #db.session.rollback()
    return make_response({"msg":"Error de servidor"}, 500, headers)