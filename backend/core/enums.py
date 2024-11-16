import random

from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def random_choice(cls):
        return random.choice(cls.list())


class Gender(ExtendedEnum):
    MALE = 1
    FEMALE = 2
    OTHERS = 3


class MailSendType(ExtendedEnum):
    VERIFICATION = 1
    PASSWORD_RESET = 2
    NEW_USER_SEND_PASSWORD = 3


class MenuType(ExtendedEnum):
    PARENT = 1
    CHILD = 2
    PERMISSION = 3


class PermissionType(ExtendedEnum):
    ALL_DATA = 1
    SELF_DATA = 2


class FileType(Enum):
    PROFILE_PICTURE = 1  # "profile_picture"

class Status(ExtendedEnum):
    INACTIVE = 1
    ACTIVE = 2
    DELETE = 3

class Tools(ExtendedEnum):
    GOOGLE_PAGE_SPEED = "google_page_speed"
    GOOGLE_ANALYTIC = "google_analytic"
    GT_MATRIX = "gt_matrix"
    KEYWORD_RANKING = "keyword_ranking"