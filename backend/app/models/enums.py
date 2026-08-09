from enum import Enum

class StockoutRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ImpactLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RuleAction(str, Enum):
    CREATE_EXCEPTION_CASE = "CREATE_EXCEPTION_CASE"
    EVALUATE_ALTERNATIVE_SUPPLIER = "EVALUATE_ALTERNATIVE_SUPPLIER"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    AUTO_CREATE_PO = "AUTO_CREATE_PO"
    NO_ACTION = "NO_ACTION"

class ExceptionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class POStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    EXPEDITED = "EXPEDITED"
    DELAYED = "DELAYED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    AUTO_EXECUTED = "AUTO_EXECUTED"

class FreightMode(str, Enum):
    AIR = "AIR"
    OCEAN = "OCEAN"
    GROUND = "GROUND"
    RAIL = "RAIL"
