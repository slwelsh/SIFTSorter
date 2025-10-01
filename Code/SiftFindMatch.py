import cv2
from ReadFolder import ImageLoader
from ReadFolder import MyImage
import autocropalt
from CustomDetector import CustomDetector
import os


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


# This is a class that better organizes match results by saving two variables
class Match:
    def __init__(self, match_result, computed_score, key_points1 = None, key_points2 = None, best_p = None):
        self.isMatch = match_result
        self.score = computed_score
        self.kp1 = key_points1
        self.kp2 = key_points2
        self.best_points = best_p


# This is a class that organizes the info that will be saved in each row of csv file
class MatchResults:
    def __init__(self, original_photo_name, compare_photo_name, match_score, match_result):
        self.original_name = original_photo_name
        self.compare_name = compare_photo_name
        self.match_score = match_score
        self.match_result = match_result


# This is a class that gets all SIFT scores and finds the first match for a new photo in a database of pictures
class SiftFindMatch:

    # Initializer with additional customization
    def __init__(self, cfg_file_path=None, yolo_weights_path=None, is_auto_cropped=True, resized_width=250, distance_coefficient=0.67, acceptance_number=4):
        self.resized_width = resized_width
        self.distance_coefficient = distance_coefficient
        self.acceptance_number = acceptance_number
        self.cfg_file_path = cfg_file_path
        self.yolo_weights_path = yolo_weights_path
        self.is_auto_cropped = is_auto_cropped

    # Loads a picture given a file path
    def load_picture(self, image_path):
        image = cv2.imread(image_path)
        if self.is_auto_cropped is True and self.cfg_file_path is not None and self.yolo_weights_path is not None:
            custom_detector = CustomDetector(self.cfg_file_path, self.yolo_weights_path)
            image = custom_detector.crop(image)
        image = resize_with_aspect_ratio(image, width=self.resized_width)
        return image

    # Function that tries to determine whether two pictures are a match based off of match score and acceptance number
    def is_match(self, original_image, compare_image, real_original_image, real_compare_image):
        try:
            # 2) Check for similarities between the 2 images
            sift = cv2.SIFT_create()
            kp_1, desc_1 = sift.detectAndCompute(original_image, None)
            kp_2, desc_2 = sift.detectAndCompute(compare_image, None)

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
            else:
                best_good_points.extend(good_points_alternative)

            # Define how similar they are
            if len(kp_1) <= len(kp_2):
                number_keypoints = len(kp_1)
            else:
                number_keypoints = len(kp_2)

            match_score = len(best_good_points) / number_keypoints * 100

            if match_score >= self.acceptance_number:
                return Match(True, match_score, kp_1, kp_2, best_good_points)
            else:
                return Match(False, match_score)
        except:
            if real_original_image is None or real_compare_image is None:
                print("Test Failed")
                return Match(False, 0)
            else:
                if self.is_auto_cropped is True and self.cfg_file_path is not None and self.yolo_weights_path is not None:
                    new_original = autocropalt.crop(real_original_image)
                    new_compare_image = autocropalt.crop(real_compare_image)
                else:
                    new_original = real_original_image
                    new_compare_image = real_compare_image
                new_original = resize_with_aspect_ratio(new_original, width=self.resized_width)
                new_compare_image = resize_with_aspect_ratio(new_compare_image, width=self.resized_width)
                return self.is_match(new_original, new_compare_image, None, None)

    # Function that initiates matching
    def start_matching(self, image_path, photo_directory_path):
        match_result_list = []
        total_matches = 0
        highest_acceptance = None
        kps = None
        best_match = None
        best_pts = None

        print('\n~~~~Loading Database~~~~\n')
        image_loader = ImageLoader(self.cfg_file_path, self.yolo_weights_path, self.is_auto_cropped, self.resized_width)
        images = image_loader.load_images_from_folder(photo_directory_path)

        img = cv2.imread(image_path)
        original_loader = MyImage(img, os.path.basename(image_path), self.resized_width, self.cfg_file_path, self.yolo_weights_path, self.is_auto_cropped)
        original = original_loader
        processed_original_image = original.processed_img

        print('\n~~~~Finding Matches~~~~\n')

        for i in range(len(images)):
            print(str(original) + ' compared with ' + str(images[i]))
            image_to_compare = images[i].processed_img
            match_result = self.is_match(processed_original_image, image_to_compare, original.img, images[i].img)

            
            if match_result.isMatch is True:
                print('\033[1;32;40m\t Match Found! (score = ' + str(match_result.score) + ')\033[0m')
                match_info = MatchResults(str(original), str(images[i]), match_result.score, "Acceptance")
                match_result_list.append(match_info)
                total_matches += 1
                if highest_acceptance is None or match_result.score > highest_acceptance:
                            highest_acceptance = match_result.score
                            kps = [match_result.kp1, match_result.kp2]
                            best_match = str(images[i])
                            best_pts = match_result.best_points
            else:
                print('\t no match (score = ' + str(match_result.score) + ')')
                match_info = MatchResults(str(original), str(images[i]), match_result.score, "Rejection")
                match_result_list.append(match_info)
                        


        # This displays the results of the program in the console
        print('\n ~~~~RESULTS~~~~\n')
        print('resized-width: ' + str(self.resized_width))
        print('distance_coefficient: ' + str(self.distance_coefficient))
        print('acceptance_number: ' + str(self.acceptance_number))
        print('total_matches: ' + str(total_matches) + '\n')
    
        print('Matches: ')
        for match_info in match_result_list:
            if match_info.match_result == "Acceptance":
                print(f"{match_info.compare_name:<20} {match_info.match_result:<12} {match_info.match_score:.4f} ")

        # This displays the best match found for the target picture (like the Sift Comparator)
        if (total_matches > 0):
            pic = self.load_picture(image_path)
            pic2 = self.load_picture(photo_directory_path +'/'+ str(best_match))
            result = cv2.drawMatches(pic, kps[0], pic2, kps[1], best_pts, None)

            cv2.imshow("Result", result)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

