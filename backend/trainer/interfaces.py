from abc import ABC, abstractmethod

class IMeeting(ABC):
    @abstractmethod
    def createMeeting(user, data ,lsDetails_id ) :
        pass


class INotification(ABC):
    
    def send_notification(self,data,user):
        self.send_notification(data=data,user=user)
    
    @abstractmethod
    def send_email_notification(data,user):
        pass
    
class Notification(ABC):
    @abstractmethod
    def send_notification(self, recipient):
        pass

    def prepare_notification(self, recipient):
        # Common code for preparing the notification
        # You can add additional logic here
        message = self.get_message()
        recipient.notify(message)

    @abstractmethod
    def get_message(self):
        pass