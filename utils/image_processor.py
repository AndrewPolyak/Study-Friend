##
# This file contains utility logic that pre-processes images to be more computer-readable.
#
# Author: Andrew Polyak
# Version: May 23, 2025
##

import cv2

# TODO - Consider this to improve the pre-processing: https://github.com/facebookresearch/AugLy

class ImageProcessor():
    """
    TODO
    """
    def __init__(self):
        super().__init__()

    def pre_process_image(self, file_path):
        """
        TODO
        """

        image = cv2.imread(filename=file_path)

        # Convert to RBG to grayscale
        image = cv2.cvtColor(src=image,
                             code=cv2.COLOR_BGR2GRAY)
        
        # Rescale to properly emphasize small characters of text
        image = cv2.resize(src=image,
                           dsize=None,
                           fx=2, # 2X on x-axis
                           fy=2, # 2X on y-axis
                           interpolation=cv2.INTER_CUBIC)
        
        # Bilateral filtering to reduce noise while keeping sharp edges
        image = cv2.bilateralFilter(src=image,
                                    d=9,
                                    sigmaColor=75,
                                    sigmaSpace=75)
        
        # Apply thresholding to make whites lighter and blacks darker
        image = cv2.adaptiveThreshold(src=image,
                                      maxValue=255, # White
                                      adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      thresholdType=cv2.THRESH_BINARY,
                                      blockSize=41, # Number of pixels used to determine threshold value
                                      C=5) # To reduce noise

        return image
        
# Test
def main():
    processor = ImageProcessor()

    image = processor.pre_process_image(file_path="test documents/write-hand-written-notes-and-assignments-for-you.jpeg")
    cv2.imshow("Result", image)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
