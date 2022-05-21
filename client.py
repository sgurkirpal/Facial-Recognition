"""
    This file is not used anymore. Just attaching. It is testing using fastapi.
    USELESS FILE
    NOT RELEVANT TO ASSINGNMENT
"""

from fastapi import FastAPI, File, UploadFile, Form
from server import app as serv
from fastapi.testclient import TestClient


clientApp=FastAPI()
server=TestClient(serv)


@clientApp.post('/search_faces/')
async def search_faces(file: UploadFile =
                            File(..., description="An image file, possible containing multiple human faces."),k:int=10,confidence:float=0.6):
    global server
    dat={}
    fil={}
    fil["file"]=file.file
    dat["k"]=k
    dat["confidence"]=confidence
    result=server.post("/search_faces/",files=fil,data=dat)
    print(result)
    return result.json()


@clientApp.post('/add_face/')
async def add_face(file: UploadFile =File(..., description="An image file, possible containing multiple human faces.")):
    global server
    fil={}
    fil["file"]=file.file
    print(file.filename)
    result=server.post("/add_face/",files=fil)
    print(result)
    return result.json()


@clientApp.post('/add_faces_in_bulk/')
async def add_faces_in_bulk(file: UploadFile =File(..., description="An image file, possible containing multiple human faces.")):
    global server
    fil={}
    fil["file"]=file.file
    print(file.filename)
    result=server.post("/add_faces_in_bulk/",files=fil)
    print(result)
    return result.json()

    
@clientApp.post('/get_face_info/')
async def get_face_info(api_key: str = Form(...), face_id: str = Form(...)):
    global server
    dat={}
    dat["face_id"]=face_id
    dat["api_key"]=api_key
    result=server.post("/get_face_info/",data=dat)
    print(result)
    return result.json()

    
