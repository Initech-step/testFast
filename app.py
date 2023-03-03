from typing import Union
import pymongo
from fastapi import FastAPI, status, HTTPException, Header
from bson.objectid import ObjectId
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"]
)

"""define db credentials"""
username = 'iniabasiDev'
pword = 'klZTWheObvDoH6yG'
AUTHENTICATION='J4kvV2xfD0YvPLEpM4zg7GQHtA3hyKfSRgcEtNGU'

"""connect to database"""
client = pymongo.MongoClient(f"mongodb+srv://{username}:{pword}@cluster0.vi5mjm8.mongodb.net/?retryWrites=true&w=majority")
db = client['NUASA']
print(db)

"""define models"""
class Year(BaseModel):
    year:str

class Course(BaseModel):
    course_year:str
    course_name:str
    course_code:str

class Material(BaseModel):
    course_id:str
    material_title:str
    material_description:str
    material_link:str

def checkSRC(src_auth):
    if src_auth == AUTHENTICATION:
        return True
    return False

"""
ROOT
"""
@app.get("/")
def read_root():
    return {
            "status":True,
            "application":"NUASA resource archives backend server",
            "developer": "Ini-abasi Etim, DOA (2023)",
            "date": "28-02-2023"
            }

"""
YEAR APIS
"""
@app.post("/api/year/", status_code=status.HTTP_201_CREATED)
def create_year(year:Year, auth:str=Header()):
    if checkSRC(auth):
        year_dict = year.dict()
        year_collection = db.years
        match = year_collection.find_one({'year':year_dict['year']})
        if match == None:
            year_collection.insert_one(year_dict)
            return {'status':True}
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Another year with the same name exists')
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You cant take this action from your IP address')

@app.get("/api/year/", status_code=status.HTTP_200_OK)
def get_years():
    year_collection = db.years
    data = year_collection.find({})
    serializable_data = [{'id': str(d.get('_id')), 'year': d.get('year')} for d in data]
    return {'status':True, 'years':serializable_data}

"""
COURSE APIS
"""
@app.post("/api/add_course/", status_code=status.HTTP_201_CREATED)
def add_course(course:Course, auth:str=Header()):
    if checkSRC(auth):
        course_dict = course.dict()
        course_collection = db.courses
        match = course_collection.find_one({'course_code':course_dict['course_code']})

        if match == None:
            course_collection.insert_one(course_dict)
            return {'status':True}
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Another course with the same code exists')
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You cant take this action from your IP address')

@app.get("/api/course/{year_id}", status_code=status.HTTP_200_OK)
def get_course(year_id:str):
    course_collection = db.courses
    data = course_collection.find({'course_year':year_id})
    serializable_data = [{'id': str(d.get('_id')), 'course_name': d.get('course_name'), 'course_code': d.get('course_code'), 'course_year': str(d.get('course_year'))} for d in data]
    return {'status':True, 'courses':serializable_data}

"""
MATERIAL APIS
"""
@app.get("/api/materials/{course_id}/", status_code=status.HTTP_200_OK)
def get_materials(course_id:str):
    materials_collection = db.resources
    data = materials_collection.find({'course_id':course_id})
    serializable_data = []
    for d in data:
        serializable_data.append({
            'id': str(d.get('_id')),
            'course_id': str(d.get('course_id')),
            'material_title': d.get('material_title'), 
            'material_description': d.get('material_description'),
            'material_link': d.get('material_link')
        })
        return {'status':True, 'materials':serializable_data}

@app.post("/api/add_materials/", status_code=status.HTTP_201_CREATED)
def add_materials(material:Material, auth:str=Header()):
    if checkSRC(auth):
        material_dict = material.dict()
        rescources_collection = db.resources
        rescources_collection.insert_one(material_dict)
        return {'status':True}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You cant take this action from your IP address')

@app.delete('/api/del_materials/{material_id}/', status_code=status.HTTP_200_OK)
def delete_material(material_id:str, auth:str=Header()):
    if checkSRC(auth):
        material_collection = db.resources
        data = material_collection.find_one({'_id': ObjectId(material_id)})
        if data == None:
            return {'status':False, 'message':'Target id is not found'}
        material_collection.delete_one(data)
        return {'status':True}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You cant take this action from your IP address')

