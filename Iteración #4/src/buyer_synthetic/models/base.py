"""Base models for Buyer Synthetic platform."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel, Field
from uuid import UUID, uuid4


class BaseModel(PydanticBaseModel):
    """Base model with common fields."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        """Pydantic model configuration."""
        
        # Allow serialization of datetime objects
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
        
        # Use enum values for serialization
        use_enum_values = True
        
        # Validate assignments
        validate_assignment = True
        
        # Generate schema with examples
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:30:00"
            }
        }
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()
    
    def dict_exclude_none(self) -> dict:
        """Return dictionary excluding None values."""
        return self.dict(exclude_none=True)
    
    def json_exclude_none(self) -> str:
        """Return JSON string excluding None values."""
        return self.json(exclude_none=True)