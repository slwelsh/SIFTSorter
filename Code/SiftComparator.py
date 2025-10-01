import cv2
from CustomDetector import CustomDetector


# Function that resizes an image
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


# Class that can be used to compare two image using SIFT. This can be useful for debugging certain irregularities in
# the SIFT matcher
class SiftComparator:
    # Initialization function
    def __init__(self, cfg_file_path=None, yolo_weights_path=None, is_auto_cropped=True, resized_width=250, distance_coefficient=0.67):
        self.is_auto_cropped = is_auto_cropped
        self.resized_width = resized_width
        self.distance_coefficient = distance_coefficient
        self.cfg_file_path = cfg_file_path
        self.yolo_weights_path = yolo_weights_path

    # Loads a picture given a file path
    def load_picture(self, image_path):
        image = cv2.imread(image_path)
        if self.is_auto_cropped is True and self.cfg_file_path is not None and self.yolo_weights_path is not None:
            custom_detector = CustomDetector(self.cfg_file_path, self.yolo_weights_path)
            image = custom_detector.crop(image)
        image = resize_with_aspect_ratio(image, width=self.resized_width)
        return image

    # Starts comparing two photos
    def start_matching(self, image_path_1, image_path_2):
        original = self.load_picture(image_path_1)
        image_to_compare = self.load_picture(image_path_2)

        # 1) Check if 2 images are equals
        if original.shape == image_to_compare.shape:
            print("The images have same size and channels")
            difference = cv2.subtract(original, image_to_compare)
            b, g, r = cv2.split(difference)

            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                print("The images are completely Equal")
            else:
                print("The images are NOT equal")

        # 2) Check for similarities between the 2 images
        sift = cv2.SIFT_create()
        kp_1, desc_1 = sift.detectAndCompute(original, None)
        kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)

        index_params = dict(algorithm=0, trees=5)
        search_params = dict()
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(desc_1, desc_2, k=2)

        good_points = []
        for m, n in matches:
            if m.distance < self.distance_coefficient * n.distance:
                good_points.append(m)

        matches_alternative = flann.knnMatch(desc_2, desc_1, k=2)

        good_points_alternative = []
        for m, n in matches_alternative:
            if m.distance < self.distance_coefficient * n.distance:
                good_points_alternative.append(m)

        best_good_points = []
        if len(good_points) >= len(good_points_alternative):
            best_good_points.extend(good_points)
            matches_first_match = True
        else:
            best_good_points.extend(good_points_alternative)
            matches_first_match = False

        # Define how similar they are
        if len(kp_1) <= len(kp_2):
            number_keypoints = len(kp_1)
        else:
            number_keypoints = len(kp_2)

        # Output results
        print("Keypoints 1ST Image: " + str(len(kp_1)))
        print("Keypoints 2ND Image: " + str(len(kp_2)))
        print("GOOD Matches:", len(good_points))
        print("How good it's the match: ", len(best_good_points) / number_keypoints * 100)
        if (len(best_good_points) / number_keypoints * 100) >= 4:
            print('\033[1;32;40m Images match!\033[0m')
        else:
            print('\033[1;31;40m Not a match :(\033[0m')

        if matches_first_match:
            result = cv2.drawMatches(original, kp_1, image_to_compare, kp_2, good_points, None)
        else:
            result = cv2.drawMatches(image_to_compare, kp_2, original, kp_1, good_points_alternative, None)

        cv2.drawKeypoints(original, kp_1, original)
        cv2.drawKeypoints(image_to_compare, kp_2, image_to_compare)

        cv2.imshow("result", result)

        cv2.imshow("First_Image_Keypoints", original)
        cv2.imshow("Second_Image_Keypoints", image_to_compare)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
