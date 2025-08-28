import os
import shutil
from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate
from app.utils.file_processor import extract_text_from_file
from app.core.config import settings

def save_document(db: Session, file, filename: str):
    """Сохраняет файл, извлекает текст и сохраняет метаданные в БД."""
    # 1. Сохранить файл локально
    file_location = os.path.join(settings.UPLOAD_DIRECTORY, filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # 2. Извлечь текст
    extracted_text = extract_text_from_file(file_location)

    # 3. Сохранить метаданные в БД
    db_document = Document(
        filename=filename,
        file_path=file_location,
        content=extracted_text # Для MVP сохраняем в БД, в будущем - в Elasticsearch
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Document).offset(skip).limit(limit).all()