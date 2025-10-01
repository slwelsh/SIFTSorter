import cv2
import CustomDetector


def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


original = cv2.imread("CarapacePhotos/533-2020-07-15-carapace.JPG")
original = CustomDetector.crop(original)
original = resize_with_aspect_ratio(original, width=400)
image_to_compare = cv2.imread("CarapacePhotos/533-2020-06-24-carapace.JPG")
image_to_compare = CustomDetector.crop(image_to_compare)
image_to_compare = resize_with_aspect_ratio(image_to_compare, width=400)

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
    if m.distance < 0.72 * n.distance:
        good_points.append(m)

# Define how similar they are
number_keypoints = 0
if len(kp_1) <= len(kp_2):
    number_keypoints = len(kp_1)
else:
    number_keypoints = len(kp_2)


print("Keypoints 1ST Image: " + str(len(kp_1)))
print("Keypoints 2ND Image: " + str(len(kp_2)))
print("GOOD Matches:", len(good_points))
print("How good it's the match: ", len(good_points) / number_keypoints * 100)

result = cv2.drawMatches(original, kp_1, image_to_compare, kp_2, good_points, None)


cv2.imshow("result", cv2.resize(result, None, fx=0.4, fy=0.4))
cv2.imwrite("feature_matching.jpg", result)


cv2.imshow("Original", cv2.resize(original, None, fx=0.4, fy=0.4))
cv2.imshow("Duplicate", cv2.resize(image_to_compare, None, fx=0.4, fy=0.4))
cv2.waitKey(0)
cv2.destroyAllWindows()
