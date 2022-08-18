import SiftMatcher as Matcher

resized_width = 250
distance_coefficient = 0.8
acceptance_number = 4
photo_directory_path = "/Users/william6688/Desktop/Turtle Folders/Sample Turtles"
save_directory_path = "NewDatabase"

sift_matcher = Matcher.SiftMatcher(resized_width, distance_coefficient, acceptance_number, photo_directory_path, save_directory_path)
sift_matcher.start_matching()
