import inspect
from functools import wraps
from flask import request
from pydantic.main import ModelMetaclass
from app.errors import bad_request


def validate_schema(func):
    """
    Decorator for route methods which will validate JSON in request
    using a Pydantic model.

    example::

        @api.route('/signup', methods=['POST'])
        @validate_schema()
        def sign_up(user: schemas.UserCreate):
            ...

    The request will be verified based on the UserCreate schema.
    If validation is successfull the function will receive user object as input.
    If validation fails the decorator will return a 400 error with error messages.

    Each endpoint can only have one schema parameter as input.
    """

    def get_and_validate_data():
        """
        Get json data from request and return as dict.
        Works with both old datastructure: {"data": {"attributes": ...}}
        and new: {...}
        """
        try:
            data = request.get_json()
        except:
            data = {}
        if isinstance(data, str):
            raise Exception("Data format should be json not string")
        if (
            data is not None
            and "data" in data
            and isinstance(data["data"], dict)
            and "attributes" in data["data"]
        ):
            return data["data"]["attributes"]
        return data

    @wraps(func)
    def wrapper(*args, **kwargs):
        schema = None
        schema_parameter = None
        additional_parameters = {}
        func_signature = inspect.signature(func)
        for parameter in func_signature.parameters:
            if schema is not None:
                raise Exception("Max one schema per endpoint")
            if isinstance(
                func_signature.parameters[parameter].annotation, ModelMetaclass
            ):
                schema_parameter = parameter
                schema = func_signature.parameters[parameter].annotation
            else:
                print(additional_parameters)
                print(kwargs)
                additional_parameters[parameter] = kwargs[parameter]
        if schema is None or schema_parameter is None:
            raise Exception("No schema defined for endpoint")
        try:
            new_obj = get_and_validate_data()
            if new_obj is None:
                new_obj = {}
            kwargs[schema_parameter] = schema(**{**new_obj, **additional_parameters})
        except Exception as e:
            return bad_request(e)
        res = func(*args, **kwargs)
        return res

    return wrapper
