import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Service, Booking, Testimonial, ContactMessage, BookingResponse

app = FastAPI(title="Auto Detailer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Auto Detailer Backend Ready"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# Schemas endpoint for Flames viewer
@app.get("/schema")
def get_schema():
    return {
        "service": Service.model_json_schema(),
        "booking": Booking.model_json_schema(),
        "testimonial": Testimonial.model_json_schema(),
        "contactmessage": ContactMessage.model_json_schema(),
    }

# Public endpoints
@app.get("/services", response_model=List[Service])
def list_services():
    if db is None:
        return []
    docs = get_documents("service")
    # Convert Mongo docs to Pydantic by filtering keys
    results = []
    for d in docs:
        d.pop("_id", None)
        results.append(Service(**d))
    return results

class BookingCreate(BaseModel):
    name: str
    email: str
    phone: str
    vehicle_make: str
    vehicle_model: str
    vehicle_year: Optional[int] = None
    service_id: Optional[str] = None
    preferred_date: Optional[str] = None
    notes: Optional[str] = None

@app.post("/book", response_model=BookingResponse)
def create_booking(payload: BookingCreate):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    booking = Booking(**payload.model_dump())
    booking_id = create_document("booking", booking)
    return BookingResponse(id=booking_id, message="Booking received. We'll confirm shortly.")

@app.post("/contact")
def submit_contact(message: ContactMessage):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    _id = create_document("contactmessage", message)
    return {"id": _id, "message": "Thanks for reaching out! We'll get back soon."}

# Seed sample services if none exist
@app.post("/seed")
def seed_services():
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    existing = get_documents("service", {}, limit=1)
    if existing:
        return {"message": "Services already seeded"}
    samples = [
        Service(title="Exterior Wash", description="Hand wash, dry, wheels & tires", duration_minutes=45, price=39.0, category="Exterior"),
        Service(title="Interior Detail", description="Vacuum, steam clean, interior surfaces", duration_minutes=90, price=129.0, category="Interior"),
        Service(title="Full Detail", description="Complete inside & out detailing", duration_minutes=180, price=259.0, category="Packages"),
        Service(title="Ceramic Coating", description="2-year protection, deep gloss", duration_minutes=240, price=699.0, category="Add-ons"),
    ]
    for s in samples:
        create_document("service", s)
    return {"message": "Seeded sample services"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
