from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.content import ContactMessageState


class ContactModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ContactSubmissionRequest(ContactModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=64)
    company: str | None = Field(default=None, max_length=160)
    project_type: Literal["architecture", "interior", "reuse"] | None = None
    message: str = Field(min_length=20, max_length=12_000)
    source_locale: Literal["en", "fa"]
    started_at: int = Field(ge=0)
    website: str = Field(default="", max_length=200)

    @field_validator("name", "phone", "company", "message", "website", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("phone", "company", mode="after")
    @classmethod
    def optional_text_is_none_when_empty(cls, value: str | None) -> str | None:
        return value or None


class ContactSubmissionResponse(ContactModel):
    accepted: Literal[True] = True


class AdminContactMessageResponse(ContactModel):
    id: UUID
    name: str
    email: EmailStr
    phone: str | None
    company: str | None
    project_type: str | None
    body: str
    source_locale: Literal["en", "fa"]
    state: ContactMessageState
    read_at: datetime | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminContactMessageListResponse(ContactModel):
    items: list[AdminContactMessageResponse]
    total: int


class AdminContactMessageStateRequest(ContactModel):
    state: ContactMessageState
