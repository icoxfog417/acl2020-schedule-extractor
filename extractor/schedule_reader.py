from extractor.pdf_reader import PDFReader


class ScheduleReader():
    """
    Extract schedule from ACL2020 anthology.
    Link: https://acl2020.org/schedule/
    """

    def __init__(self, acl_schedule_path):
        self.path = acl_schedule_path
        self.reader = PDFReader(self.path, start_page=74)
