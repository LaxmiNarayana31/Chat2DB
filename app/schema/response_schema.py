from pydantic.v1 import BaseModel
from typing import Union,Optional

class ResponseSchema(BaseModel):
    status: bool = True
    status_code: int
    response: str
    data: Union[Optional[dict], Optional[list], None] = None