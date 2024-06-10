from datetime import date, datetime

from pydantic import BaseModel, Field
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import uuidhex
from app.models.base import Base


class POSTConsumableCategory(BaseModel):
    name: str
    description: str | None = None


class POSTConsumable(BaseModel):
    name: str
    quantity: int = Field(ge=0)
    description: str | None = None


class POSTConsumableHistory(BaseModel):
    modified_count: int
    description: str | None = None


class GETListParams(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int | None = Field(None, gt=0)


class ConsumableCategory(Base):
    __tablename__ = "consumable_categories"

    category_id: Mapped[str] = mapped_column(default=uuidhex, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None] = mapped_column()
    created_at: Mapped[date] = mapped_column(default=date.today)

    consumables: Mapped[list["Consumable"]] = relationship(
        "Consumable", back_populates="consumable_category"
    )

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


class Consumable(Base):
    __tablename__ = "consumables"

    consumable_id: Mapped[str] = mapped_column(default=uuidhex, primary_key=True)
    name: Mapped[str] = mapped_column()
    quantity: Mapped[int] = mapped_column(CheckConstraint("quantity >= 0"))

    description: Mapped[str | None] = mapped_column()
    created_at: Mapped[date] = mapped_column(default=date.today)

    category_id: Mapped[str] = mapped_column(
        ForeignKey("consumable_categories.category_id")
    )
    consumable_category: Mapped["ConsumableCategory"] = relationship(
        "ConsumableCategory", back_populates="consumables"
    )

    history: Mapped[list["ConsumableHistory"]] = relationship(
        "ConsumableHistory", back_populates="consumable"
    )

    def to_dict(self):
        return {
            "consumable_id": self.consumable_id,
            "name": self.name,
            "quantity": self.quantity,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "category_id": self.category_id,
        }


class ConsumableHistory(Base):
    __tablename__ = "consumable_history"

    history_id: Mapped[int] = mapped_column(primary_key=True)
    modified_count: Mapped[int] = mapped_column()
    modified_time: Mapped[datetime] = mapped_column(default=datetime.now)
    description: Mapped[str | None] = mapped_column()

    consumable_id: Mapped[str] = mapped_column(ForeignKey("consumables.consumable_id"))
    consumable: Mapped["Consumable"] = relationship(
        "Consumable", back_populates="history"
    )

    def to_dict(self):
        return {
            "history_id": self.history_id,
            "modified_count": self.modified_count,
            "description": self.description or "",
            "modified_time": self.modified_time.isoformat(),
            "consumable_id": self.consumable_id,
        }
