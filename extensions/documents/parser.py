from .pdf import PDFParser

class DocumentParser:
    """
    # Document Parser
    """
    def __init__(self, pdf_structure_model, device) -> None:
        self.pdf = PDFParser(model_dir=pdf_structure_model, device=device)