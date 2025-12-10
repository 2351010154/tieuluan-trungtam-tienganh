from enum import Enum


class Role(Enum):
    ADMIN = "Admin"
    INSTRUCTOR = "Instructor"
    CASHIER = "Cashier"
    STUDENT = "Student"


class Level(Enum):
    BEGINNER = "Dễ"
    INTERMEDIATE = "Trung Cấp"
    ADVANCED = "Nâng Cao"


class Mode(Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"


class Status(Enum):
    PAID = "Paid"
    PENDING = "Pending"
