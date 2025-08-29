# app/models/document.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, JSON, ForeignKey, Table, UniqueConstraint,
    Index # Добавим для индексов
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

# Вспомогательная таблица для связи многие-ко- many между документами и сущностями
# document_entities = Table('document_entities', Base.metadata,
#     Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
#     Column('entity_id', Integer, ForeignKey('entities.id'), primary_key=True)
# )

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String) # Путь к файлу в файловой системе
    content = Column(Text) # Извлеченный текст
    file_type = Column(String, index=True) # Новый столбец: тип файла (расширение)
    # extracted_entities = Column(JSON) # Можно использовать, если не хотим отдельную таблицу

    upload_time = Column(DateTime(timezone=True), server_default=func.now())

    # Отношение один-ко-многим с фрагментами
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    # Отношение многие-ко-многим с сущностями
    # entities = relationship("Entity", secondary=document_entities, back_populates="documents")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    # Ссылка на документ
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, index=True)
    # Содержимое фрагмента
    content = Column(Text, nullable=False)
    # Порядковый номер фрагмента в документе
    chunk_index = Column(Integer, nullable=False)
    # Позиция начала фрагмента в исходном тексте документа (опционально)
    start_position = Column(Integer)
    # Позиция конца фрагмента в исходном тексте документа (опционально)
    end_position = Column(Integer)

    # Отношение обратно к документу
    document = relationship("Document", back_populates="chunks")

    # Индекс для быстрого поиска фрагментов по документу
    __table_args__ = (Index('idx_doc_chunk_index', 'document_id', 'chunk_index'),)


# class Entity(Base):
#     __tablename__ = "entities"

#     id = Column(Integer, primary_key=True, index=True)
#     # Тип сущности, например, "PERSON", "ORG", "DATE"
#     entity_type = Column(String, index=True)
#     # Значение сущности, например, "Иванов И.И.", "ООО Ромашка", "2023-10-27"
#     value = Column(String, index=True)

#     # Отношение многие-ко-многим с документами
#     documents = relationship("Document", secondary=document_entities, back_populates="entities")

#     # UniqueConstraint теперь определен
#     __table_args__ = (UniqueConstraint('entity_type', 'value', name='uq_entity_type_value'),)
