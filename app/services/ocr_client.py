import base64
from io import BytesIO
import cv2
import requests
from PIL import Image


class OCRClient:

    def __init__(
        self,
        base_url: str,
        timeout: int = 120,
    ):

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()

    def close(self):

        self.session.close()

    def _image_to_base64(
        self,
        image,
    ) -> str:

        success, buffer = cv2.imencode(".png", image)

        if not success:
            raise ValueError("Failed to encode image.")

        return base64.b64encode(buffer.tobytes()).decode("utf-8")

    def _post(
        self,
        endpoint: str,
        image: Image.Image,
    ) -> dict:

        payload = {
            "image": self._image_to_base64(image),
        }

        response = self.session.post(
            url=f"{self.base_url}/{endpoint}",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def extract_drawing(
        self,
        image: Image.Image,
    ) -> tuple[int | None, int | None]:

        result = self._post(
            endpoint="drawing",
            image=image,
        )

        return (
            result.get("width"),
            result.get("height"),
        )

    def extract_name(
        self,
        image: Image.Image,
    ) -> str | None:

        result = self._post(
            endpoint="name",
            image=image,
        )

        return result.get("name")

    def extract_amount(
        self,
        image: Image.Image,
    ) -> str | None:

        result = self._post(
            endpoint="amount",
            image=image,
        )

        return result.get("amount")