# app/services/document_service.py
import os
import shutil
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.document import Document, DocumentChunk # Импортируем DocumentChunk
from app.schemas.document import DocumentCreate
from app.services import chunking_service # Импортируем chunking_service
from app.core.config import settings
from app.utils.file_processor import extract_text_from_file

def save_document(db: Session, file, filename: str):
    """Сохраняет файл, извлекает текст и сущности, разбивает на фрагменты, сохраняет метаданные в БД."""
    # 1. Определяем тип файла
    _, ext = os.path.splitext(filename)
    file_type = ext.lower().lstrip('.') # 'pdf', 'docx', 'txt' и т.д.

    # 2. Сохранить файл локально
    file_location = os.path.join(settings.UPLOAD_DIRECTORY, filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # 3. Извлекаем текст
    extracted_text = extract_text_from_file(file_location)

    # 4. Извлекаем сущности
    # extracted_entities_dict = extract_entities(extracted_text) # {'PERSON': [...], 'ORG': [...]}
    # print(f"Извлеченные сущности для {filename}: {extracted_entities_dict}")

    # 5. --- Добавлено: Разбиваем текст на фрагменты ---
    # Используем стратегию по умолчанию из chunking_service
    text_chunks = chunking_service.create_chunks(extracted_text)
    print(f"Документ {filename} разбит на {len(text_chunks)} фрагментов.")

    # 6. Начинаем транзакцию для сохранения документа, фрагментов и сущностей
    try:
        # 7. Сохраняем документ в БД
        db_document = Document(
            filename=filename,
            file_path=file_location,
            content=extracted_text, # Сохраняем полный текст для обратной совместимости (пока)
            file_type=file_type
        )
        db.add(db_document)
        db.flush() # Получаем ID документа до коммита

        # 8. --- Добавлено: Сохраняем фрагменты ---
        db_chunks = []
        for i, chunk_text in enumerate(text_chunks):
            start_pos = extracted_text.find(chunk_text) # Находим примерную позицию (может быть неточно при дубликатах)
            end_pos = start_pos + len(chunk_text) if start_pos != -1 else None
            
            db_chunk = DocumentChunk(
                document_id=db_document.id,
                content=chunk_text,
                chunk_index=i,
                start_position=start_pos,
                end_position=end_pos
            )
            db_chunks.append(db_chunk)
            db.add(db_chunk)
        # db.flush() # Можно сделать flush после добавления всех фрагментов

        # 9. Обрабатываем и сохраняем сущности
        # all_entities_for_doc = []
        # for ent_type, ent_values in extracted_entities_dict.items():
        #     for ent_value in ent_values:
        #         # Проверяем, существует ли сущность в БД
        #         existing_entity = db.query(Entity).filter(
        #             and_(Entity.entity_type == ent_type, Entity.value == ent_value)
        #         ).first()

        #         if existing_entity:
        #             entity_to_add = existing_entity
        #         else:
        #             entity_to_add = Entity(entity_type=ent_type, value=ent_value)
        #             db.add(entity_to_add)
        #             db.flush() # Получаем ID новой сущности

        #         all_entities_for_doc.append(entity_to_add)

        # 10. Связываем документ с извлеченными сущностями
        # db_document.entities = all_entities_for_doc

        # 11. Коммитим все изменения
        db.commit()
        db.refresh(db_document)
        print(f"Документ {filename} (ID: {db_document.id}), его фрагменты ({len(db_chunks)}) и сущности успешно сохранены.")
        return db_document

    except Exception as e:
        db.rollback()
        print(f"Ошибка при сохранении документа {filename} и связанных данных: {e}")
        raise # Передаем исключение дальше

def get_document(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Document).offset(skip).limit(limit).all()

# --- Добавлено: Функция для получения фрагментов документа ---
def get_document_chunks(db: Session, document_id: int, skip: int = 0, limit: int = 100):
    """Получает фрагменты документа."""
    return db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).offset(skip).limit(limit).all()

# --- Функции для фильтров остаются без изменений ---
# def get_unique_entities(db: Session, entity_type: str = None):
#     query = db.query(Entity.value).distinct(Entity.value)
#     if entity_type:
#         query = query.filter(Entity.entity_type == entity_type)
#     return [value for (value,) in query.all()]

# def get_unique_file_types(db: Session):
#     query = db.query(Document.file_type).distinct(Document.file_type)
#     query = query.filter(Document.file_type.isnot(None))
#     return [ftype for (ftype,) in query.all()]
