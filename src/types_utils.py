import sys
import uuid
from typing import Union
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from pydantic import BaseModel
from pydantic import Field

from face.liveness import HandSign

class ChallengeResponse(BaseModel):
    id: Union[str, uuid.UUID]
    sign: HandSign

class ChallengeCache(BaseModel):
    sign: HandSign
    sid: Optional[str]
    trial: int

class VerifyResponse(BaseModel):
    verified: bool
    face_verified: bool
    is_alive: bool

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

class SocketErrorResult(BaseModel):
    error: str