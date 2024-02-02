from typing import Union, Any
from django.http.response import HttpResponse, JsonResponse


def create_response(data: Union[Any, dict] = None,
                    code: int = None,
                    description: str = None,
                    message: str = None,
                    json_response: bool = True
                    ):

    _response = {"code": 200 if code is None else code,
                 "description": description,
                 "data": data,
                 "message": message}

    if json_response:
        return JsonResponse(_response)
    return HttpResponse(_response)
