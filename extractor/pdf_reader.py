from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer


class PDFReader():
    """
    Extract texts from PDF
    """
    def __init__(self, pdf_path):
        self.path = pdf_path

    def iterate_page_texts(self,
                           start_page=1,
                           end_page=None):
        """
        Generate texts in each page.
        """

        pages = extract_pages(self.path, laparams=LAParams())
        page_number = 0
        for p in pages:
            page_number += 1
            if start_page > 0 and page_number < start_page:
                continue
            elif end_page is not None and page_number > end_page:
                break
            texts = [element.get_text() for element in p
                     if isinstance(element, LTTextContainer)]

            yield texts
