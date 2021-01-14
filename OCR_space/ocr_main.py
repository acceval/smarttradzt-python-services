# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 11:51:23 2021

@author: James Ang
"""

import io
import json
import cv2
import numpy as np
import requests

img = cv2.imread("RussiaDLC-1.png")
height, width, _ = img.shape

# cv2.imshow('image',img)
# #waits for user to press any key  
# #(this is necessary to avoid Python kernel form crashing) 
# cv2.waitKey(0)
  
# #closing all open windows
# cv2.destroyAllWindows()

url_api = "https://api.ocr.space/parse/image"
_, compressedimage = cv2.imencode(".jpg", img, [1, 90])
file_bytes = io.BytesIO(compressedimage)

result = requests.post(url_api,
              files = {"screenshot.jpg": file_bytes},
              data = {"apikey": "ad82a1baad88957",
                      "language": "eng"})

result = result.content.decode()
result = json.loads(result)

parsed_results = result.get("ParsedResults")[0]
text_detected = parsed_results.get("ParsedText")
print(text_detected)