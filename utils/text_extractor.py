##
# This file contains utility logic that converts various files' contents to usable text. 
#
# Author: Andrew Polyak
# Version: May 26, 2025
##

import json
import time
import io
import pathlib

from PIL import Image

import textract # Encompasses extraction for a good number of file types out-of-the-box

# For other extraction tasks that textract doesn't easily support
import PyPDF2

# Azure Computer Vision API-related modules
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes


class TextExtractor():
    """
    This class provides `extract_text()`, an interface to extract the text (printed or handwritten)
    from images, PDFs, Word, Excel, CSV, PowerPoint, & TXT documents, returning the raw text.
    """
    def __init__(self):
        super().__init__()
        
        # Access Azure credentials
        with open(".venv/azure_credentials.json", "r") as credentials: # TODO fix path prior to release
            self.AZURE_CRED: json = json.load(credentials)
            print("Azure credentials successfully loaded")


    def extract_text(self,
                     file_path: str,
                     hand_written: bool = False) -> str:
        """
        This function returns the text from most standard files and images.
        
        Args:
            file_path: str --> The file path of the document being processed
            hand_written: bool --> True if the text being extracted is handwritten
        
        Returns:
            The raw text from the document
        """

        extracted_text: str = ""
        extension = pathlib.Path(file_path).suffix # Get file extension (e.g., .pdf)

        # Handwritten documents require specialized processing
        if hand_written:
            try: # Attempt to use advanced Azure API for handwriting recognition
                extracted_text = self.azure_ocr(file=file_path, ext=extension)
            
            except:
                extracted_text = "Text extraction task failed"
        
        # For non-handwritten documents, use Textract or PyPDF
        else:
            if extension == ".pdf": # Textract doesn't easily support PDF
                reader = PyPDF2.PdfReader(open(file_path, "rb"))

                for page in range(0, len(reader.pages)):
                    extracted_text += reader.pages[page].extract_text()

            else: # Use Textract for all other documents
                extracted_text = textract.process(filename=file_path)

        return extracted_text
    

    def azure_ocr(self,
                  file: str,
                  ext: str) -> str:
        """
        This function returns the text from handwritten images / PDFs by
        leveraging the Azure Computer Vision API.

        Args:
            file: str --> The file path of the image or PDF being processed
            ext: str --> The extension of the file
        
        Returns:
            The raw text from the image
        """

        # Establish Azure endpoint connection
        key: str = self.AZURE_CRED["ACCOUNT_KEY"]
        endpoint: str = self.AZURE_CRED["END_POINT"]

        credentials = CognitiveServicesCredentials(key)
        client = ComputerVisionClient(endpoint=endpoint,
                                      credentials=credentials)
        
        # Prepare file and call endpoint
        if ext == ".pdf": # PDF
            # Call Azure endpoint
            raw_http_response = client.read_in_stream(image=open(file, "rb"),
                                                      language="en",
                                                      raw=True)
        else: # IMAGE
            with Image.open(file) as img:
                with io.BytesIO() as output: # In-memory binary stream of image
                    img.convert(mode="RGB").save(fp=output, format="JPEG") # Ensure image is JPEG format
                    output.seek(0) # Reset binary stream pointer to beginning

                    # Call Azure endpoint
                    raw_http_response = client.read_in_stream(image=output,
                                                            language="en",
                                                            raw=True)

        # Get operation ID from returned headers
        operation_location = raw_http_response.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        # Access returned OCR result
        while True:
            result = client.get_read_result(operation_id=operation_id)

            # Repeat attempting to access result if it hasn't been returned yet
            if result.status not in ["notStarted", "running"]:
                break
            time.sleep(1)

        # Extract data from OCR result
        extracted_text = ""

        if result.status == OperationStatusCodes.succeeded:
            for line in result.analyze_result.read_results[0].lines:
                extracted_text += line.text + "\n"

        return extracted_text
        
        
# Test
def main():
    extractor = TextExtractor()

    print("Starting test...\n\n")
    
    # Word extraction
    print(f"Word Printed Document Conversion:\n{extractor.extract_text(file_path="test documents/Bioluminescence_Sample_Text.docx")}\n\n")

    # Image (hand-written text) extraction
    print(f"JPEG Hand Written Document Conversion:\n{extractor.extract_text(file_path="test documents/write-hand-written-notes-and-assignments-for-you.jpeg", hand_written=True)}\n\n")

    # PDF printed extraction
    print(f"PDF Printed Document Conversion:\n{extractor.extract_text(file_path="test documents/4_day_gym_plan.pdf")}\n\n")

    # PDF (hand-written) extraction
    print(f"PDF Hand Written Document Conversion:\n{extractor.extract_text(file_path="test documents/4_day_gym_plan.pdf", hand_written=True)}\n\n")
    
    # TXT extraction
    print(f"TXT Printed Document Conversion:\n{extractor.extract_text(file_path="test documents/ComputerScienceFunFacts.txt")}\n\n")

    # CSV extraction
    print(f"CSV Printed Document Conversion:\n{extractor.extract_text(file_path="test documents/RandomCompanyData.csv")}\n\n")

    # Excel extraction
    print(f"Excel Printed Document Conversion:\n{extractor.extract_text(file_path="test documents/BestRestaurantsCanada2025.xlsx")}\n\n")

    # PowerPoint extraction
    print(f"PowerPoint Printed Document Conversion:\n{extractor.extract_text(file_path="test documents/Notebook Lesson XL by Slidesgo.pptx")}\n\n")


if __name__ == "__main__":
    main()
