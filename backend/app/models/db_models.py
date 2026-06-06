from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    birth_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    calendar: Mapped[str] = mapped_column(String(10), nullable=False)
    birth_place: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow, nullable=False
    )

    charts: Mapped[List["BaziChart"]] = relationship(
        back_populates="person", cascade="all, delete-orphan"
    )


class BaziChart(Base):
    __tablename__ = "bazi_charts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), nullable=False, index=True)

    year_gz: Mapped[str] = mapped_column(String(10), nullable=False)
    month_gz: Mapped[str] = mapped_column(String(10), nullable=False)
    day_gz: Mapped[str] = mapped_column(String(10), nullable=False)
    hour_gz: Mapped[str] = mapped_column(String(10), nullable=False)

    five_elements_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow, nullable=False
    )

    person: Mapped[Person] = relationship(back_populates="charts")
    analyses: Mapped[List["Analysis"]] = relationship(
        back_populates="chart", cascade="all, delete-orphan"
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chart_id: Mapped[int] = mapped_column(ForeignKey("bazi_charts.id"), nullable=False, index=True)

    overview: Mapped[str] = mapped_column(Text, nullable=False)
    career: Mapped[str] = mapped_column(Text, nullable=False)
    relationship_text: Mapped[str] = mapped_column(Text, nullable=False)
    health: Mapped[str] = mapped_column(Text, nullable=False)
    luck_cycles: Mapped[str] = mapped_column(Text, nullable=False)

    raw_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow, nullable=False
    )

    chart: Mapped[BaziChart] = relationship(back_populates="analyses")


class Compatibility(Base):
    __tablename__ = "compatibility"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chart_a_id: Mapped[int] = mapped_column(ForeignKey("bazi_charts.id"), nullable=False)
    chart_b_id: Mapped[int] = mapped_column(ForeignKey("bazi_charts.id"), nullable=False)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    raw_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow, nullable=False
    )

