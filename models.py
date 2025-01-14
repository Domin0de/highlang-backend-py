from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, ForeignKey, Integer, String

class Base(DeclarativeBase):
    """Base class for the models"""
    pass

class OriginalItem(Base):
    """Model for the original text"""
    __tablename__ = "originals"

    id = Column(Integer, primary_key=True)
    text = Column(String(255))

class TranslationItem(Base):
    """Model for the translated text"""
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True)
    lang = Column(String(20))
    html_text = Column(String(1000))
    original_id = Column(Integer, ForeignKey(OriginalItem.id))
    audio_path = Column(String(200))
