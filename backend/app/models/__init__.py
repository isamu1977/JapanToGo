"""ORM model package.

Importing this module registers every model on ``Base.metadata`` which is
required by Alembic autogenerate and by the ``create_all`` helper.
"""

from app.models.base import (
    Base,
    LegalTermType,
    PreOrderStatus,
    PreOrderType,
    ShipmentStatus,
    ShippingMethod,
    SuiteItemStatus,
    TimestampMixin,
    UserRole,
)
from app.models.pre_order import PreOrder, PreOrderItem
from app.models.shipment import Shipment
from app.models.suite_item import InspectionPhoto, SuiteItem
from app.models.user import (
    SUITE_CODE_PREFIX,
    LegalTermsAcceptance,
    User,
    suite_code_sequence,
)

__all__ = [
    "SUITE_CODE_PREFIX",
    "Base",
    "InspectionPhoto",
    "LegalTermType",
    "LegalTermsAcceptance",
    "PreOrder",
    "PreOrderItem",
    "PreOrderStatus",
    "PreOrderType",
    "Shipment",
    "ShipmentStatus",
    "ShippingMethod",
    "SuiteItem",
    "SuiteItemStatus",
    "TimestampMixin",
    "User",
    "UserRole",
    "suite_code_sequence",
]
