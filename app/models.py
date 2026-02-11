from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB


class Base(DeclarativeBase):
    pass


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    text_hash: Mapped[str] = mapped_column(Text, nullable=False)

    requires_clearance: Mapped[bool] = mapped_column(Boolean, nullable=False)
    requires_citizenship: Mapped[bool] = mapped_column(Boolean, nullable=False)

    hits: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    evidence: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    text_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
