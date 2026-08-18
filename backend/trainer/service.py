from __future__ import annotations
from .interfaces import IMeeting
class MeetingServices:
    def __init__(self, strategy: IMeeting):
        self._strategy = strategy
    
    @property
    def strategy(self)-> IMeeting:
        return self._strategy
    
    @strategy.setter
    def strategy(self , strategy:IMeeting) -> None:
        self._strategy=strategy
        
    
    def addMeeting(self,user,data,lsDetails_id):
        self._strategy.createMeeting.delay(user,data,lsDetails_id)
    
    