from enum import Enum


class Role(Enum):
    ADMIN = "Admin"
    INSTRUCTOR = "Instructor"
    CASHIER = "Cashier"
    STUDENT = "Student"


class Level(Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class ConfigKey(Enum):
    MAX_STUDENTS = "max_students"
    FEE_BEGINNER = "fee_Beginner"
    FEE_INTERMEDIATE = "fee_Intermediate"
    FEE_ADVANCED = "fee_Advanced"

class Mode(Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"


class Status(Enum):
    PAID = "Paid"
    PENDING = "Pending"
