##
# This file contains utility logic that converts various files' contents to usable text. 
#
# We can use the following interface to extract text from documents & other files: https://textract.readthedocs.io/en/stable/
#
# Author: Andrew Polyak
# Date: May 21, 2025
##

import textract

class TextExtractor():
    """
    This class contains functions that extract and return text from files.
    """
    def __init__(self):
        super().__init__()

    def extract_text(file_path: str) -> str:
        """
        This function returns the text from most standard files based on the Textract interface.
        """

        extracted_text: str = textract.process(filename=file_path)
        return extracted_text

# Test
def main():
    file_path: str = "test documents/Bioluminescence_Sample_Text.docx"
    
    extracted_text: str = TextExtractor.extract_text(file_path=file_path)
    print(extracted_text)

main()
