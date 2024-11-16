import pdfkit
from typing import Any
from tempfile import NamedTemporaryFile

async def create_pdf(template) -> str | Any:
    options = {
        'page-height': '21.5cm',
        'page-width': '25cm',
        'margin-left': '7mm',
        'margin-right': '7mm',
        'margin-bottom': '5mm',
        'margin-top': '5mm'
    }
    try:
        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            pdfkit.from_string(template, temp_pdf.name,  options=options)
            pdf_file_path = temp_pdf.name

        return pdf_file_path
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()

    return None
