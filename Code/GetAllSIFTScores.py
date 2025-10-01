import cv2
from ReadFolder import ImageLoader
import autocropalt
import csv


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
    def __init__(self, match_result, computed_score):
        self.isMatch = match_result
        self.score = computed_score


# This is a class that organizes the info that will be saved in each row of csv file
class MatchResults:
    def __init__(self, original_photo_name, compare_photo_name, match_score, match_result):
        self.original_name = original_photo_name
        self.compare_name = compare_photo_name
        self.match_score = match_score
        self.match_result = match_result


# This is a class that gets all SIFT scores for every possible pair in a photo database
class GetAllSIFTScores:

    # Initializer with additional customization
    def __init__(self, cfg_file_path=None, yolo_weights_path=None, is_auto_cropped=True, resized_width=250, distance_coefficient=0.67, acceptance_number=4):
        self.resized_width = resized_width
        self.distance_coefficient = distance_coefficient
        self.acceptance_number = acceptance_number
        self.cfg_file_path = cfg_file_path
        self.yolo_weights_path = yolo_weights_path
        self.is_auto_cropped = is_auto_cropped

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
            print("How good is the match: ", match_score)

            if match_score >= self.acceptance_number:
                return Match(True, match_score)
            else:
                return Match(False, match_score)
        except:
            if real_original_image is None or real_compare_image is None:
                print("How good is the match: Failed")
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
    def start_matching(self, photo_directory_path, save_directory_path):
        csv_match_results_file = []

        lowest_true_acceptance = None
        highest_false_acceptance = None
        lowest_false_rejection = None
        highest_true_rejection = None

        false_instances = 0
        false_acceptance_instances = 0
        false_acceptance_list = []
        false_rejection_instances = 0
        false_rejection_list = []

        image_loader = ImageLoader(self.cfg_file_path, self.yolo_weights_path, self.is_auto_cropped, self.resized_width)
        images = image_loader.load_images_from_folder(photo_directory_path)

        while len(images) > 0:
            processed_original_image = images[0].processed_img
            print('Photos Left To Compare:' + str(len(images)) + ' (' + str(images[0]) + ')')
            for i in range(len(images)):
                if i is len(images) - 1:
                    pass
                else:
                    print(str(images[0]) + ' compared with ' + str(images[i + 1]))
                    image_to_compare = images[i + 1].processed_img
                    match_result = self.is_match(processed_original_image, image_to_compare, images[i].img, images[i + 1].img)

                    if str(images[0]).split('-')[0] == str(images[i + 1]).split('-')[0]:
                        if match_result.isMatch is True:
                            print('True Acceptance')
                            match_info = MatchResults(str(images[0]), str(images[i + 1]), match_result.score, "True Acceptance")
                            csv_match_results_file.append(match_info)
                            if lowest_true_acceptance is None or match_result.score < lowest_true_acceptance:
                                lowest_true_acceptance = match_result.score
                        else:
                            false_instances += 1
                            false_rejection_instances += 1
                            print('False Rejection')
                            match_info = MatchResults(str(images[0]), str(images[i + 1]), match_result.score, "False Rejection")
                            csv_match_results_file.append(match_info)
                            if lowest_false_rejection is None or match_result.score < lowest_false_rejection:
                                lowest_false_rejection = match_result.score
                    else:
                        if match_result.isMatch is True:
                            false_instances += 1
                            false_acceptance_instances += 1
                            print('False Acceptance')
                            match_info = MatchResults(str(images[0]), str(images[i + 1]), match_result.score, "False Acceptance")
                            csv_match_results_file.append(match_info)
                            if highest_false_acceptance is None or match_result.score > highest_false_acceptance:
                                highest_false_acceptance = match_result.score
                        else:
                            print('True Rejection')
                            match_info = MatchResults(str(images[0]), str(images[i + 1]), match_result.score, "True Rejection")
                            csv_match_results_file.append(match_info)
                            if highest_true_rejection is None or match_result.score > highest_true_rejection:
                                highest_true_rejection = match_result.score

            images.remove(images[0])

        # This organizes the order of two lists that will be outputted and saved to the details text file
        false_rejection_list.sort()
        false_acceptance_list.sort()
        # This clears the text file from any previous usage of the program
        yolo_text_file = open(save_directory_path + "/all_SIFT_Scores_output_details.txt", "a+")
        yolo_text_file.truncate(0)
        # This adds the specifications for a match batch into a viewable details file
        yolo_text_file.write('resized-width: ' + str(self.resized_width) + "\n")
        yolo_text_file.write('distance_coefficient: ' + str(self.distance_coefficient) + "\n")
        yolo_text_file.write('acceptance_number: ' + str(self.acceptance_number) + "\n")
        yolo_text_file.write('false_instances: ' + str(false_instances) + "\n")
        yolo_text_file.write('false_acceptance_instances: ' + str(false_acceptance_instances) + "\n")
        yolo_text_file.write('false_acceptance_list: ' + str(false_acceptance_list) + "\n")
        yolo_text_file.write('false_rejection_instances: ' + str(false_rejection_instances) + "\n")
        yolo_text_file.write('false_rejection_list: ' + str(false_rejection_list) + "\n")
        yolo_text_file.write('lowest_true_acceptance: ' + str(lowest_true_acceptance) + "\n")
        yolo_text_file.write('lowest_false_rejection: ' + str(lowest_false_rejection) + "\n")
        yolo_text_file.write('highest_false_acceptance: ' + str(highest_false_acceptance) + "\n")
        yolo_text_file.write('highest_true_rejection: ' + str(highest_true_rejection) + "\n")

        # This displays the results (which were also saved in the details file) of the program in the console
        print('resized-width: ' + str(self.resized_width))
        print('distance_coefficient: ' + str(self.distance_coefficient))
        print('acceptance_number: ' + str(self.acceptance_number))
        print('false_instances: ' + str(false_instances))
        print('false_acceptance_instances: ' + str(false_acceptance_instances))
        print('false_acceptance_list: ' + str(false_acceptance_list))
        print('false_rejection_instances: ' + str(false_rejection_instances))
        print('false_rejection_list: ' + str(false_rejection_list))
        print('lowest_true_acceptance: ' + str(lowest_true_acceptance))
        print('lowest_false_rejection: ' + str(lowest_false_rejection))
        print('highest_false_acceptance: ' + str(highest_false_acceptance))
        print('highest_true_rejection: ' + str(highest_true_rejection))

        csv_writer = csv.writer(open(save_directory_path + "/all_SIFT_scores_output.csv", "w"))
        csv_writer.writerow(["ID_1", "ID_2", "Matching_score", "Result"])
        for match_info in csv_match_results_file:
            csv_writer.writerow([match_info.original_name, match_info.compare_name, match_info.match_score, match_info.match_result])
