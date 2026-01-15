

from pydantic import BaseModel

class SaveFileData(BaseModel):
    path: str
    content: str
