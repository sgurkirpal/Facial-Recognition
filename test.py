import pytest
from server import app as app
from fastapi.testclient import TestClient
from asgi_lifespan import LifespanManager
import httpx


# testing search_face funtion
@pytest.mark.asyncio
async def test_search():
    async with LifespanManager(app):
        async with httpx.AsyncClient(app=app,base_url="http://0.0.0.0") as clientApp:
            response=await clientApp.post("/search_faces/",data={"k":4,"confidence":0.8},files={"file":open("./testing/Aaron_Peirsol_0002.jpg","rb")})
            json_result=response.json()
            assert json_result["status"]=="OK"
            assert json_result["body"]["matches"]["face1"][0]["id"]==39


# testing add_face funtion
@pytest.mark.asyncio
async def test_add():
    async with LifespanManager(app):
        async with httpx.AsyncClient(app=app,base_url="http://0.0.0.0") as clientApp:
            response=await clientApp.post("/add_face/",files={"file":open("./testing/Aaron_Eckhart_0001.jpg","rb")})
            json_result=response.json()
            assert json_result["status"]=="OK"
            assert json_result["body"]["Added_row"][0]["person_name"]=="Aaron_Eckhart_0001"


# testing add_faces_in_bulk funtion
@pytest.mark.asyncio
async def test_add_zip():
    async with LifespanManager(app):
        async with httpx.AsyncClient(app=app,base_url="http://0.0.0.0") as clientApp:
            response=await clientApp.post("/add_faces_in_bulk/",files={"file":open("./testing/test_zip.zip","rb")})
            json_result=response.json()
            assert json_result["status"]=="OK"
            assert json_result["body"]["Added_rows"][0]["person_name"]=="Aaron_Pena_0001"


# testing get_face_info funtion
@pytest.mark.asyncio
async def test_face_info():
    async with LifespanManager(app):
        async with httpx.AsyncClient(app=app,base_url="http://0.0.0.0") as clientApp:
            response=await clientApp.post("/get_face_info/",data={"api_key":"23","face_id":"125"})
            json_result=response.json()
            assert json_result["status"]=="OK"
            assert json_result["body"]["matches"][0]["person_name"]=="Adrian_Annus"


