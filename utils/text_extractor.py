##
# This file contains utility logic that converts various files' contents to usable text. 
#
# Author: Andrew Polyak
# Version: May 22, 2025
##

import textract # Easy text extraction all-in-one interface
import easyocr # Better for hand-written text

import os
os.environ['PATH'] += os.pathsep + r'C:\Program Files\Tesseract' # TODO Remove this in non-local environment

class TextExtractor():
    """
    This class contains functions that extract and return text from files.
    """
    def __init__(self):
        super().__init__()

        self.easy_ocr = easyocr.Reader(["en"]) # English only # TODO for now...

    def extract_text(self,
                     file_path: str,
                     hand_written: bool = False) -> str:
        """
        This function returns the text from most standard files based on the
        Textract interface.
        
        Args:
            file_path: str --> The file path of the document being processed
            hand_written: bool --> True if the text being extracted is hand written
        
        Returns:
            The raw text from the document
        """

        # EasyOCR is the best free method of hand written text extraction.
        # In future versions, perhaps a more advanced, paid API can be used
        if hand_written:
            # TODO Must implement image pre-processing to improve performance... Use https://www.freecodecamp.org/news/getting-started-with-tesseract-part-ii-f7f9a0899b3f/

            # Extract hand writing content
            extracted_text = self.easy_ocr.readtext(image=file_path,
                                                    detail=0,
                                                    paragraph=True)[0]

        else:
            # Extract hand written content
            extracted_text: str = textract.process(filename=file_path)

        return extracted_text


# Test
def main():
    extractor = TextExtractor()
    
    print()
    print(f"Word Printed Document Conversion:\n{extractor.extract_text(file_path="test documents/Bioluminescence_Sample_Text.docx")}\n\n")
    print(f"JPEG Hand Written Document Conversion:\n{extractor.extract_text(file_path="test documents/write-hand-written-notes-and-assignments-for-you.jpeg", hand_written=True)}\n\n")


if __name__ == "__main__":
    main()
