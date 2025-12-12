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


class Mode(Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"


class Status(Enum):
    PAID = "Paid"
    PENDING = "Pending"
