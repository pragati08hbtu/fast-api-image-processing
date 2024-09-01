from celery import Celery
import csv
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, UploadFile, HTTPException, BackgroundTasks
from io import BytesIO
from pydantic import BaseModel
import os
import requests
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# FastAPI app
app = FastAPI()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Celery setup
REDIS_URL = os.getenv("REDIS_URL")
celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

# Models
class ImageProcessingRequest(Base):
    __tablename__ = "image_processing_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True)
    status = Column(String, default="Pending")
    output_csv = Column(Text, nullable=True)
    webhook_url = Column(String, nullable=True)

# Pydantic model for request
class UploadResponse(BaseModel):
    request_id: str

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# Helper function to save image and return URL
def save_image(image_buffer, filename, output_directory="output_images"):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    filepath = f"{output_directory}/{filename}.jpg"

    with open(filepath, "wb") as f:
        f.write(image_buffer.getvalue())

    return filepath

# Celery task for image processing
@celery.task
def process_images(request_id, csv_data, webhook_url=None):
    db = SessionLocal()
    request_record = db.query(ImageProcessingRequest).filter_by(request_id=request_id).first()
    
    try:
        output_csv_data = []
        for row in csv_data:
            reader = csv.reader([row])

            for fields in reader:
                serial_no = fields[0]
                product_name = fields[1]
                image_urls = fields[2]

            input_urls = [url.strip() for url in image_urls.split(',')]
            output_urls = []

            for url in input_urls:
                response = requests.get(url, stream=True).raw
                img = Image.open(response)
                img = img.convert("RGB")
                output_buffer = BytesIO()
                img.save(output_buffer, format="JPEG", quality=50)
                
                output_url = save_image(output_buffer, f"{product_name}_{uuid.uuid4()}")
                output_urls.append(output_url)
            
            output_csv_data.append(f"{serial_no},{product_name},{','.join(input_urls)},{','.join(output_urls)}")
        
        # Store result in the database
        request_record.status = "Completed"
        request_record.output_csv = "\n".join(output_csv_data)
        db.commit()
        
        # Trigger webhook if provided
        if webhook_url:
            requests.post(webhook_url, json={"request_id": request_id, "output_csv": request_record.output_csv})
    except Exception as e:
        request_record.status = "Failed"
        db.commit()
        raise e
    finally:
        db.close()

# Upload API
@app.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile, background_tasks: BackgroundTasks, webhook_url: str = None, db: SessionLocal = Depends(get_db)): # type: ignore
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")
    
    request_id = str(uuid.uuid4())
    request_record = ImageProcessingRequest(request_id=request_id, webhook_url=webhook_url)
    db.add(request_record)
    db.commit()
    
    csv_content = await file.read()
    csv_lines = csv_content.decode('utf-8').splitlines()
    
    # Validate CSV here (for simplicity, assuming the first line is header and ignoring it)
    csv_data = csv_lines[1:]

    if not csv_data:
        raise HTTPException(status_code=400, detail="Empty CSV file.")
    
    # Trigger background processing
    background_tasks.add_task(process_images, request_id, csv_data, webhook_url)
    
    return {"request_id": request_id}

# Status API
@app.get("/status/{request_id}")
def check_status(request_id: str, db: SessionLocal = Depends(get_db)): # type: ignore
    request_record = db.query(ImageProcessingRequest).filter_by(request_id=request_id).first()

    if not request_record:
        raise HTTPException(status_code=404, detail="Request ID not found.")
    
    return {
        "request_id": request_id,
        "status": request_record.status,
        "output_csv": request_record.output_csv
    }
