from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from app.db.base import Base


class ResourceEmbedding(Base):
    __tablename__ = "resource_embeddings"

    import uuid

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    resource_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    college_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    subject_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    chunk_index = Column(Integer)
    page_number = Column(Integer)

    chunk_text = Column(Text, nullable=False)

    embedding = Column(Vector(1024), nullable=False)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
