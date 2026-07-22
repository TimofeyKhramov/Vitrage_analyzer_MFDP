from sqlmodel import Session

from app.models.analysis_result import AnalysisResult
from app.models.document import Document
from app.models.drawing import Drawing


class ResultService:

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def save_document_results(
        self,
        document: Document,
        results: list[dict],
    ) -> None:

        for page_result in results:

            page_number = page_result["page"]

            for drawing_index, drawing_data in enumerate(
                page_result["drawings"],
                start=1,
            ):

                drawing = Drawing(
                    document_id=document.id,
                    page_number=page_number,
                    drawing_number=drawing_index,
                )

                self.session.add(drawing)

                self.session.flush()

                analysis_result = AnalysisResult(
                    drawing_id=drawing.id,
                    name=drawing_data["name"],
                    quantity=drawing_data["amount"],
                    width=drawing_data["width"],
                    height=drawing_data["height"],
                    doors_count=drawing_data["doors_amount"],
                )

                self.session.add(
                    analysis_result,
                )

        self.session.commit()