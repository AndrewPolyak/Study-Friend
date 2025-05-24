##
# This file contains utility logic that converts various files' contents to usable text. 
#
# Author: Andrew Polyak
# Version: May 23, 2025
##

import textract # Easy text extraction all-in-one interface
import easyocr # Better for hand-written text

import image_processor # Interface for image pre-processing tasks

class TextExtractor():
    """
    This class contains functions that extract and return text from files.
    """
    def __init__(self):
        super().__init__()

        self.easy_ocr: easyocr.Reader = easyocr.Reader(["en"]) # English only for now
        self.img_processor: image_processor.ImageProcessor = image_processor.ImageProcessor()

        self.API_available = False # TODO run process to determine this

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

        # Hand-written documents require specialized processing
        if hand_written:
            # Pre-process image to improve performance
            pre_processed_img = self.img_processor.pre_process_image(file_path=file_path)

            # Attempt to use advanced Azure API for handwriting recognition
            if self.API_available:
                    # TODO Use this free OCR API: https://azure.microsoft.com/en-us/products/ai-services/ai-vision?msockid=2b3c822dd43d6f6f08529606d5cd6ea8#Pricing-5
                    pass
            
            # If API unavailable, rely on lighter-weight, free method
            # TODO: Accuracy is unusable with this method...
            else:
                extracted_text: str = self.easy_ocr.readtext(image=pre_processed_img,
                                                            detail=0,
                                                            paragraph=True)[0]
        # For non-hand-written documents, use Textract
        else:
            extracted_text: str = textract.process(filename=file_path)

        return extracted_text


# Test
def main():
    extractor = TextExtractor()
    
    print("Starting test...\n\n")
    print(f"Word Printed Document Conversion:\n{extractor.extract_text(file_path="test documents/Bioluminescence_Sample_Text.docx")}\n\n")
    print(f"JPEG Hand Written Document Conversion:\n{extractor.extract_text(file_path="test documents/write-hand-written-notes-and-assignments-for-you.jpeg", hand_written=True)}\n\n")


if __name__ == "__main__":
    main()
