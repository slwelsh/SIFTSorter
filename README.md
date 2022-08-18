Before running these files you will need to set up your programming language(python in this case) and coding environment.
For downloading python, just go to the python website (https://www.python.org/) and download python. When downloading python, 
make sure you select add to PATH. This will ensure that the computer terminal can automatically access and use python and its package
manager pip without being in the folder which it is contained and can also sometimes aid coding text editors or IDEs(Integrated Development System) 
to automatically run python as they know its folder location.

Next you want to choose a advanced text editor or IDE to use to read and edit the code. If you are not familiar with coding, I would 
recommend an IDE as it has all the tools necessary to start coding where as text editors usually requires additional plugins 
to do certain stuff like debugging and running code. The IDE I recommend for python is PyCharm(https://www.jetbrains.com/pycharm/download). 

If you are on a government network and you are getting a strange popup every few seconds about some certificate error, follow the instructions in 
this paragraph. Otherwise, you may go to the next paragraph. To fix the error go to the top and select PyCharm < Preferences < Tools < Server Certificates on 
a mac or File < Settings < Tools < Server Certificates on Windows and Linux and select the option "accept all untrusted certificates automatically." Make sure to press
apply and okay. This should fix the error.

Once you download PyCharm, you have to link the python downloaded earlier with the PyCharm so PyCharm can understand and run python code.
To do this, you must go to the top and get to PyCharm < Preferences < Project<project name> < Python Interpreter on a mac or 
File < Settings < Project<project name> < Python Interpreter on Windows and Linux and select the gear button and press add. 
From there you should select System Interpreter instead of Virtualenv Environment. Although Virtualenv Environment can be used, 
it can be inconvenient and confusing as any packages you download will only be applied to that project and if you work on 
another project you may accidentally add a package to the wrong project. In addition, you may need a special command besides "pip 
install <package name>" to download packages from the terminal. After selecting System Interpreter, click the three ellipsis button
and find/enter/drag the path of the python.exe downloaded. Click Ok to get back to the Python Interpreter screen. In the place where 
you can choose a python interpreter, select the python interpreter that you just added. Press Apply and Ok. You should now be set up 
on PyCharm.

Once importing a python project or writing some code, press the run button. Make sure that the path of the file you want to run is properly set. You can check if 
it is properly set if the file you want to run is written to the left of the run button. If not you need to click that and press "edit configurations..." Edit the Script 
Path to the desired file location that you want to run and press apply and okay. 

If you get some error regarding a package not being found, you can install a package by going to PyCharm < Preferences < Project<project name> < Python Interpreter 
on a mac or File < Settings < Project<project name> < Python Interpreter on Windows and Linux and pressing the add button. Search for the package that is needed. 
One thing to keep in mind is that the import statement package name is not necessarily the name of the package. You will have to do a quick google search to find out 
the true package name before installing it. Once you find the package you need, install package and you will be notified if/when the package has been successfully installed.

If there is an issue downloading certain files, especially in a government network, run this command in the command terminal:
"pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package_name>". It is important that you select add to PATH when downloading
python or else the computer will not know what pip is referring to if you are not in the same directory it is contained in.

To run the SIFT Matcher code, you must add the import statement "import SIFTMatcher as Matcher." Once this is done you will need
to create 5 variables: resized_width, distance_coefficient, acceptance_number, photo_directory_path, and save_directory_path.

Resized_width is width of the readjusted photo when photos are matched. The higher the number, the bigger the size of the photo, 
meaning better resolution. The results of this are a longer photo load time and match time due to more data being computed and 
more chances for the SIFT algorithm to find key points. Too high of a number and the SIFT algorithm may pick of background interference 
with longer runtime and too little will result in a shorter runtime but not enough keypoints being found for accurate matching. 
I would recommend starting with 250 and playing with that number to match what best works for you.

The second variable, distance_coefficient, compares how close relatively in distance one keypoint in a photo is to another. 
A high distance_coefficient means more leeway to accept keypoints on different pictures as matches, raising the match score between photos
A low distance_coefficient means the closeness of the keypoints has to be more accurate, likely decreasing the match score 
between photos. I recommend using 0.67 and tweaking it from there.

The variable acceptance_number is a number between 0-100 that is a threshold number needed for a match score to deem two 
pictures a match. A relatively high acceptance_number would require the match score to be really high between two photos, likely rejecting
scores coming from the same specimen in two photos if there is a bit of variation. A relatively low acceptance_number may on the other hand 
accept matches that are not actually matches. I recommend the number 4 as there is likely significant variation between different photos with 
the same specimen and enough differences in photos where there are different specimens that 4 can be considered high.

The string variables photo_directory_path and save_directory_path are just the path of what photos are being matched and 
where matched photos will be.

To use the SiftMatcher, you must initialize the variables mentioned above through a constructor. An example would be 
"sift_matcher = Matcher.SiftMatcher(resized_width, distance_coefficient, acceptance_number, photo_directory_path, save_directory_path)".
If you would like to use the variables that was recommended, you may use a shorter constructor like this: 
"sift_matcher = Matcher.SiftMatcher(photo_directory_path, save_directory_path)" Then you must actually run the function 
that allows the matching to start. To do this, add "sift_matcher.start_matching()". After this you can run the program and look at 
the console to see the results. 

When the program finishes running you will get three new files, a folder containing the photo matches, a csv file (output.csv) containing 
match scores/results, and a text file (details.txt) that states the the value of variables initialized and important information
on the highest match scores for true results, lowest match scores for false results, etc. You should use the text file to tweak
the SiftMatcher program's variables. 



