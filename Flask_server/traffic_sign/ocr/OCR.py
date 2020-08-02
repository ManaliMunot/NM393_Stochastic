# USAGE
# python text_detection.py --image images/lebron_james.jpg --east frozen_east_text_detection.pb

# import the necessary packages
from imutils.object_detection import non_max_suppression
import numpy as np

import time
import cv2
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_text(image,width=320,height=320,confidence=0.5,east=""):
  east  = os.curdir+'/frozen_east_text_detection.pb'
# load the input image and grab the image dimensions
  image = cv2.imread(image)
  orig = image.copy()
  (H, W) = image.shape[:2]

# set the new width and height and then determine the ratio in change
# for both the width and height
  (newW, newH) = (width, height)
  rW = W / float(newW)
  rH = H / float(newH)

# resize the image and grab the new image dimensions
  image = cv2.resize(image, (newW, newH))
  (H, W) = image.shape[:2]

# define the two output layer names for the EAST detector model that
# we are interested -- the first is the output probabilities and the
# second can be used to derive the bounding box coordinates of text
  layerNames = [
	"feature_fusion/Conv_7/Sigmoid",
	"feature_fusion/concat_3"]


# load the pre-trained EAST text detector
  print("[INFO] loading EAST text detector...")
  net = cv2.dnn.readNet(east)

# construct a blob from the image and then perform a forward pass of
# the model to obtain the two output layer sets
  blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
	(123.68, 116.78, 103.94), swapRB=True, crop=False)
  start = time.time()
  net.setInput(blob)
  (scores, geometry) = net.forward(layerNames)
  end = time.time()

# show timing information on text prediction
  print("[INFO] text detection took {:.6f} seconds".format(end - start))

# grab the number of rows and columns from the scores volume, then
# initialize our set of bounding box rectangles and corresponding
# confidence scores
  (numRows, numCols) = scores.shape[2:4]
  rects = []
  confidences = []

# loop over the number of rows
  for y in range(0, numRows):
	# extract the scores (probabilities), followed by the geometrical
	# data used to derive potential bounding box coordinates that
	# surround text
      scoresData = scores[0, 0, y]
      xData0 = geometry[0, 0, y]
      xData1 = geometry[0, 1, y]
      xData2 = geometry[0, 2, y]
      xData3 = geometry[0, 3, y]
      anglesData = geometry[0, 4, y]

	# loop over the number of columns
      for x in range(0, numCols):
		# if our score does not have sufficient probability, ignore it
          if scoresData[x] < confidence:
              continue

		# compute the offset factor as our resulting feature maps will
		# be 4x smaller than the input image
          (offsetX, offsetY) = (x * 4.0, y * 4.0)

		# extract the rotation angle for the prediction and then
		# compute the sin and cosine
          angle = anglesData[x]
          cos = np.cos(angle)
          sin = np.sin(angle)

		# use the geometry volume to derive the width and height of
		# the bounding box
          h = xData0[x] + xData2[x]
          w = xData1[x] + xData3[x]

		# compute both the starting and ending (x, y)-coordinates for
		# the text prediction bounding box
          endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
          endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
          startX = int(endX - w)
          startY = int(endY - h)

		# add the bounding box coordinates and probability score to
		# our respective lists
          rects.append((startX, startY, endX, endY))
          confidences.append(scoresData[x])

# apply non-maxima suppression to suppress weak, overlapping bounding
# boxes
  boxes = non_max_suppression(np.array(rects), probs=confidences)
  results = []
  text_res = []
# loop over the bounding boxes
  for (startX, startY, endX, endY) in boxes:
      startX = int(startX * rW)
      startY = int(startY * rH)
      endX = int(endX * rW)
      endY = int(endY * rH)
      orig1 = orig.copy()
      gray = cv2.cvtColor(orig1, cv2.COLOR_BGR2GRAY)
      blur = cv2.GaussianBlur(gray, (3,3), 0)
      thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph open to remove noise and invert image
      kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
      opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
      invert = 255 - opening
      r = orig1[startY:endY, startX:endX]
      r = orig1[startY-5:endY+5, startX-5:endX+5]
      configuration = ("-l eng --oem 1 --psm 8")
      text = pytesseract.image_to_string(r, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
      results.append(((startX, startY, endX, endY), text))
      text_res.append(text)
    #return text'''
  for ((start_X, start_Y, end_X, end_Y), text) in results:
	  # display the text detected by Tesseract
	  print("{}\n".format(text))

	# Displaying text
	  text = "".join([x if ord(x) < 128 else "" for x in text]).strip()
	  cv2.rectangle(orig, (start_X, start_Y), (end_X, end_Y),(0, 255, 0), 2)
	  cv2.putText(orig, text, (start_X, end_Y + 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255, 0), 2)
  cv2.imwrite('res.jpg',orig)
  return text_res
if __name__=="__main__": get_text('download (2).jfif')
