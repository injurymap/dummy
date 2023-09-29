from typing import List, Optional
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from humps import camelize


class CamelModel(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
        orm_mode = True
        anystr_strip_whitespace = True


class PydanticError(BaseModel):
    loc: List[str]
    msg: str
    type: str
    codes: Optional[str]
    didYouMean: Optional[str]

    def errors(self):
        return [self.dict(by_alias=True)]


class BookAppointment(CamelModel):
    id: str
    ref_id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    cell_phone_number: Optional[str]
    email: Optional[str]

class Booking(CamelModel):
    id: str
    pg_id: Optional[str]
    booking_time: Optional[str]