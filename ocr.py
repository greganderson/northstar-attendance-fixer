import cv2
import easyocr
import matplotlib.pyplot as plt

def draw_boxes(names, image, detections, threshold = 0.25):
    for bbox, text, score in detections:
        if score > threshold:
            cv2.rectangle(image, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 5)
            cv2.putText(image, text, tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.65, (255, 0, 0), 2)

img_path = "./templates/names.png"
img = cv2.imread(img_path)

names = ["Olmstead, Michael", "Hymas, Izabelle", "Nield, Bailey"]
reader = easyocr.Reader(["en"], gpu = False)
text_detections = reader.readtext(img)
threshold = 0.8
draw_boxes(names, img, text_detections, threshold)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGBA))
plt.show()
