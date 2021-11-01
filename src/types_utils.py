import uuid
from typing import TypedDict
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from face.liveness import HandSign

class ChallengeResponse(TypedDict):
    id: Union[str, uuid.UUID]
    sign: HandSign

class FaceAuthModel(BaseModel):
    cedula: str = Field(
        ..., 
        title="Document ID number", 
        max_length=11,
        min_length=11,
        regex='^([0-9]+)$'
    )
    source: str = Field(...,  title="Source to verify")
    id: Union[str, uuid.UUID]