from enum import Enum
from decimal import Decimal
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, constr


class FeeType(str, Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    TIERED = "tiered"
    RANGE = "range"


class Fee(BaseModel):
    fee_id: constr(strip_whitespace=True) = Field(..., description="Unique identifier for this fee record")
    bank: str = Field(..., description="Name of the bank, e.g. 'Eurobank', 'Alpha Bank'")
    product_or_service: str = Field(
        ..., description="High-level product or service (e.g. 'Debit Card', 'SEPA Transfer')"
    )
    category: str = Field(
        ..., description="Broad category (e.g. 'Card Services', 'Payments', 'Cash Services')"
    )
    subcategory: Optional[str] = Field(
        None, description="More specific subcategory (e.g. 'Instant Transfer' under 'Payments')"
    )
    fee_name_raw: str = Field(
        ..., description="The exact fee name as printed in the PDF"
    )
    fee_type: FeeType = Field(
        ..., description="Type of fee: fixed, percentage, tiered, or range"
    )

    amount_fixed: Optional[Decimal] = Field(
        None, description="Flat fee amount if fee_type is fixed"
    )
    amount_percent: Optional[Decimal] = Field(
        None, description="Percentage rate if fee_type is percentage"
    )
    min_amount: Optional[Decimal] = Field(
        None, description="Minimum fee amount for tiered or range fees"
    )
    max_amount: Optional[Decimal] = Field(
        None, description="Maximum fee amount for tiered or range fees"
    )
    currency: constr(min_length=3, max_length=3) = Field(
        'EUR', description="Currency code (ISO 4217), typically 'EUR'"
    )

    calculation_basis: Optional[str] = Field(
        None, description="Basis for calculation (e.g. 'per transaction')"
    )
    channel: Optional[str] = Field(
        None, description="Execution channel (e.g. 'Branch', 'ATM', 'e-Banking')"
    )
    applicable_to: Optional[str] = Field(
        None, description="Customer segment (e.g. 'Individuals', 'Businesses')"
    )
    conditions: Optional[str] = Field(
        None, description="Special conditions or thresholds if any"
    )
    frequency: Optional[str] = Field(
        None, description="Recurrence frequency (e.g. 'annual', 'one-off')"
    )
    effective_date: Optional[date] = Field(
        None, description="Date the fee came into effect"
    )

    source_document: str = Field(
        ..., description="Filename of the source PDF"
    )
    source_page: Optional[int] = Field(
        None, description="Page number in the PDF where the fee was found"
    )
    source_section: Optional[str] = Field(
        None, description="Section or heading in the PDF"
    )
    notes: Optional[str] = Field(
        None, description="Additional remarks or caveats"
    )

    class Config:
        str_strip_whitespace = True
        json_schema_extra = {
            "example": {
                "fee_id": "f12345",
                "bank": "Eurobank",
                "product_or_service": "Credit Cards",
                "category": "Card Services",
                "subcategory": "Annual Subscription",
                "fee_name_raw": "Ετήσια Συνδρομή Πιστωτικών Καρτών",
                "fee_type": "fixed",
                "amount_fixed": "30.00",
                "currency": "EUR",
                "calculation_basis": "per card, per year",
                "channel": "Branch",
                "applicable_to": "Individuals",
                "frequency": "annual",
                "effective_date": "2025-06-11",
                "source_document": "timologio-personal-banking.pdf",
                "source_page": 6,
                "source_section": "1.1. VISA",
                "notes": "Free if < 12 months in My Blue package"
            }
        }

fee1 = Fee(
    fee_id="f10001",
    bank="Alpha Bank",
    product_or_service="Credit Card",
    category="Card Services",
    subcategory="Annual Fee",
    fee_name_raw="Ετήσια Συνδρομή Πιστωτικής Κάρτας",
    fee_type=FeeType.FIXED,
    amount_fixed=Decimal("25.00"),
    currency="EUR",
    calculation_basis="per card, per year",
    channel="Branch",
    applicable_to="Individuals",
    frequency="annual",
    effective_date=date(2025, 1, 1),
    source_document="deltio-telon-alpha-misthodosia.pdf",
    source_page=4,
    source_section="3.2",
    notes=None
)

fee2 = Fee(
    fee_id="f10002",
    bank="Eurobank",
    product_or_service="SEPA Transfer",
    category="Payments",
    subcategory=None,
    fee_name_raw="Τέλος εκτέλεσης SEPA",
    fee_type=FeeType.FIXED,
    amount_fixed=Decimal("0.20"),
    currency="EUR",
    calculation_basis="per transaction",
    channel="e-Banking",
    applicable_to="Individuals",
    frequency="per transaction",
    effective_date=date(2025, 2, 15),
    source_document="timologio-personal-banking.pdf",
    source_page=12,
    source_section="5.1",
    notes="Δωρεάν για ποσά έως €50"
)

print(fee1)