from ninja import Schema

class LocationOUT(Schema):
    Country:str
    City:str

class DataOUT(Schema):
    Location:LocationOUT
    Type:str

class MessageOUT(Schema):
    error_msg:str
    suggestion:str

class StateDataOUT(Schema):
    Location:str
    Type:str
    message:MessageOUT


class StateOUT(Schema):
    state_name:str
    data: StateDataOUT

class UserOut(Schema):
    user_prompt: str
    data:DataOUT
    id: int
    username: str


