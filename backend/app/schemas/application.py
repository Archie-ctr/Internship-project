"""Validation contracts for the business-registration service form."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OwnerDetails(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    id_number: str = Field(min_length=6, max_length=50, pattern=r"^[A-Za-z0-9-]+$")
    phone_number: str = Field(min_length=7, max_length=30, pattern=r"^[+0-9 ()-]+$")


class BusinessAddress(BaseModel):
    line1: str = Field(min_length=3, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    district: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=100, default="Rwanda")


class CreateBusinessRegistrationRequest(BaseModel):
    """The server's authoritative validation; browser validation is convenience only."""

    business_name: str = Field(min_length=2, max_length=150)
    business_type: str = Field(
        pattern=r"^(sole_proprietorship|partnership|limited_company)$"
    )
    owner: OwnerDetails
    address: BusinessAddress


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_code: str
    service_name: str
    status: str
    business_name: str
    created_at: datetime


class ApplicationDetailResponse(ApplicationResponse):
    form_data: dict
    rejection_reason: str | None
