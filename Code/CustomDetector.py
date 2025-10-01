import cv2
import numpy as np
import autocropalt


# Tool that can be used to crop things based off trained data.
class CustomDetector:
    def __init__(self, cfg_file_path, yolo_weights_path):
        self.cfg_file_path = cfg_file_path
        self.yolo_weights_path = yolo_weights_path

    def crop(self, image):
        try:
            # Load Yolo
            net = cv2.dnn.readNet(self.yolo_weights_path, self.cfg_file_path)

            layer_names = net.getLayerNames()
            output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

            # Loading image
            img = image
            img = cv2.resize(img, None, fx=0.4, fy=0.4)
            height, width, channels = img.shape

            # Detecting objects
            blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

            net.setInput(blob)
            outs = net.forward(output_layers)

            # Showing informations on the screen
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.3:
                        # Object detected
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)

                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # Output to files
            roi = img[y:y + h, x:x + w]

            if x < 0 or y < 0 or w < 0 or h < 0:
                roi = autocropalt.crop(image)
                return roi
            else:
                return roi
        except:
            return image
