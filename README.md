## 1. What does this program do?

- The program develops an application that performs the “facial search” on a database of images. The application is a secure API service which can be invoked by sending an HTTP post request to the API’s endpoint.
- LFW face dataset is used to test the API.
- The parameters for the SQL queries are dynamically populated at runtime from
  the supplied objects.
- One of the functions 'search_faces' implements the retreival of top-k matches in the database.
- Others are responsible for adding to the database and displaying face information.
- Face_recognition library is used to implement the face recognition API.
- PostgreSQL database is used for storing the face representation and information.

## 2. A description of how this program works (i.e. its logic)

- The program/project is created in virtual environment.
- The API structure of the library is defined by :

```
 from fastapi import FastAPI, File, UploadFile, Form
 app = FastAPI()

 @app.post("/search_faces/")
 async def search_faces(file: UploadFile =
 File(..., description="An image file, possible containing multiple human faces."))

 @app.post("/add_face/")
 async def add_face(file: UploadFile =
 File(..., description="An image file having a single human face."))

 @app.post("/add_faces_in_bulk/")
 async def add_faces_in_bulk(file: UploadFile =
 File(..., description="A ZIP file containing multiple face images."))

 @app.post("/get_face_info/")
 async def get_face_info(api_key: str = Form(...), face_id: str = Form(...)):
```

- Main API code that is the server code resides in the server.py.
- First of all the dataset is loaded into the database.
- Database used is local postgres server.The database name is face_db and table name is face_table.The column names are face_id (auto incrementing primary key), name of person, version number, location, date which are by default null and encoding of the image which is a float array of 128 length.
- Dataset loading is done seperately in main.py file.
- Different classes are made for different tasks and SOLID principles are followed.
- server.py is main server file which contains all the classes and methods
  for proper functionality of the server.
- Functions implemented are:

  - 'search_face':

    - Implements the logic for performing the facial search
    - Here additional 2 parameters for k and confidence are passed which determine
      the form of json to return. Here k is the number of top matches to print and confidence is
      a float value between 0 and 1.
    - I have assumed it to be the value which is returned by the
      face_distance function. Lesser the value better the matching. That is, if the value of
      confidence is 0.4 then only entries with distance less than 0.4 are returned even if they are less
      than k.
    - To get the matchings, face_distance function of face_recognition library is used.

  - 'add_face':
    - Implementing the logic for saving the face details in DB.
    - json returned contains the face_id for the added face, person_name ie the file name
      and the version number. Version number is calculated by checking the number of rows
      with same name in the databaes.
  - 'add_faces_in_bulk' :
    - Implementing the logic for saving the face details in DB provided in zip format.
    - json returned contains the face_id for all the added faces, person_name ie the file name
      and the version number. Version number is calculated by checking the number of rows
      with same name in the databaes.
    - the zip file is put in a temporary directory and that path of the temporary directory is used to extract the zip file into another temporary directory.
    - the extracted folder is then walked through the os.walk method
      and all the files in that folder are then passed through face_recognition
      functions and their encoding is calculated and then all the infomation is
      then put in the database with name of person as the name of the file.
  - 'get_face_info':
    - Implement the logic for retrieving the details of a face record from DB.
    - Here, api key is of no use and on the basis of face_id which is also the primary
      key of the database, whole of the row is returned but in a better json format.

## 3. Some Assumptions

- If no face or multiple faces deteced in an image while adding to the database,
  then exception is raised.
- If there are multiple faces detected while seaching, then all faces are displayed.
- The format for json returned in search_faces is:
  ```
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
  ```
- while adding faces, version is the number of rows already containing the same name+1.
- location and date are kept null while adding.
- for returning face_information, only the face_id is used and it returns whole of the face information stored in the row.
- I have assumed the confidence value in search_faces function to be the value which is returned by the
  face_distance function. Lesser the value better the matching. That is, if the value of
  confidence is 0.4 then only entries with distance less than 0.4 are returned even if they are less
  than k.

## 4. How to compile and run this program

- The project was made in virtual env and requirements.txt is attched.
  ```
      cd sde/Scripts
      ./activate
  ```
- To add the dataset in the database, run `python main.py`. (As the dataset is quite large, hence it is not included in the submission zip file, so while running this file, the path to the
  dataset needs to be changed in the file.)

- Running the server on fastapi: `uvicorn server:app --reload`.
- Tests are implemented using pytest. Running tests: `pytest test.py`
- To get the coverage: run

```
    coverage run -m pytest test.py
    coverage report
```

## 5. Provide a snapshot of a sample run

- Snapshots are attached in a folder named ScreenShots.

## 6. Github Link

https://github.com/sgurkirpal/cs305_2022

## 7. Results

- I am getting a coverage of 95%. Screenshot is attached in a folder named Screenshot.
