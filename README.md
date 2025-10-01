# SIFT Turtle Carapace Sorter Instructions

This project was started in 2021 by @knightowl247 via https://github.com/knightowl247/Sift-Sorter
It is now being edited and added to here. There are executables compiled using PyInstaller available for download ...


## To Run:
To run the program simply run "SIFT_Gooey.exe" in a command prompt or double click that file in File Explorer. Please be patient with processing times. This should pull up the GUI. Please make sure to also have the command prompt in view, as a lot of the outputs for final results are printed there. Also ensure that the executable remains in the main folder with the _internal folder, this is needed to be able to access all the libraries and other dependencies.


## Important Notes: 
There are 4 modules in this program, the first three being built by William Huang and the last one created by Sarah Welsh (modifying Huang's previous work). 
When you select any of these modules on the main screen there will be a cropping page, asking if you want to use the Auto Crop feature or use the Original Image. Cropping the image has the purpose of helping the program run faster. This makes the images load into the program a bit slower, but increases the speed of the SIFT algorithm. 
If you select the Auto Crop option, there will be another options page to select the "Settings Folder" or individual files. This is referring to the .cfg and .weights files. If you select the settings option, just navigate to the folder those files are saved in (I have included them in the _internal folder). If you select your own files you will have to select the files individually (it is recommended you pick the settings option if you want to autocrop). To skip this hassle, you can just choose to use the Original Image.

> Note the first 3 modules use "True" and "False" descriptors for any Accepted or Rejected matches. This is using the IDs in the image file names to check if the images actually do or don't match each other. I'm assuming this was testing purposes of the project. This True/False aspect was not included in the last module I created, as I didn't feel it made sense given its purpose. 


### Below is a brief description of the 4 modules -

Sift Matcher - This module requires the input of the Database folder of the images, an empty save folder to direct the output files to, and a "Speciman Name" (this is just what the resulting folder groups will be named). When run, the program will compare every image in the database with every other image and determine if they are a match or not. 
If it is an "Accepted" match, the images will be saved into a unique "Speciman Name" folder. The results for all the comparisons are saved in a "SIFT_matcher_output.csv" file. A details file ("SIFT_matcher_details.txt") file is also created highlighting some important stats of the success of the matcher (lowest true acceptance, list of false rejections, etc.)

Sift Scores - This module does the same work as the Matcher, except it does NOT sort and save the images into new folders. It only creates and saves the output csv and details txt files. 

Sift Comparator - This module takes the input of two images and runs the SIFT algorithm on them to determine if they are a match or not. There is no final save file that returns the output. Instead the images are displayed with all the key points marked, with an additional third image mapping all the "good" points together. The final result of this module (accepted or rejected match) is printed with the final "score" in the console. 
> Note you can get the images to close themselves by pressing any key

Sift Find Match - This module takes the input of one image and a Database folder and compares that single image against all the images in the folder. The output of this is printing the total number of matches found and listing the file names of the matches (with the scores they received) in the console. It also displays a combined image of the original picture with the best match found (with all the best points mapped together like in the Comparator).
This module was made specifically to add new pictures the database (which is why I omitted the True/False aspect of it). If no match is found, no comparison image is displayed and there is no list of matches in the console. 

Compare Folders - This module is almost identical to the Matcher module. Instead of sorting through just one folder database, it compares two different databases and finds all the matches between them. It will also produce a results csv file and sort all the matches found for Folder A images with Folder B images.


### Technical Note
There are 3 main variables when using the SIFT algorithm - 
- resized-width: width of the readjusted photo when photos are matched (default = 250)
- distance_coefficient: compares how close relatively in distance one keypoint in a photo is to another (default = 0.67)
- acceptance_number: a number between 0-100 that is a threshold number needed for a match score to deem two pictures a match (default = 4.0)

I have modified the gui to show the defaults recommended by Huang automatically, so no user interaction is needed. If you would like to test the algorithm or try to make it more accurate, these are variables to alter.


> A more detailed explanation of the variables can be found in Huang's original README.md file (in the forked repo).
