import cv2
import os
import ReadFolder
import csv
import autocropalt


class Match:
    def __init__(self, match_result, computed_score):
        self.isMatch = match_result
        self.score = computed_score


class SiftMatcher:
    def __init__(self, photo_directory_path, save_directory_path):
        self.resized_width = 250
        self.distance_coefficient = 0.67
        self.acceptance_number = 4
        self.save_directory_path = save_directory_path
        self.images = ReadFolder.load_images_from_folder(photo_directory_path, width=250)

    def __init__(self, resized_width, distance_coefficient, acceptance_number, photo_directory_path, save_directory_path):
        self.resized_width = resized_width
        self.distance_coefficient = distance_coefficient
        self.acceptance_number = acceptance_number
        self.save_directory_path = save_directory_path
        self.images = ReadFolder.load_images_from_folder(photo_directory_path, width=resized_width)

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

            # Define how similar they are
            if len(kp_1) <= len(kp_2):
                number_keypoints = len(kp_1)
            else:
                number_keypoints = len(kp_2)

            print("How good is the match: ", len(good_points) / number_keypoints * 100)
            if (len(good_points) / number_keypoints * 100) >= self.acceptance_number:
                return Match(True, len(good_points) / number_keypoints * 100)
            else:
                return Match(False, len(good_points) / number_keypoints * 100)
        except:
            if real_original_image is None or real_compare_image is None:
                print("How good is the match: Failed")
                return Match(False, 0)
            else:
                new_original = autocropalt.crop(real_original_image)
                new_original = ReadFolder.resize_with_aspect_ratio(new_original, width=self.resized_width)
                new_compare_image = autocropalt.crop(real_compare_image)
                new_compare_image = ReadFolder.resize_with_aspect_ratio(new_compare_image, width=self.resized_width)
                return self.is_match(new_original, new_compare_image, None, None)

    def start_matching(self):
        csv_match_results_file = []
        new_folder = []

        lowest_true_acceptance = 100
        highest_false_acceptance = 0
        lowest_false_rejection = 100
        highest_true_rejection = 0

        false_instances = 0
        false_acceptance_list = []
        false_rejection_list = []
        false_acceptance_instances = 0
        false_rejection_instances = 0

        while len(self.images) > 0:
            temporaryList = [self.images[0]]
            original = self.images[0].processed_img
            print('Photos Left To Sort:' + str(len(self.images)) + ' (' + str(self.images[0]) + ')')
            for i in range(len(self.images)):
                if i == len(self.images) - 1:
                    pass
                else:
                    print(str(self.images[0]) + ' compared with ' + str(self.images[i + 1]))
                    image_to_compare = self.images[i + 1].processed_img
                    match_result = self.is_match(original, image_to_compare, self.images[i].img, self.images[i + 1].img)

                    if str(self.images[0]).split('-')[0] == str(self.images[i + 1]).split('-')[0]:
                        if match_result.isMatch is True:
                            print('True Acceptance')
                            if match_result.score < lowest_true_acceptance:
                                lowest_true_acceptance = match_result.score
                            csv_match_results_file.append([str(self.images[0]), str(self.images[i + 1]), match_result.score, 'True Acceptance'])
                        else:
                            false_instances += 1
                            false_rejection_instances += 1
                            print('False Rejection')
                            false_rejection_list.append(match_result.score)
                            if match_result.score < lowest_false_rejection:
                                lowest_false_rejection = match_result.score
                            csv_match_results_file.append([str(self.images[0]), str(self.images[i + 1]), match_result.score, 'False Rejection'])

                    else:
                        if match_result.isMatch is True:
                            false_instances += 1
                            false_acceptance_instances += 1
                            print('False Acceptance')
                            false_acceptance_list.append(match_result.score)
                            if match_result.score > highest_false_acceptance:
                                highest_false_acceptance = match_result.score
                            csv_match_results_file.append([str(self.images[0]), str(self.images[i + 1]), match_result.score, 'False Acceptance'])

                        else:
                            print('True Rejection')
                            if match_result.score > highest_true_rejection:
                                highest_true_rejection = match_result.score
                        csv_match_results_file.append([str(self.images[0]), str(self.images[i + 1]), match_result.score, 'True Rejection'])

                    if match_result.isMatch is True:
                        temporaryList.append(self.images[i + 1])
            new_folder.append(temporaryList)
            for i in range(len(temporaryList)):
                self.images.remove(temporaryList[i])

        false_rejection_list.sort()
        false_acceptance_list.sort()
        # This clears the text file from any previous usage of the program
        yolo_text_file = open("details.txt", "a+")
        yolo_text_file.truncate(0)
        yolo_text_file.write(str(new_folder))
        yolo_text_file.write('resized-width: ' + str(self.resized_width))
        yolo_text_file.write('distance_coefficient: ' + str(self.distance_coefficient))
        yolo_text_file.write('acceptance_number: ' + str(self.acceptance_number))
        yolo_text_file.write('false_instances: ' + str(false_instances))
        yolo_text_file.write('false_acceptance_instances: ' + str(false_acceptance_instances))
        yolo_text_file.write('false_acceptance_list: \n')
        yolo_text_file.write(str(false_acceptance_list))
        yolo_text_file.write('false_rejection_instances: ' + str(false_rejection_instances))
        yolo_text_file.write('false_rejection_list: \n')
        yolo_text_file.write(str(false_rejection_list))

        print(new_folder)
        print('resized-width: ' + str(self.resized_width))
        print('distance_coefficient: ' + str(self.distance_coefficient))
        print('acceptance_number: ' + str(self.acceptance_number))
        print('false_instances: ' + str(false_instances))
        print('false_acceptance_instances: ' + str(false_acceptance_instances))
        print('false_acceptance_list: '), print(false_acceptance_list)
        print('false_rejection_instances: ' + str(false_rejection_instances))
        print('false_rejection_list: '), print(false_rejection_list)
        print('lowest_true_acceptance: ' + str(lowest_true_acceptance))
        print('lowest_false_rejection: ' + str(lowest_false_rejection))
        print('highest_false_acceptance: ' + str(highest_false_acceptance))
        print('highest_true_rejection: ' + str(highest_true_rejection))

        csv_writer = csv.writer(open("output.csv", "w"))
        csv_writer.writerow(["ID_1", "ID_2", "Matching_score", "Result"])
        for row in csv_match_results_file:
            csv_writer.writerow(row)

        for subFolder in range(len(new_folder)):
            os.makedirs(os.path.join(self.save_directory_path, 'Turtle ' + str(subFolder + 1)))
            for image in range(len(new_folder[subFolder])):
                path = self.save_directory_path + '/' + 'Turtle ' + str(subFolder + 1)
                cv2.imwrite(os.path.join(path, str(new_folder[subFolder][image])), new_folder[subFolder][image].img)

