##
# This file contains utility logic that converts various files' contents to usable text. 
#
# Author: Andrew Polyak
# Version: May 23, 2025
##

import json
import time
import io

from PIL import Image

import textract # Easy text extraction all-in-one interface
import easyocr # Free, light-weight, hand-written text extractor

import image_processor # Interface for image pre-processing tasks

# Azure Computer Vision API-related modules
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes


class TextExtractor():
    """
    This class contains functions that extract and return text from files.
    """
    def __init__(self):
        super().__init__()

        self.easy_ocr: easyocr.Reader = easyocr.Reader(["en"]) # English only for now
        self.img_processor: image_processor.ImageProcessor = image_processor.ImageProcessor()

        self.AZURE_CRED: json = None

        # Access Azure credentials
        with open(".venv/azure_credentials.json", "r") as credentials: # TODO fix path prior to release
            self.AZURE_CRED = json.load(credentials)
            print("Azure credentials successfully loaded")


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
            try: # Attempt to use advanced Azure API for handwriting recognition
                extracted_text: str = self.azure_ocr(image=file_path)
            
            except: # If API unavailable, rely on lighter-weight, free method
                print("Azure connection failed... using EasyOCR")
                pre_processed_img = self.img_processor.pre_process_image(file_path=file_path) # Pre-process image to improve performance

                extracted_text: str = self.easy_ocr.readtext(image=pre_processed_img, # TODO: Accuracy is unusable with this method...
                                                            detail=0,
                                                            paragraph=True)[0]
        
        # For non-hand-written documents, use Textract
        else:
            extracted_text: str = textract.process(filename=file_path)

        return extracted_text
    

    def azure_ocr(self,
                  image) -> str:
        """
        TODO
        """

        # Establish Azure endpoint connection
        key = self.AZURE_CRED["ACCOUNT_KEY"]
        endpoint = self.AZURE_CRED["END_POINT"]

        credentials = CognitiveServicesCredentials(key)
        client = ComputerVisionClient(endpoint=endpoint,
                                      credentials=credentials)

        # Prepare image and call endpoint
        with Image.open(image) as img:
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
    
    # Word document extraction
    print(f"Word Printed Document Conversion:\n{extractor.extract_text(file_path="test documents/Bioluminescence_Sample_Text.docx")}\n\n")

    # Image (hand-written text) extraction
    print(f"JPEG Hand Written Document Conversion:\n{extractor.extract_text(file_path="test documents/write-hand-written-notes-and-assignments-for-you.jpeg", hand_written=True)}\n\n")

    # TODO confirm PDF extraction

    # TODO confirm TXT extraction

    # TODO confirm CSV extraction

    # TODO confirm Excel extraction

    # TODO confirm PowerPoint extraction


if __name__ == "__main__":
    main()
