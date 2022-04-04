import ast
from flask import jsonify
from pydantic import ValidationError
from app.schemas import PydanticError


def bad_request(message, error_code=None):
    if str(message) == "Not Authorized" or str(message) == "Invalid credentials":
        return forbidden(message)
    if isinstance(message, (ValidationError, PydanticError)):
        pydantic_errors = message.errors()
        for error in pydantic_errors:
            if error.get("msg", "nothing")[0] == "{":
                error.update(ast.literal_eval(error["msg"]))
        error = {"error": "bad request", "message": pydantic_errors}
    else:
        error = {"error": "bad request", "message": str(message)}
    if error_code is not None:
        error["code"] = error_code
    response = jsonify(error)
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({"error": "unauthorized", "message": str(message)})
    response.status_code = 403
    return response


def forbidden(message="Unauthorized"):
    response = jsonify({"error": "forbidden", "message": str(message)})
    response.status_code = 403
    return response


def not_found():
    response = jsonify({"error": "not found"})
    response.status_code = 404
    return response


def server_error():
    response = jsonify({"error": "Unknown error"})
    response.status_code = 500
    return response
