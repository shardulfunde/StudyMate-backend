from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, validator


VALID_INTEREST = {"Yes", "Maybe", "No"}
VALID_SPENDING = {"Under ₹100", "₹100–₹200", "₹200–₹400", "₹400+"}
VALID_FREQUENCY = {"Daily", "2–3 times/week", "Once a week", "Rarely"}
VALID_CATEGORIES = {
    "Food (meals, snacks)",
    "Beverages (coffee, juice, etc.)",
    "Desserts",
    "Stationery",
    "Other services",
}
VALID_DECISION = {"Price/discount", "Quality/taste", "Convenience (distance or delivery)", "Popularity/brand"}
VALID_OFFER = {"5–10% discount", "10–20% discount", "Flat ₹50–₹100 off", "Combo deals"}
VALID_ORDERING = {"Delivery", "Takeaway", "Dine-in", "No preference"}
VALID_DELIVERY_FLEX = {"Yes", "Maybe", "No"}
VALID_USAGE = {"Almost every time", "Sometimes", "Rarely"}


class StudentDealsSurveyRequest(BaseModel):
    interest: str
    spending: str
    frequency: str
    category_preference: List[str]
    decision_driver: str
    offer_preference: str
    ordering_preference: str
    delivery_flexibility: str
    usage_intent: str
    open_feedback: Optional[str] = None

    @validator("interest")
    def validate_interest(cls, v):
        if v not in VALID_INTEREST:
            raise ValueError("Invalid interest value")
        return v

    @validator("spending")
    def validate_spending(cls, v):
        if v not in VALID_SPENDING:
            raise ValueError("Invalid spending value")
        return v

    @validator("frequency")
    def validate_frequency(cls, v):
        if v not in VALID_FREQUENCY:
            raise ValueError("Invalid frequency value")
        return v

    @validator("category_preference")
    def validate_category_preference(cls, v):
        if not v:
            raise ValueError("Select at least one category")
        for item in v:
            if item not in VALID_CATEGORIES:
                raise ValueError(f"Invalid category: {item}")
        return v

    @validator("decision_driver")
    def validate_decision_driver(cls, v):
        if v not in VALID_DECISION:
            raise ValueError("Invalid decision driver value")
        return v

    @validator("offer_preference")
    def validate_offer(cls, v):
        if v not in VALID_OFFER:
            raise ValueError("Invalid offer preference value")
        return v

    @validator("ordering_preference")
    def validate_ordering(cls, v):
        if v not in VALID_ORDERING:
            raise ValueError("Invalid ordering preference value")
        return v

    @validator("delivery_flexibility")
    def validate_delivery(cls, v):
        if v not in VALID_DELIVERY_FLEX:
            raise ValueError("Invalid delivery flexibility value")
        return v

    @validator("usage_intent")
    def validate_usage(cls, v):
        if v not in VALID_USAGE:
            raise ValueError("Invalid usage intent value")
        return v

    @validator("open_feedback")
    def validate_feedback(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError("Feedback must be under 1000 characters")
            return v or None
        return v


class StudentDealsSurveyResponseSchema(BaseModel):
    id: UUID
    message: str


class StudentDealsSurveyStatusResponseSchema(BaseModel):
    submitted: bool
