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


class Status(Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
