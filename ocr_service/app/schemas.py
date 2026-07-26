from pydantic import BaseModel


class OcrRequest(BaseModel):

    image: str