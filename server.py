"""
    The file is the main server file which contains all the classes and methods
    for proper functionality of the server.
    Some assumptions:
    - If no face or multiple faces deteced in an image while adding to the database,
        then exception is raised.
    - If there are multiple faces detected while seaching, then all faces are displayed.
    - The format for json returned in search_faces is: 
        {
        "status": "OK",
        "body": {
            "matches": {
                "face1": [
                    {"id": 1, "person_name": "JK Lal"}
                    {"id": 2, "person_name": "JK Pal"}
                    {"id": 3, "person_name": "JK Hal"}
                ],
                "face2": [
                    {"id": 5, "person_name": "PK Lal"}
                    {"id": 4, "person_name": "PK Pal"}
                    {"id": 6, "person_name": "PK Hal"}
                ]
            }
        }
    - while adding faces, version is the number of rows already containing the same name+1.
    - location and date are kept null while adding.
    - for returning face_information, only the face_id is used and it returns whole of the face 
        information stored in the row.
}
"""

from tkinter.filedialog import LoadFileDialog
from fastapi import FastAPI, File, UploadFile, Form
import uvicorn
import face_recognition
from sqlalchemy import select
import numpy
import shutil
import tempfile
from pathlib import Path
import os
import sqlalchemy

face_encodings=[]   # stores the face encoding of all rows in the database
names=[]            # stores the names of persons in the database
ids=[]              # stores the primary key that is face_id
dic_name=[]         # stores the names of persons corresponding to the face_distance matrix
dic_id=[]           # stores the face_id corresponding to the face_distance matrix


# Database class to connect to postgres server and execute SQL queries
class Database():
    def __init__(self,db_string):
        self.db_string = db_string
        try:
            # creating sqlalchemy engine
            self.db = sqlalchemy.create_engine(self.db_string,pool_pre_ping=True)
            print("Database accessed ")
        except Exception as e:
            print(e)
        

    def execute(self,execute_string):
        try:
            self.db.execute(execute_string)
            print("Executed ")
        except Exception as e:
            print(e)


# The function adds encoding of all the rows in the database
# to a list as the list of numpy arrays which can be directly used
# to find face_distance
def get_all_encodings(con):
    global face_encodings, names
    face_encodings=[]
    names=[]
    rs=con.execute("select * from face_table;")
    for row in rs:
        face_encodings.append(numpy.array(row.encoding))
        names.append(row.name)
        ids.append(row.face_id)


# This class implements the parsing of the file which is passed as argument to the
# the functions. It contains functions which find the encoding as well as adds the 
# image to the database.
class ParseImage():
    # uploaded file as argument
    def __init__(self,image):
        self.image = image

    # returns the numpy array corresponding to the face encoding of the image
    # the function returns a list if there are multiple faces detected and 
    # raises an exception if there areno faces detected
    def get_encoding(self):
        if(len(face_recognition.face_encodings(self.image))==0):
            return None
        return face_recognition.face_encodings(self.image)

    # returns the numpy array corresponding to the face encoding of the image
    # the function raises an exception if there are no faces detected or
    # multiple faces deteced
    def get_encoding_for_adding(self):
        if(len(face_recognition.face_encodings(self.image))==0):
            return None
        if(len(face_recognition.face_encodings(self.image))>1):
            return None
        return face_recognition.face_encodings(self.image)[0].tolist()


    # the function returns a list of face_distances for all the faces detected in the image.
    # those lists are then sorted in increasing order to get most accurate results.
    def compare_images(self):
        output=[]
        lis=self.get_encoding()
        if(lis==None):
            return None
        for i in range(len(lis)):
            output.append(face_recognition.face_distance(face_encodings,lis[i]).tolist())
            for j in range(len(output[i])):
                dic_name.append({})
                dic_name[i][output[i][j]]=names[j]
                dic_id.append({})
                dic_id[i][output[i][j]]=ids[j]
        return output


# This class implements the functionality of adding faces from a zip file
# It takes the zip file as the argument which is then put in a temporary directory
# that path of the temporary directory is used to extract the zip file into another
# temporary directory.
class ZipExtractor():
    def __init__(self,file):
        # print(file.filename)
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            self.tmp_path = Path(tmp.name)
    

    # In this, the extracted folder is then walked through the os.walk method 
    # and all the files in that folder are then passed through face_recognition
    # functions and their encoding is calculated and then all the infomation is 
    # then put in the database with name of person as the name of the file.
    def get_file_path_and_add(self,db):
        ret=[]
        for root, dirs, files in os.walk(self.dir,topdown=True):
            for name in files:
                # print(os.path.join(root, name))
                image= face_recognition.load_image_file(os.path.join(root, name))
                image_parser=ParseImage(image)
                image_encoding=image_parser.get_encoding_for_adding()
                if(image_encoding==None):
                    return None
                file_name=str(name)
                person_name=file_name[:file_name.find('.')]
                version=1
                rs=db.db.execute("select * from face_table where name='"+person_name+"';")
                for row in rs:
                    version+=1
                f=db.db.execute("insert into face_table(name,version,encoding) values('"+person_name+"','"+str(version)+"','{"+str(image_encoding)[1:-1]+"}') returning face_id;")
                for row in f:
                     ret.append([row.face_id,person_name,version])
        return ret

    # extracting the zip file onto a temporary directory.
    def unpack(self):
        self.dir=tempfile.mkdtemp()
        print(self.dir,self.tmp_path)
        shutil.unpack_archive(self.tmp_path,self.dir)


# the function implements the adding of the faces to the database
# when the add_face function is called.
def add_image(file,db):
    my_file=file.file
    image = face_recognition.load_image_file(my_file)
    image_parser=ParseImage(image)
    image_encoding=image_parser.get_encoding_for_adding()
    if(image_encoding==None):
        return None
    file_name=str(file.filename)
    person_name=file_name[:file_name.find('.')]
    version=1
    rs=db.db.execute("select * from face_table where name='"+person_name+"';")
    for row in rs:
        version+=1
    f=db.db.execute("insert into face_table(name,version,encoding) values('"+person_name+"','"+str(version)+"','{"+str(image_encoding)[1:-1]+"}') returning face_id;")
    for row in f:
        return [row.face_id,person_name,version]

app=FastAPI()

# Implements the logic for performing the facial search
# here additional 2 parameters for k and confidence are passed which determine 
# the form of json to return. Here k is the number of top matches to print and confidence is
# a float value between 0 and 1. I have assumed it to be the value which is returned by the 
# face_distance function. Lesser the value better the matching. That is, if the value of 
# confidence is 0.4 then only entries with distance less than 0.4 are returned even if they are less 
# than k.
@app.post("/search_faces/")
async def search_faces(file: UploadFile =
                            File(..., description="An image file, possible containing multiple human faces."),k:int=Form(...),confidence:float=Form(...)):
    my_file=file.file   # converting file to python file object

    # connect to database server
    my_db=Database("postgresql://postgres:postgres@localhost/face_db")
    image = face_recognition.load_image_file(my_file)
    image_parser=ParseImage(image)

    get_all_encodings(my_db.db)

    output=image_parser.compare_images()
    if(output==None):
        return {"status": "Bad Request", "body": "Zero faces detected"}

    face_num=1

    #creating json in required format for k items and confidence 
    for_json={}
    for i in output:
        cnt=0
        for_json["face"+str(face_num)]=[]
        # print("Face"+str(face_num))
        face_num+=1
        i.sort()
        for j in i:
            cnt+=1
            if(cnt>k):
                break
            if(j>confidence):
                break
            sample_dic={}
            sample_dic["id"]=dic_id[face_num-2][j]
            sample_dic["person_name"]=dic_name[face_num-2][j]
            for_json["face"+str(face_num-1)].append(sample_dic)
            # print(dic_name[face_num-2][j])

    return {"status": "OK", "body": {"matches": for_json}}



# Implementing the logic for saving the face details in DB
# json returned contains the face_id for the added face, person_name ie the file name 
# and the version number. Version number is calculated by checking the number of rows 
# with same name in the databaes.
@app.post("/add_face/")
async def add_face(file: UploadFile =
                  File(..., description="An image file having a single human face.")):

    my_db=Database("postgresql://postgres:postgres@localhost/face_db")
    print(file.filename)
    output=add_image(file, my_db)    
    if(output==None):
        return {"status": "Bad Request", "body": "Zero or multiple faces detected"}
    return {"status": "OK", "body": {"Added_row": [{"id": output[0], "person_name": output[1],"version number":output[2]}]}}



# Implementing the logic for saving the face details in DB provided in zip format.
# json returned contains the face_id for all the added faces, person_name ie the file name 
# and the version number. Version number is calculated by checking the number of rows 
# with same name in the databaes.
@app.post("/add_faces_in_bulk/")
async def add_faces_in_bulk(file: UploadFile =
                           File(..., description="A ZIP file containing multiple face images.")):

    my_file=file.file
    print(file)
    zip=ZipExtractor(file)
    zip.unpack()
    my_db=Database("postgresql://postgres:postgres@localhost/face_db")
    output=zip.get_file_path_and_add(my_db)
    if(output==None):
        return {"status": "Bad Request", "body": "Zero or multiple faces detected"}
    json_list=[]
    for i in output:
        json_list.append({})
        json_list[len(json_list)-1]["id"]=i[0]
        json_list[len(json_list)-1]["person_name"]=i[1]
        json_list[len(json_list)-1]["version number"]=i[2]
    return {"status": "OK", "body": {"Added_rows": json_list}}



# Implement the logic for retrieving the details of a face record from DB.
# here, api key is of no use and on the basis of face_id which is also the primary
# key of the database, whole of the row is returned but in a better json format.
@app.post("/get_face_info/")
async def get_face_info(api_key: str = Form(...), face_id: str = Form(...)):
    my_db=Database("postgresql://postgres:postgres@localhost/face_db")
    rs=my_db.db.execute("select * from face_table where face_id="+face_id+";")
    name=""
    encoding=""
    version=""
    location=""
    date=""
    for row in rs:
        name=row.name
        encoding=row.encoding
        date=row.date
        version=row.version
        location=row.location
        
    return {"status": "OK", "body": {"matches": [{"id": face_id, "person_name": name,"version number":version,"date":date,"location":location,"encoding":encoding}]}}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
