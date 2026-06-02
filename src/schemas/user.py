from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class EmailVerifySendRequest(BaseModel):
    email: EmailStr


class EmailVerifyConfirmRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class PrivacyConsentCreate(BaseModel):
    required_agreed: bool
    optional_agreed: bool = False


class UserCreate(BaseModel):
    student_id: str = Field(..., min_length=5, max_length=20)
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    verification_code: str = Field(
        ..., min_length=6, max_length=6, pattern=r"^\d{6}$"
    )
    privacy_consent: PrivacyConsentCreate

    # ★ 전화번호 형식 검증 추가 (기존: 형식 검증 없음)
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # 숫자·하이픈만 허용 (예: 010-1234-5678 또는 01012345678)
        cleaned = re.sub(r"[-\s]", "", v)
        if not cleaned.isdigit():
            raise ValueError("전화번호는 숫자와 하이픈(-)만 입력 가능합니다.")
        if len(cleaned) < 10 or len(cleaned) > 11:
            raise ValueError("올바른 전화번호 형식이 아닙니다.")
        return v

    # ★ 학번 형식 검증 추가 (기존: 길이만 검증)
    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("학번은 숫자만 입력 가능합니다.")
        return v


class LoginRequest(BaseModel):
    student_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    student_id: str
    name: str
    email: str
    phone: Optional[str]
    department: Optional[str]
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
