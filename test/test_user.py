from .utils import *
from starlette import status
from app.routers.user import GetUser, get_db, Autentication, access, timedelta, jwt, secret, algorithm

app.dependency_overrides[get_db] = overide_get_db
app.dependency_overrides[GetUser] = overide_get_user


def test_return_user(test_user):
    response = client.get("/user/details")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "Imisioluwa23"
    assert response.json()["firstname"] == "Imisioluwa"
    assert response.json()["lastname"] == "Isong"
    assert response.json()["email"] == "isongrichard234@gmail.com"
    assert response.json()["phone_number"] == "+234-9047-7100-32"


def test_user_signup(test_user):
    form = {
        "first_name": "Imisioluwa",
        "last_name": "Isong",
        "username": "Username23",
        "email": "email@gmail.com",
        "phone_number": "+234-9047-7100-37",
        "password": hash.hash("Interstellar.")
    }
    response = client.post("/user/signup", json=form)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == "User has been created successfully."


def test_user_pass_recovery(test_user):
    form = {
        "password": "Interstellar.",
        "confirm_password": "Interstellar."
    }
    response = client.put("/user/password/recovery",
                          params={"username": "Imisioluwa23", "email": "isongrichard234@gmail.com",
                                  "phone_number": "+234-9047-7100-32"}, json=form)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == "Your password has been changed successfully"


def test_update_user_details(test_user):
    form = {
        "first_name": "Imisioluwa",
        "last_name": "Isong",
        "email": "isongimisioluwa234@gmail.com",
        "username": "Richard23",
        "phone_number": "+234-9047-7100-37",
        "password": hash.hash("Interstellar.")
    }

    response = client.put("/user/update-details", json=form)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == "Details has been updated successfully"


def test_delete_user(test_user):
    response = client.delete("/user/delete-user")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_authentication(test_user):
    db = test_begin()

    authenticated = Autentication(test_user.username, "Imisioluwa234.", db)
    assert authenticated is not None
    assert authenticated.username == test_user.username


def test_access():
    username = "Imisioluwa23"
    user_id = 1
    expired = timedelta(minutes=15)

    token = access(username, user_id, expired)

    decode = jwt.decode(token, secret, algorithms=algorithm)

    assert decode['sub'] == username
    assert decode['id'] == user_id


@pytest.mark.asyncio
async def test_get_user(test_user):
    encode = {'sub': 'Imisioluwa23', 'id': 1}
    token = jwt.encode(encode, secret, algorithm=algorithm)

    user = await GetUser(token=token)
    assert user == {"username": "Imisioluwa23", "user_id": 1}
