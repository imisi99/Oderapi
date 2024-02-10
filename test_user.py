from utils import *
from schemas.model_db import User
from starlette import status
from routers.user import GetUser, get_db

main.app.dependency_overrides[get_db] = overide_get_db
main.app.dependency_overrides[GetUser] = overide_get_user


def test_return_user(test_user):
    response = client.get("/user/details")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "Imisioluwa23"
    assert response.json()["firstname"] == "Imisioluwa"
    assert response.json()["lastname"] == "Isong"
    assert response.json()["email"] == "isongrichard234@gmail.com"
    assert response.json()["phone_number"] == "+234-9047-7100-32"

