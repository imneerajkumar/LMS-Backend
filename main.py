import os
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from models import Student, Address 
from dotenv import load_dotenv

# uvicorn main:app --reload
app = FastAPI()
load_dotenv()

mongodb_url = os.getenv("MONGODB_URL")
client = MongoClient(mongodb_url)
db = client["Library"]
students_collection = db["students"]

# Create a new student
@app.post("/students/", status_code=201)
async def create_student(student: Student):
    inserted_student = students_collection.insert_one(student.dict())
    student_id = str(inserted_student.inserted_id)
    return {"id": student_id}

# Get all students
@app.get("/students/", status_code=200)
async def get_students():
    students = []
    for student in students_collection.find():
        students.append({
            "name": student["name"],
            "age": student["age"]
        })
    return {"data": students}

# Get a student by ID
@app.get("/students/{student_id}", response_model=Student, status_code=200)
async def get_student(student_id: str):
    student = students_collection.find_one({"_id": ObjectId(student_id)})
    if student:
        return {
            "id": str(student["_id"]),
            **student
        }
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Update a student by ID
@app.patch("/students/{student_id}", status_code=204)
async def update_student(student_id: str, student_update: Student):
    student_update_dict = student_update.dict(exclude_unset=True)
    updated_student = students_collection.update_one({"_id": ObjectId(student_id)}, {"$set": student_update_dict})

    if updated_student.modified_count:
        return {}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Delete a student by ID
@app.delete("/students/{student_id}", status_code=200)
async def delete_student(student_id: str):
    deleted_student = students_collection.delete_one({"_id": ObjectId(student_id)})
    if deleted_student.deleted_count:
        return {}
    else:
        raise HTTPException(status_code=404, detail="Student not found")
