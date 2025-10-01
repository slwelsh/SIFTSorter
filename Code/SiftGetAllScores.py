import cv2
import ReadFolder
import autocropalt
import csv


resized_width = 250
distance_coefficient = 0.67
acceptance_number = 4
directory_path = ""
new_file = []


class Match:
    def __init__(self, match_result, computed_score):
        self.isMatch = match_result
        self.score = computed_score


class MatchResults:
    def __init__(self, original_photo_name, compare_photo_name, match_result):
        self.original_name = original_photo_name
        self.compare_name = compare_photo_name
        self.score = match_result


def is_match(original_image, compare_image, real_original_image, real_compare_image):
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
            if m.distance < distance_coefficient * n.distance:
                good_points.append(m)

        # Define how similar they are
        if len(kp_1) <= len(kp_2):
            number_keypoints = len(kp_1)
        else:
            number_keypoints = len(kp_2)

        print("How good is the match: ", len(good_points) / number_keypoints * 100)
        if (len(good_points) / number_keypoints * 100) >= acceptance_number:

            return Match(True, len(good_points) / number_keypoints * 100)
        else:
            return Match(False, len(good_points) / number_keypoints * 100)
    except:
        if real_original_image is None or real_compare_image is None:
            print("How good is the match: Failed")
            return Match(False, 0)
        else:
            new_original = autocropalt.crop(real_original_image)
            new_original = ReadFolder.resize_with_aspect_ratio(new_original, width=resized_width)
            new_compare_image = autocropalt.crop(real_compare_image)
            new_compare_image = ReadFolder.resize_with_aspect_ratio(new_compare_image, width=resized_width)
            return is_match(new_original, new_compare_image, None, None)


images = ReadFolder.load_images_from_folder(directory_path, width=resized_width)

while len(images) > 0:
    temporaryList = [images[0]]
    original = images[0].processed_img
    print('Photos Left To Compare:' + str(len(images)) + ' (' + str(images[0]) + ')')
    for i in range(len(images)):
        if i is len(images) - 1:
            pass
        else:
            print(str(images[0]) + ' compared with ' + str(images[i + 1]))
            image_to_compare = images[i + 1].processed_img
            match_result = is_match(original, image_to_compare, images[i].img, images[i + 1].img)

            if str(images[0]).split('-')[0] == str(images[i + 1]).split('-')[0]:
                if match_result.isMatch is True:
                    print('True Acceptance')
                    tempfile = [str(images[0]), str(images[i + 1]), match_result.score, "True Acceptance"]
                    new_file.append(tempfile)
                else:
                    print('False Rejection')
                    tempfile = [str(images[0]), str(images[i + 1]), match_result.score, "False Rejection"]
                    new_file.append(tempfile)
            else:
                if match_result.isMatch is True:
                    print('False Acceptance')
                    tempfile = [str(images[0]), str(images[i + 1]), match_result.score, "False Acceptance"]
                    new_file.append(tempfile)
                else:
                    print('True Rejection')
                    tempfile = [str(images[0]), str(images[i + 1]), match_result.score, "True Rejection"]
                    new_file.append(tempfile)

            tempfile = [str(images[0]), str(images[i + 1]), match_result.score]
            new_file.append(tempfile)

    for i in range(len(temporaryList)):
        images.remove(temporaryList[i])

csv_writer = csv.writer(open("output.csv", "w"))
csv_writer.writerow(["Photo_1", "Photo_2", "Sift_Match_Score", "Match_Result_With_Acceptance_" + str(acceptance_number)])
for row in new_file:
    csv_writer.writerow(row)
