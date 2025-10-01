# Created by William Huang (2021) for 
# Utilizing Computer Algorithms to Identify Individual Box Turtles Via Carapace Measurements Research Project
# Modified by Sarah Welsh (2025)

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import glob
import os
from SiftMatcher import SiftMatcher
from GetAllSIFTScores import GetAllSIFTScores
from SiftComparator import SiftComparator
from SiftFindMatch import SiftFindMatch
from SiftCompareFolders import SiftCompareFolders

# initialize the gooey
#gui = Tk()
gui = tb.Window(themename="darkly")
# Gui Dimensions (width, height), centers the window
width = 1000
height = 400
x = (gui.winfo_screenwidth() // 2) - (width // 2)
y = (gui.winfo_screenheight() // 2) - (height // 2)
gui.geometry(f'{width}x{height}+{x}+{y}')
# Gui Name
gui.title("Turtle Shell SIFT Sorter")
page = None

autocrop = None
weights_file_path = ""
cfg_file_path = ""

# A class to hold the information for the original photo, resized image, and image name
class MyImage:
    def __init__(self, img, resized_img, resized_greyscale_img, img_name):
        self.img = img
        self.processed_img = resized_img
        self.resized_greyscale_img = resized_greyscale_img
        self.__name = img_name

    def __str__(self):
        return self.__name


# This is a page that is used to pick the folder that images will taken from
def page1():
    for widget in gui.winfo_children():
        widget.destroy()
    def changepageandsavesiftmode(savedpage):
        global page
        page = savedpage
        ask_if_cropped_or_not_page()


    sift_matcher_button = tb.Button(gui, text="Matcher", width=10, command=lambda: changepageandsavesiftmode(sift_matcher_page))
    sift_matcher_button.grid(row=2, column=1,  pady=10, padx=10)
    sift_matcher_label = Label(gui ,text="Runs through Database folder - sorts pictures into folders and generates SIFT scores")
    sift_matcher_label.grid(row=2,column = 2, sticky="w")

    all_sift_scores_button = tb.Button(gui, text="Only Scores", width=10, command=lambda: changepageandsavesiftmode(all_sift_scores_page))
    all_sift_scores_button.grid(row=3, column=1,  pady=10, padx=10)
    sift_scores_label = Label(gui ,text="Runs through Database folder - only generates SIFT scores")
    sift_scores_label.grid(row=3,column = 2, sticky="w")

    sift_comparator_button = tb.Button(gui, text="Comparator", width=10, command=lambda: changepageandsavesiftmode(sift_comparator_page))
    sift_comparator_button.grid(row=4, column=1,  pady=10, padx=10)
    sift_comparator_label = Label(gui ,text="Compares two images and determines if they are a match")
    sift_comparator_label.grid(row=4,column = 2, sticky="w")

    sift_find_button = tb.Button(gui, text="Find Match", width=10, command=lambda: changepageandsavesiftmode(sift_find_page))
    sift_find_button.grid(row=5, column=1,  pady=10, padx=10)
    sift_find_label = Label(gui ,text="Finds all matches for one image by searching Database folder")
    sift_find_label.grid(row=5,column = 2, sticky="w")

    sift_find_button = tb.Button(gui, text="Compare Folders", width=10, command=lambda: changepageandsavesiftmode(sift_folder_page))
    sift_find_button.grid(row=6, column=1,  pady=10, padx=10)
    sift_find_label = Label(gui ,text="Sorts two Database folders")
    sift_find_label.grid(row=6,column = 2, sticky="w")


def ask_if_cropped_or_not_page():
    for widget in gui.winfo_children():
        widget.destroy()
    def changePage(isautocropped, newpage):
        global autocrop
        autocrop = isautocropped
        newpage()

    auto_crop_button = tb.Button(gui, text="Auto Crop", width=10, command=lambda: changePage(True, ask_how_crop_settings_are_initialized))
    auto_crop_button.grid(row=2, column=1,  pady=10, padx=10)

    use_original_button = tb.Button(gui, text="Use Original", width=10, command=lambda: changePage(False, page))
    use_original_button.grid(row=2, column=2,  pady=10, padx=10)


def ask_how_crop_settings_are_initialized():
    for widget in gui.winfo_children():
        widget.destroy()
    use_settings_folder_button = tb.Button(gui, text="Use Settings Folder", width=20, command=initialize_with_settings_folder_page)
    use_settings_folder_button.grid(row=2, column=1,  pady=10, padx=10)

    import_individual_files_button = tb.Button(gui, text="Import Individual Files", width=20, command=initialize_with_individual_files_page)
    import_individual_files_button.grid(row=2, column=2,  pady=10, padx=10)


def initialize_with_settings_folder_page():
    for widget in gui.winfo_children():
        widget.destroy()

    def getFolderPath():
        folder_selected = filedialog.askdirectory()
        folderPath.set(folder_selected)

    def save_custom_detector_settings_and_move_on():
        global cfg_file_path, weights_file_path
        path_list = glob.glob(folderPath.get() + "/*")
        for file in path_list:
            path = file
            if path.lower().endswith(".cfg"):
                cfg_file_path = path
            elif path.lower().endswith(".weights"):
                weights_file_path = path

        if cfg_file_path == "" or weights_file_path == "":
            messagebox.showerror(title="Error", message="One or More Files Does Not Exist in Settings Folder")
        else:
            page()

    folderPath = StringVar()
    find_folder_label = Label(gui ,text="Find Settings Folder")
    find_folder_label.grid(row=0,column = 0)
    folderpath_entry = Entry(gui,textvariable=folderPath)
    folderpath_entry.grid(row=0,column=1)
    folderpath_entry.focus_set()
    #folderpath_entry.insert(-1, "~/_internal")
    browse_button = tb.Button(gui, text="Browse",command=getFolderPath)
    browse_button.grid(row=0,column=2)
    browse_button = tb.Button(gui, text="Next Page",command=save_custom_detector_settings_and_move_on)
    browse_button.grid(row=1,column=1)

def initialize_with_individual_files_page():
    for widget in gui.winfo_children():
        widget.destroy()
    def getFolderPath(stringvar, file_type, file_extension):
        file_selected = filedialog.askopenfilename(filetypes=[(file_type, file_extension)])
        stringvar.set(file_selected)

    def checkandmoveoniffieldsfilled():
        if weightsfilePath.get() != "" and cfgfilepath.get() != "":
            global weights_file_path, cfg_file_path
            weights_file_path = weightsfilePath.get()
            cfg_file_path = cfgfilepath.get()
            page()
        else:
            messagebox.showerror(title="Error", message="One or More Files Have Not Been Imported")

    weightsfilePath = StringVar()
    find_folder_label = Label(gui ,text="Find weights File")
    find_folder_label.grid(row=0,column = 0)
    weights_folderpath_entry = Entry(gui,textvariable=weightsfilePath)
    weights_folderpath_entry.grid(row=0,column=1)
    weights_folderpath_entry.focus_set()
    weights_browse_button = tb.Button(gui, text="Browse",command=lambda: getFolderPath(weightsfilePath, file_type="weights File", file_extension="*.weights"))
    weights_browse_button.grid(row=0,column=2)

    cfgfilepath = StringVar()
    find_folder_label = Label(gui ,text="Find cfg File")
    find_folder_label.grid(row=1,column = 0)
    cfg_folderpath_entry = Entry(gui,textvariable=cfgfilepath)
    cfg_folderpath_entry.grid(row=1,column=1)
    cfg_browse_button = tb.Button(gui, text="Browse",command=lambda: getFolderPath(cfgfilepath, file_type="cfg File", file_extension="*.cfg"))
    cfg_browse_button.grid(row=1,column=2)

    use_settings_folder_button = tb.Button(gui, text="Next Page", command=checkandmoveoniffieldsfilled)
    use_settings_folder_button.grid(row=2, column=1,  pady=10, padx=10)

def sift_matcher_page():
    global autocrop
    for widget in gui.winfo_children():
        widget.destroy()

    waiting_text = StringVar()
    def getFolderPath(stringvar):
        folder_selected = filedialog.askdirectory()
        stringvar.set(folder_selected)

    def run_sift_matcher():
        if photo_folderpath_entry.get() == "" or save_folderpath_entry.get() == "" or resized_width_entry.get() == "" or \
                distance_coefficient_entry.get == "" or acceptance_number_entry.get() == "" or specimen_name_entry.get() == "":
            messagebox.showerror(title="Error", message="One or More Fields Have Not Been Filled")
        else:
            if len(os.listdir(save_folderpath_entry.get())) == 0:
                    waiting_text.set("Computing/Loading...")

                    # Needs to add wait statement to ensure waiting text UI change
                    gui.after(10, compute_matches)
            else:
                messagebox.showerror(title="Error", message="Select A Save Folder With No Files Present")

    def compute_matches():
        # Initializes the class
        sift_matcher = SiftMatcher(cfg_file_path, weights_file_path, autocrop, int(resized_width_entry.get()),
                                   float(distance_coefficient_entry.get()), float(acceptance_number_entry.get()))
        # Starts matching
        sift_matcher.start_matching(photo_folderpath_entry.get(), save_folderpath_entry.get(),
                                    specimen_name_entry.get())
        #gui.destroy()

    photofolderPath = StringVar()
    find_folder_label = Label(gui ,text="Find Photo Folder")
    find_folder_label.grid(row=0,column = 0)
    photo_folderpath_entry = Entry(gui,textvariable=photofolderPath)
    photo_folderpath_entry.grid(row=0,column=1)
    save_browse_button = tb.Button(gui, text="Browse", command=lambda: getFolderPath(photofolderPath))
    save_browse_button.grid(row=0,column=2)
    photo_folderpath_entry.focus_set()

    savefolderPath = StringVar()
    find_folder_label = Label(gui ,text="Pick Save Folder")
    find_folder_label.grid(row=1,column = 0)
    save_folderpath_entry = Entry(gui,textvariable=savefolderPath)
    save_folderpath_entry.grid(row=1,column=1)
    save_browse_button = tb.Button(gui, text="Browse",command=lambda: getFolderPath(savefolderPath))
    save_browse_button.grid(row=1,column=2)

    enter_label = Label(gui ,text="Enter Resized Width")
    enter_label.grid(row=2,column = 0)
    resized_width_entry = Entry(gui)
    resized_width_entry.grid(row=2,column=1)
    resized_width_entry.insert(-1, "250")

    enter_label = Label(gui ,text="Enter Distance Coefficient")
    enter_label.grid(row=3,column = 0)
    distance_coefficient_entry = Entry(gui)
    distance_coefficient_entry.grid(row=3,column=1)
    distance_coefficient_entry.insert(-1, "0.67")

    enter_label = Label(gui ,text="Enter Acceptance Number")
    enter_label.grid(row=4,column = 0)
    acceptance_number_entry = Entry(gui)
    acceptance_number_entry.grid(row=4,column=1)
    acceptance_number_entry.insert(-1, 4)

    enter_label = Label(gui, text="Enter Specimen Name")
    enter_label.grid(row=5, column=0)
    specimen_name_entry = Entry(gui)
    specimen_name_entry.grid(row=5, column=1)

    run_sift_button = tb.Button(gui, text="Run", width=10, command=run_sift_matcher)
    run_sift_button.grid(row=6, column=1,  pady=10, padx=10)

    loading_indicator_label = Label(gui, textvariable=waiting_text)
    loading_indicator_label.grid(row=6, column=0)

    back_button = tb.Button(gui, text="<- Back", width=10, command=page1)
    back_button.grid(row=7, column=1,  pady=10, padx=10)

def all_sift_scores_page():
    global autocrop
    for widget in gui.winfo_children():
        widget.destroy()

    waiting_text = StringVar()

    def getFolderPath(stringvar):
        folder_selected = filedialog.askdirectory()
        stringvar.set(folder_selected)

    def run_sift_matcher():
        if photo_folderpath_entry.get() == "" or save_folderpath_entry.get() == "" or resized_width_entry.get() == "" or \
                distance_coefficient_entry.get == "" or acceptance_number_entry.get() == "":
            messagebox.showerror(title="Error", message="One or More Fields Have Not Been Filled")
        else:
            if len(os.listdir(save_folderpath_entry.get())) == 0:
                waiting_text.set("Computing/Loading...")

                # Needs to add wait statement to ensure waiting text UI change
                gui.after(10, compute_matches)
            else:
                messagebox.showerror(title="Error", message="Select A Save Folder With No Files Present")

    def compute_matches():
        # Initializes the class
        get_all_sift_scores = GetAllSIFTScores(cfg_file_path, weights_file_path, autocrop, int(resized_width_entry.get()),
                                   float(distance_coefficient_entry.get()), float(acceptance_number_entry.get()))
        # Starts applying the SIFT algorithm to all photos in directory
        get_all_sift_scores.start_matching(photo_folderpath_entry.get(), save_folderpath_entry.get())

        #gui.destroy()

    photofolderPath = StringVar()
    find_folder_label = Label(gui, text="Find Photo Folder")
    find_folder_label.grid(row=0, column=0)
    photo_folderpath_entry = Entry(gui, textvariable=photofolderPath)
    photo_folderpath_entry.grid(row=0, column=1)
    photo_folderpath_entry.focus_set()
    save_browse_button = tb.Button(gui, text="Browse", command=lambda: getFolderPath(photofolderPath))
    save_browse_button.grid(row=0, column=2)

    savefolderPath = StringVar()
    find_folder_label = Label(gui, text="Pick Save Folder")
    find_folder_label.grid(row=1, column=0)
    save_folderpath_entry = Entry(gui, textvariable=savefolderPath)
    save_folderpath_entry.grid(row=1, column=1)
    save_browse_button = tb.Button(gui, text="Browse", command=lambda: getFolderPath(savefolderPath))
    save_browse_button.grid(row=1, column=2)

    enter_label = Label(gui, text="Enter Resized Width")
    enter_label.grid(row=2, column=0)
    resized_width_entry = Entry(gui)
    resized_width_entry.grid(row=2, column=1)
    resized_width_entry.insert(-1, "250")

    enter_label = Label(gui, text="Enter Distance Coefficient")
    enter_label.grid(row=3, column=0)
    distance_coefficient_entry = Entry(gui)
    distance_coefficient_entry.grid(row=3, column=1)
    distance_coefficient_entry.insert(-1, "0.67")

    enter_label = Label(gui, text="Enter Acceptance Number")
    enter_label.grid(row=4, column=0)
    acceptance_number_entry = Entry(gui)
    acceptance_number_entry.grid(row=4, column=1)
    acceptance_number_entry.insert(-1, 4)

    run_sift_button = tb.Button(gui, text="Run", width=10, command=run_sift_matcher)
    run_sift_button.grid(row=6, column=1, pady=10, padx=10)

    loading_indicator_label = Label(gui, textvariable=waiting_text)
    loading_indicator_label.grid(row=6, column=0)

    back_button = tb.Button(gui, text="<- Back", width=10, command=page1)
    back_button.grid(row=7, column=1,  pady=10, padx=10)


def sift_comparator_page():
    global autocrop
    for widget in gui.winfo_children():
        widget.destroy()

    waiting_text = StringVar()

    def getFolderPath(stringvar):
        file_selected = filedialog.askopenfile()
        stringvar.set(file_selected.name)

    def run_sift_matcher():
        if first_photo_path_entry.get() == "" or second_photo_path_entry.get() == "" or resized_width_entry.get() == "" or \
                distance_coefficient_entry.get == "":
            messagebox.showerror(title="Error", message="One or More Fields Have Not Been Filled")
        else:
                # Change waiting text to inform user that things are loading
                waiting_text.set("Computing/Loading...")

                # Needs to add wait statement to ensure waiting text UI change
                gui.after(10, compute_matches)

    def compute_matches():
        # # Initializes the class
        sift_tester = SiftComparator(cfg_file_path, weights_file_path, autocrop, int(resized_width_entry.get()), float(distance_coefficient_entry.get()))
        # Starts Comparing two photos. Will output results in a screen to show you how SIFT is working.
        sift_tester.start_matching(first_photo_path_entry.get(), second_photo_path_entry.get())

        #gui.destroy()

    firstimagepath = StringVar()
    find_folder_label = Label(gui, text="Pick First Image")
    find_folder_label.grid(row=0, column=0)
    first_photo_path_entry = Entry(gui, textvariable=firstimagepath)
    first_photo_path_entry.grid(row=0, column=1)
    first_photo_path_entry.focus_set()
    save_browse_button = tb.Button(gui, text="Browse", command=lambda: getFolderPath(firstimagepath))
    save_browse_button.grid(row=0, column=2)

    secondimagepath = StringVar()
    find_folder_label = Label(gui, text="Pick Second Image")
    find_folder_label.grid(row=1, column=0)
    second_photo_path_entry = Entry(gui, textvariable=secondimagepath)
    second_photo_path_entry.grid(row=1, column=1)
    save_browse_button = tb.Button(gui, text="Browse", command=lambda: getFolderPath(secondimagepath))
    save_browse_button.grid(row=1, column=2)

    enter_label = Label(gui, text="Enter Resized Width")
    enter_label.grid(row=2, column=0)
    resized_width_entry = Entry(gui)
    resized_width_entry.grid(row=2, column=1)
    resized_width_entry.insert(-1, "250")

    enter_label = Label(gui, text="Enter Distance Coefficient")
    enter_label.grid(row=3, column=0)
    distance_coefficient_entry = Entry(gui)
    distance_coefficient_entry.grid(row=3, column=1)
    distance_coefficient_entry.insert(-1, "0.67")

    run_sift_button = tb.Button(gui, text="Run", width=10, command=run_sift_matcher)
    run_sift_button.grid(row=6, column=1, pady=10, padx=10)

    loading_indicator_label = Label(gui, textvariable=waiting_text)
    loading_indicator_label.grid(row=6, column=0)

    back_button = tb.Button(gui, text="<- Back", width=10, command=page1)
    back_button.grid(row=7, column=1,  pady=10, padx=10)





def sift_find_page():
    global autocrop
    for widget in gui.winfo_children():
        widget.destroy()

    waiting_text = StringVar()

    def getImagePath(stringvar):
        file_selected = filedialog.askopenfile()
        stringvar.set(file_selected.name)
    
    def getFolderPath(stringvar):
        folder_selected = filedialog.askdirectory()
        stringvar.set(folder_selected)

    def run_sift_matcher():
        if first_photo_path_entry.get() == "" or photo_folderpath_entry.get() == "" or resized_width_entry.get() == "" or \
                distance_coefficient_entry.get == "":
            messagebox.showerror(title="Error", message="One or More Fields Have Not Been Filled")
        else:
                # Change waiting text to inform user that things are loading
                waiting_text.set("Computing/Loading...")

                # Needs to add wait statement to ensure waiting text UI change
                gui.after(10, compute_matches)

    def compute_matches():
        # # Initializes the class
        sift_tester = SiftFindMatch(cfg_file_path, weights_file_path, autocrop, int(resized_width_entry.get()), float(distance_coefficient_entry.get()), float(acceptance_number_entry.get()))
        # Starts Comparing two photos. Will output results in a screen to show you how SIFT is working.
        sift_tester.start_matching(first_photo_path_entry.get(), photo_folderpath_entry.get())

        #gui.destroy()

    firstimagepath = StringVar()
    find_folder_label = Label(gui, text="Pick First Image")
    find_folder_label.grid(row=0, column=0)
    first_photo_path_entry = Entry(gui, textvariable=firstimagepath)
    first_photo_path_entry.grid(row=0, column=1)
    first_photo_path_entry.focus_set()
    save_browse_button = tb.Button(gui, text="Browse", command=lambda: getImagePath(firstimagepath))
    save_browse_button.grid(row=0, column=2)

    photofolderPath = StringVar()
    find_folder_label = Label(gui, text="Pick Database Folder")
    find_folder_label.grid(row=1, column=0)
    photo_folderpath_entry = Entry(gui, textvariable=photofolderPath)
    photo_folderpath_entry.grid(row=1, column=1)
    save_browse_button = tb.Button(gui, text="Browse", command=lambda: getFolderPath(photofolderPath))
    save_browse_button.grid(row=1, column=2)


    enter_label = Label(gui, text="Enter Resized Width")
    enter_label.grid(row=3, column=0)
    resized_width_entry = Entry(gui)
    resized_width_entry.grid(row=3, column=1)
    resized_width_entry.insert(-1, "250")

    enter_label = Label(gui, text="Enter Distance Coefficient")
    enter_label.grid(row=4, column=0)
    distance_coefficient_entry = Entry(gui)
    distance_coefficient_entry.grid(row=4, column=1)
    distance_coefficient_entry.insert(-1, "0.67")

    enter_label = Label(gui, text="Enter Acceptance Number")
    enter_label.grid(row=5, column=0)
    acceptance_number_entry = Entry(gui)
    acceptance_number_entry.grid(row=5, column=1)
    acceptance_number_entry.insert(-1, 4)

    run_sift_button = tb.Button(gui, text="Run", width=10, command=run_sift_matcher)
    run_sift_button.grid(row=6, column=1, pady=10, padx=10)

    loading_indicator_label = Label(gui, textvariable=waiting_text)
    loading_indicator_label.grid(row=6, column=0)

    back_button = tb.Button(gui, text="<- Back", width=10, command=page1)
    back_button.grid(row=7, column=1,  pady=10, padx=10)





def sift_folder_page():
    global autocrop
    for widget in gui.winfo_children():
        widget.destroy()

    waiting_text = StringVar()

    def getFolderPath(stringvar):
        folder_selected = filedialog.askdirectory()
        stringvar.set(folder_selected)

    def run_sift_matcher():
        if first_folder_path_entry.get() == "" or second_folder_path_entry.get() == "" or resized_width_entry.get() == "" or \
                distance_coefficient_entry.get == "" or save_folderpath_entry.get() == "" or specimen_name_entry.get() == "":
            messagebox.showerror(title="Error", message="One or More Fields Have Not Been Filled")
        else:
                # Change waiting text to inform user that things are loading
                waiting_text.set("Computing/Loading...")

                # Needs to add wait statement to ensure waiting text UI change
                gui.after(10, compute_matches)

    def compute_matches():
        # # Initializes the class
        sift_tester = SiftCompareFolders(cfg_file_path, weights_file_path, autocrop, int(resized_width_entry.get()), float(distance_coefficient_entry.get()))
        # Starts Comparing two photos. Will output results in a screen to show you how SIFT is working.
        sift_tester.start_matching(first_folder_path_entry.get(), second_folder_path_entry.get(), save_folderpath_entry.get(), specimen_name_entry.get())

        #gui.destroy()

    firstpath = StringVar()
    find_folder_label = Label(gui, text="Pick First Folder")
    find_folder_label.grid(row=0, column=0)
    first_folder_path_entry = Entry(gui, textvariable=firstpath)
    first_folder_path_entry.grid(row=0, column=1)
    first_folder_path_entry.focus_set()
    save_browse_button = tb.Button(gui, text="Browse", command=lambda: getFolderPath(firstpath))
    save_browse_button.grid(row=0, column=2)

    secondpath = StringVar()
    find_folder_label = Label(gui, text="Pick Second Folder")
    find_folder_label.grid(row=1, column=0)
    second_folder_path_entry = Entry(gui, textvariable=secondpath)
    second_folder_path_entry.grid(row=1, column=1)
    save_browse_button = tb.Button(gui, text="Browse", command=lambda: getFolderPath(secondpath))
    save_browse_button.grid(row=1, column=2)

    enter_label = Label(gui, text="Enter Resized Width")
    enter_label.grid(row=2, column=0)
    resized_width_entry = Entry(gui)
    resized_width_entry.grid(row=2, column=1)
    resized_width_entry.insert(-1, "250")

    enter_label = Label(gui, text="Enter Distance Coefficient")
    enter_label.grid(row=3, column=0)
    distance_coefficient_entry = Entry(gui)
    distance_coefficient_entry.grid(row=3, column=1)
    distance_coefficient_entry.insert(-1, "0.67")

    savefolderPath = StringVar()
    find_folder_label = Label(gui ,text="Pick Save Folder")
    find_folder_label.grid(row=4,column = 0)
    save_folderpath_entry = Entry(gui,textvariable=savefolderPath)
    save_folderpath_entry.grid(row=4,column=1)
    save_browse_button = tb.Button(gui, text="Browse",command=lambda: getFolderPath(savefolderPath))
    save_browse_button.grid(row=4,column=2)

    enter_label = Label(gui, text="Enter Specimen Name")
    enter_label.grid(row=5, column=0)
    specimen_name_entry = Entry(gui)
    specimen_name_entry.grid(row=5, column=1)

    run_sift_button = tb.Button(gui, text="Run", width=10, command=run_sift_matcher)
    run_sift_button.grid(row=7, column=1, pady=10, padx=10)

    loading_indicator_label = Label(gui, textvariable=waiting_text)
    loading_indicator_label.grid(row=6, column=0)

    back_button = tb.Button(gui, text="<- Back", width=10, command=page1)
    back_button.grid(row=8, column=1,  pady=10, padx=10)




page1()
gui.mainloop()