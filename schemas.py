from pydantic import BaseModel, Field, field_validator

class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=200)
    parties: str = Field(..., min_length=2, max_length=5000)
    terms: str = Field(..., min_length=2, max_length=15000)
    effective_date: str = Field(..., min_length=2, max_length=100)

    @field_validator("document_type", "parties", "terms", "effective_date")
    @classmethod
    def clean(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty")
        return value

class GenerateResponse(BaseModel):
    document_type: str
    content: str
    model: str

class ExportRequest(BaseModel):
    document_type: str = Field(default="Legal Document", max_length=200)
    content: str = Field(..., min_length=1, max_length=100000)
    terms: str = Field(default="", max_length=15000)
    logo_base64: str | None = None
