"""
    This file is responsible for storing the dataset images and their encodings
    into postgres database server. The database name is face_db and table name is face_table.
    the column names are face_id (auto incrementing primary key), name of person, 
    version number, location, date which are by default null and encoding of the image 
    which is a float array of 128 length.
"""
import face_recognition
import os
import psycopg2
import sqlalchemy

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


# class that contains functions to get image representation
class GetImages():
    def __init__(self,basepath):
        self.basepath=basepath

    # extract version from image
    def get_version(self,image_name,folder_name):
        return image_name[len(folder_name)+1:-4]

    # get encoding from image
    # if no face detected, then empty list hence that image is ignored
    def get_encoding(self,filepath):
        if(len(face_recognition.face_encodings(filepath))==0):
            return None
        return face_recognition.face_encodings(filepath)[0].tolist()

    # collects metadata for image and stores it into the database
    def get_metadata(self,new_path,folder_name,db):
        with os.scandir(new_path) as images:
            for image in images:
                myimage=face_recognition.load_image_file(new_path+'/'+image.name)
                # print(image.name)
                myimage_encoding=self.get_encoding(myimage)
                if(myimage_encoding==None):
                    continue
                myimage_version=self.get_version(image.name,folder_name)
                # print(str(myimage_encoding)[1:-1])
                try:
                    db.execute("insert into face_table(name,version,encoding) values('"+folder_name+"','"+myimage_version+"','{"+str(myimage_encoding)[1:-1]+"}');")
                except Exception as e:
                    print(e)
                


if __name__ == '__main__':
    # connect to database server
    my_db=Database("postgresql://postgres:postgres@localhost/face_db")

    # create table if not already created
    my_db.execute("create table if not exists face_table(face_id SERIAL PRIMARY KEY,name VARCHAR(100) NOT NULL, version VARCHAR(100),date DATE,location VARCHAR(256),encoding float[128] NOT NULL)")

    # path to the dataset
    basepath='archive/lfw_funneled/'

    image_engine=GetImages(basepath)
    with os.scandir(basepath) as entries:
        for entry in entries:
            data=image_engine.get_metadata(image_engine.basepath+entry.name,entry.name,my_db)
            
