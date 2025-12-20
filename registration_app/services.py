from abc import ABC, abstractmethod
from enum import Enum

class RegistrationResultType(Enum):
    SUCCESS = 'success'
    PAYMENT_REQUIRED = 'payment_required'
    FAILED = 'failed'
class RegistrationResult:
    def __init__(self, result_type, payment_url=None, response = None):
        self.result_type = result_type
        self.payment_url = payment_url
        self.response = response

class Registration(ABC):
    def __init__(self, activity):
        self.activity = activity
    @abstractmethod
    def register(self, user):
        pass

class FreeRegistration(Registration):
    def register(self, user):
        response = self.activity.add_person(user)
        if response['status'] != 201:
            return RegistrationResult(result_type=RegistrationResultType.FAILED, response=response)
        return RegistrationResult(result_type=RegistrationResultType.SUCCESS, response=response)
