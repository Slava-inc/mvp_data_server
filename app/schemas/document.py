from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    filename: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    content: Optional[str] = None # Не обязательно возвращать весь контент
    upload_time: datetime

    class Config:
        from_attributes = True # Для совместимости с ORM