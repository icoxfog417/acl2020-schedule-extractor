import re
from datetime import datetime
from extractor.pdf_reader import PDFReader


class ScheduleReader():
    """
    Extract schedule from ACL2020 anthology.
    Link: https://acl2020.org/schedule/
    """

    def __init__(self, acl_schedule_path):
        self.path = acl_schedule_path
        self.start_default = 74
        self.end_default = None

    def iterate_papers(self, start_page=-1, end_page=None):
        start = start_page if start_page > 0 else self.start_default
        end = end_page if end_page is not None else self.end_default
        reader = PDFReader(self.path, start, end)

        index = PaperIndex()
        papers = []
        next_is_session = False
        for texts in reader.iterate_page_texts():
            for t in texts:
                print("> {}".format(t.split("\n")))
                line = t.strip()
                if index.set_day(line):
                    continue
                elif index.set_time(line):
                    next_is_session = True
                    continue
                elif next_is_session and line:
                    index.set_session(line)
                    next_is_session = False
                    continue

                paper = Paper.parse(t, index)
                if paper is not None:
                    papers.append(paper)

        return papers


class Paper():

    def __init__(self, title, kind, authors, index=None):
        self.title = title
        self.kind = kind
        self.authors = authors
        self.index = index

    @classmethod
    def parse(cls, text, index=None):
        kind = re.match(r"\[.+?\]", text)
        if kind is None:
            return None

        kind = kind.group(0)
        title_authors = text.strip().split("\n")
        authors = title_authors[-1].strip()
        title = " ".join(title_authors[:-1])
        title = title.replace(kind, "").strip()
        kind = kind.replace("[", "").replace("]", "")
        return cls(title, kind, authors, index)

    def to_json(self, include_time_to_day=False):
        info = {
            "title": self.title,
            "kind": self.kind,
            "authors": self.authors
        }
        if self.index is not None:
            if include_time_to_day:
                info["day"] = self.index.day.strftime("%Y/%m/%d %H:%M")
            else:
                info["day"] = self.index.day.strftime("%Y/%m/%d")
                info["time"] = self.index.time

            info["session"] = self.index.session
        return info


class PaperIndex():

    def __init__(self, day=None, time=None, session=None):
        self.day = day
        self.time = None
        self.session = None

    @classmethod
    def clone(cls, paper_index):
        return cls(paper_index.day, paper_index.time, paper_index.session)

    def is_full(self):
        indexes = (self.day, self.time, self.session)
        has_indexes = [1 if x is not None else 0 for x in indexes]
        if sum(has_indexes) == len(indexes):
            return True
        else:
            return False

    def set_day(self, text):
        utc = "UTC+0"
        if utc not in text:
            return None
        _text = text[:(text.index(utc) + len(utc) - 2)]
        day = None
        try:
            day = datetime.strptime(_text, "%A, %B %d, %Y %Z")
            self.day = day
            self.time = None
            self.session = None
        except Exception as ex:
            day = None
        return (day is not None)

    def set_time(self, text):
        matched = re.match(r"\d\d\:\d\d–\d\d\:\d\d", text)
        if matched is not None:
            text = matched.group(0)
            time = text.strip()
            start, end = time.split("–")
            hour, minute = start.split(":")
            if self.day is not None:
                self.day = self.day.replace(hour=int(hour), minute=int(minute))
            self.time = time
            self.session = None
            return True
        else:
            return False

    def set_session(self, text):
        self.session = text
