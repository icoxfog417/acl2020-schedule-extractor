import unittest
import pytest
from extractor.pdf_reader import PDFReader


@pytest.mark.usefixtures("path_to_anthology")
class TestPDFReader(unittest.TestCase):

    def test_read_page(self):
        reader = PDFReader(self._path, start_page=27, end_page=50)

        text_stack = []
        for texts in reader.iterate_page_texts():
            self.assertGreater(len(texts), 0)
            text_stack.append(texts)

        self.assertEqual(len(text_stack), 50 - 27 + 1)
        self.assertTrue("Learning to Understand" in " ".join(text_stack[0]))
        self.assertTrue("DeFormer" in " ".join(text_stack[-1]))

    def test_read_schedule(self):
        reader = PDFReader(self._path)
        count = 1
        for texts in reader.iterate_page_texts():
            if count == 1:
                self.assertGreater(len(texts), 0)
                self.assertTrue("Monday, July 6" in " ".join(texts))
            elif count == 272:
                self.assertGreater(len(texts), 0)
                self.assertTrue("Demo Session 5C" in " ".join(texts))

            count += 1

        self.assertEqual(count - 1, 272 - 74 + 1)
