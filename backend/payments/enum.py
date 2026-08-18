from enum import Enum
from rest_framework import status

class PayoutStatus(Enum):
    IS_APPROVED = 'is_approved'
    REFUSED = 'refused'

    @classmethod
    def has_value(cls, value):
        return value in [status.value for status in cls]