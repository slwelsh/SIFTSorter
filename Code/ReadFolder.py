import cv2
import os
import CustomDetector


def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    try:
        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(image, dim, interpolation=inter)
    except:
        return None


class MyImage:
    def __init__(self, img_name, folder, width):
        self.img = cv2.imread(os.path.join(folder,img_name))
        new_image = self.img
        new_image = CustomDetector.crop(new_image)
        new_image = resize_with_aspect_ratio(new_image, width=width)
        self.processed_img = new_image
        self.__name = img_name

    def __str__(self):
        return self.__name


def load_images_from_folder(folder, width):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            print(filename + ' has been loaded')
            images.append(MyImage(filename, folder, width))
    return images

