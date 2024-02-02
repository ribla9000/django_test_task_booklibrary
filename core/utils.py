import json
import uuid


def get_post_values(items: tuple):
    return dict((key, value) for key, value in items if key != "csrfmiddlewaretoken")


def convert_cookies_str_to_dict(cookies: str):
    if cookies is None:
        return None
    cookies = cookies.replace("True", "'True'")
    cookies = cookies.replace("False", "'False'")
    user_values = cookies.replace("\'", "\"")
    json_object = json.loads(user_values)
    json_object["is_author"] = False if json_object["is_author"] == "False" else True
    return json_object


def get_table_values(description: tuple, data: list):
    return [
        dict(zip([col[0] for col in description], row))
        for row in data
    ]


def handle_uploaded_file(image, static_dir: str):
    file_type = str(image).split(".")[-1]
    random_name = uuid.uuid4()
    with open(f'{static_dir}/{random_name}.{file_type}', 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    return f"{random_name}.{file_type}"