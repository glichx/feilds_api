import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Load environment variables
load_dotenv()

# load env
mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
database_name = os.getenv("DATABASE_NAME")
collection_name = os.getenv("COLLECTION_NAME")

# mongo
mongo_client = MongoClient(mongo_uri)
db = mongo_client[str(database_name)]
collection = db[str(collection_name)]

# initialize fastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FieldsRequest(BaseModel):
    object_id: str
    fields: List[str]

@app.get("/")
def read_root():
    return JSONResponse(content={"status": "success"}, status_code=200)

@app.post("/get_fields_assignment")
async def get_fields_from_assignment(request: FieldsRequest):
    try:
        object_id = ObjectId(request.object_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    document = collection.find_one({"_id": object_id})
    if not document:
        # Debug output
        print(f"No document found for ObjectId: {request.object_id}")
        print(f"Database: {database_name}, Collection: {collection_name}")
        return JSONResponse(content={"error": "Document not found", "object_id": str(request.object_id)}, status_code=404)

    response = {}
    for field_key in request.fields:
        field_value = document.get("final_assignment", {}).get(field_key, None)
        response[field_key] = field_value

    return JSONResponse(content=response)

@app.post("/get_fields_release")
async def get_fields_from_release(request: FieldsRequest):
    try:
        object_id = ObjectId(request.object_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    document = collection.find_one({"_id": object_id})
    if not document:
        # Debug output
        print(f"No document found for ObjectId: {request.object_id}")
        print(f"Database: {database_name}, Collection: {collection_name}")
        return JSONResponse(content={"error": "Document not found", "object_id": str(request.object_id)}, status_code=404)

    response = {}
    for field_key in request.fields:
        field_value = document.get("final_release", {}).get(field_key, None)
        response[field_key] = field_value

    return JSONResponse(content=response)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)