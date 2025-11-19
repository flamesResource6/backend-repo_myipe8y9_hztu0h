"""
Database Schemas for Auto Detailer Website

Each Pydantic model maps to a MongoDB collection with the lowercase class name.
Examples:
- Service -> "service"
- Booking -> "booking"
- Testimonial -> "testimonial"
- ContactMessage -> "contactmessage"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class Service(BaseModel):
    title: str = Field(..., description="Service name, e.g., 'Full Detail'")
    description: str = Field(..., description="Short description of the service")
    duration_minutes: int = Field(..., ge=15, le=600, description="Estimated duration in minutes")
    price: float = Field(..., ge=0, description="Base price in USD")
    category: str = Field("Exterior", description="Category: Exterior, Interior, Packages, Add-ons")

class Booking(BaseModel):
    name: str = Field(..., description="Customer full name")
    email: EmailStr = Field(..., description="Customer email")
    phone: str = Field(..., description="Customer phone number")
    vehicle_make: str = Field(..., description="Vehicle make")
    vehicle_model: str = Field(..., description="Vehicle model")
    vehicle_year: Optional[int] = Field(None, ge=1900, le=2100)
    service_id: Optional[str] = Field(None, description="Selected service id")
    preferred_date: Optional[str] = Field(None, description="Preferred appointment date (ISO string)")
    notes: Optional[str] = Field(None, description="Additional notes from customer")
    status: str = Field("pending", description="Booking status: pending, confirmed, completed, cancelled")

class Testimonial(BaseModel):
    name: str = Field(..., description="Customer name")
    rating: int = Field(..., ge=1, le=5, description="Star rating out of 5")
    comment: str = Field(..., description="Customer review text")

class ContactMessage(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    message: str = Field(..., min_length=5)

# Optional helper models for responses
class BookingResponse(BaseModel):
    id: str
    message: str
    created_at: Optional[datetime] = None
