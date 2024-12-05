from typing import Optional
from uuid import UUID
from datetime import date, datetime
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    FilePath,
    ConfigDict,
    SecretStr,
    StringConstraints,
    constr,
)


config = ConfigDict(from_attributes=True)


class DocumentBase(BaseModel):
    organization: Optional[str] = Field(
        None,
        title="Organization",
        description="Name of the organization the document belongs to.",
        max_length=255,
        examples=["My Organization"],
    )
    full_name: Optional[str] = Field(
        None,
        title="Full Name",
        description="Full name of the individual the document refers to.",
        max_length=255,
        examples=["John Doe"],
    )
    pini: Optional[str] = Field(
        None,
        title="PINI",
        description="Personal Identification Number (PINI) of the individual.",
        max_length=14,
        examples=["12345678901234"],
    )
    passport_series: Optional[str] = Field(
        None,
        title="Passport Series",
        description="Passport series of the individual.",
        max_length=9,
        examples=["AA123456"],
    )
    birth_date: date = Field(
        datetime.now(),
        title="Birth Date",
        description="Date of birth of the individual.",
        examples=["1990-01-01"],
    )
    registration_address: Optional[str] = Field(
        None,
        title="Registration Address",
        description="Registered address of the individual.",
        max_length=255,
        examples=["123 Main Street, City, Country"],
    )
    work_address: Optional[str] = Field(
        None,
        title="Work Address",
        description="Workplace address of the individual.",
        max_length=255,
        examples=["456 Work Blvd, City, Country"],
    )
    examination_date: Optional[date] = Field(
        None,
        title="Examination Date",
        description="Date when the individual underwent an examination.",
        examples=["2024-12-01"],
    )

    a_type: Optional[bool] = Field(
        None,
        title="Health Type A",
        description="Health type of the individual for category A.",
        examples=[True],
    )
    b_type: Optional[bool] = Field(
        None,
        title="Health Type B",
        description="Health type of the individual for category B.",
        examples=[None],
    )
    c_type: Optional[bool] = Field(
        None,
        title="Health Type C",
        description="Health type of the individual for category C.",
        examples=[True, False],
    )
    d_type: Optional[bool] = Field(
        None,
        title="Health Type D",
        description="Health type of the individual for category D.",
        examples=[True, False],
    )
    e_type: Optional[bool] = Field(
        None,
        title="Health Type E",
        description="Health type of the individual for category E.",
        examples=[True, False],
    )
    tram_type: Optional[bool] = Field(
        None,
        title="Health Type Tram",
        description="Health type of the individual for tram category.",
        examples=[True, False],
    )
    trolleybus_type: Optional[bool] = Field(
        None,
        title="Health Type Trolleybus",
        description="Health type of the individual for trolleybus category.",
        examples=[True, False],
    )
    hired_type: Optional[bool] = Field(
        None,
        title="Health Type Hired",
        description="Health type of the individual for hired category.",
        examples=[True, False],
    )

    commission_director: Optional[str] = Field(
        None,
        title="Commission Director",
        description="Name of the director of the commission that issued the document.",
        max_length=255,
        examples=["Director Name"],
    )
    finish: Optional[bool] = Field(
        False,
        title="Finish Status",
        description="Indicates whether the process is finished or not.",
        examples=[True, False],
    )


class DocumentCreate(BaseModel):
    organization: Optional[str] = Field(
        None,
        title="Organization",
        description="Name of the organization the document belongs to.",
        max_length=255,
        examples=["My Organization"],
    )
    full_name: Optional[str] = Field(
        None,
        title="Full Name",
        description="Full name of the individual the document refers to.",
        max_length=255,
        examples=["John Doe"],
    )
    pini: Optional[str] = Field(
        None,
        title="PINI",
        description="Personal Identification Number (PINI) of the individual.",
        max_length=14,
        examples=["12345678901234"],
    )
    passport_series: Optional[str] = Field(
        None,
        title="Passport Series",
        description="Passport series of the individual.",
        max_length=9,
        examples=["AA123456"],
    )
    birth_date: date = Field(
        datetime.now(),
        title="Birth Date",
        description="Date of birth of the individual.",
        examples=["1990-01-01"],
    )
    registration_address: Optional[str] = Field(
        None,
        title="Registration Address",
        description="Registered address of the individual.",
        max_length=255,
        examples=["123 Main Street, City, Country"],
    )

    commission_director: Optional[str] = Field(
        None,
        title="Commission Director",
        description="Name of the director of the commission that issued the document.",
        max_length=255,
        examples=["Director Name"],
    )


class DocumentUpdate(BaseModel):
    full_name: Optional[str] = Field(
        None,
        title="Full Name",
        description="Full name of the individual the document refers to.",
        max_length=255,
        examples=["John Doe"],
    )
    pini: Optional[str] = Field(
        None,
        title="PINI",
        description="Personal Identification Number (PINI) of the individual.",
        max_length=14,
        examples=["12345678901234"],
    )
    passport_series: Optional[str] = Field(
        None,
        title="Passport Series",
        description="Passport series of the individual.",
        max_length=9,
        examples=["AA123456"],
    )
    birth_date: date = Field(
        datetime.now(),
        title="Birth Date",
        description="Date of birth of the individual.",
        examples=["1990-01-01"],
    )
    registration_address: Optional[str] = Field(
        None,
        title="Registration Address",
        description="Registered address of the individual.",
        max_length=255,
        examples=["123 Main Street, City, Country"],
    )
    work_address: Optional[str] = Field(
        None,
        title="Work Address",
        description="Workplace address of the individual.",
        max_length=255,
        examples=["456 Work Blvd, City, Country"],
    )

    a_type: Optional[bool] = Field(
        None,
        title="Health Type A",
        description="Health type of the individual for category A.",
        examples=[None],
    )
    b_type: Optional[bool] = Field(
        None,
        title="Health Type B",
        description="Health type of the individual for category B.",
        examples=[None],
    )
    c_type: Optional[bool] = Field(
        None,
        title="Health Type C",
        description="Health type of the individual for category C.",
        examples=[None],
    )
    d_type: Optional[bool] = Field(
        None,
        title="Health Type D",
        description="Health type of the individual for category D.",
        examples=[None],
    )
    e_type: Optional[bool] = Field(
        None,
        title="Health Type E",
        description="Health type of the individual for category E.",
        examples=[None],
    )
    tram_type: Optional[bool] = Field(
        None,
        title="Health Type Tram",
        description="Health type of the individual for tram category.",
        examples=[None],
    )
    trolleybus_type: Optional[bool] = Field(
        None,
        title="Health Type Trolleybus",
        description="Health type of the individual for trolleybus category.",
        examples=[None],
    )
    hired_type: Optional[bool] = Field(
        None,
        title="Health Type Hired",
        description="Health type of the individual for hired category.",
        examples=[None],
    )
    special_note: Optional[str] = Field(
        None,
        title="Special note",
        description="Special note",
        max_length=255,
        examples=["Kozoynak bilan mukun"],
    )
    commission_director: Optional[str] = Field(
        None,
        title="Commission Director",
        description="Name of the director of the commission that issued the document.",
        max_length=255,
        examples=["Director Name"],
    )
    finish: Optional[bool] = Field(
        None,
        title="Finish Status",
        description="Indicates whether the process is finished or not.",
        examples=[True, False],
    )
