from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image
from CustomDetector import CustomDetector
import glob
import os

# initialize the gooey
gui = Tk()
# Gooey Dimensions (width, height)
gui.geometry("1000x600")
# Gooey Name
gui.title("Picture Cropper Tool")
pagenum = 1

cfg_file_path = ""
yolo_weights_path = ""

img_list = []


# A class to hold the information for the original photo, resized image, and image name
class MyImage:
    def __init__(self, img, cropped_img, img_name):
        self.img = img
        self.processed_img = cropped_img
        self.__name = img_name

    def __str__(self):
        return self.__name


def ask_how_crop_settings_are_initialized():
    use_settings_folder_button = Button(gui, text="Use Settings Folder", width=20,  pady=10, padx=10, command=initialize_with_settings_folder_page)
    use_settings_folder_button.grid(row=2, column=1,  pady=10, padx=10)

    import_individual_files_button = Button(gui, text="Import Individual Files", width=20,  pady=10, padx=10, command=initialize_with_individual_files_page)
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
            convertpage()

    folderPath = StringVar()
    find_folder_label = Label(gui ,text="Find Settings Folder")
    find_folder_label.grid(row=0,column = 0)
    folderpath_entry = Entry(gui,textvariable=folderPath)
    folderpath_entry.grid(row=0,column=1)
    browse_button = Button(gui, text="Browse",command=getFolderPath)
    browse_button.grid(row=0,column=2)
    browse_button = Button(gui, text="Next Page",command=save_custom_detector_settings_and_move_on)
    browse_button.grid(row=1,column=0)


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
            convertpage()
        else:
            messagebox.showerror(title="Error", message="One or More Files Have Not Been Imported")

    weightsfilePath = StringVar()
    find_folder_label = Label(gui ,text="Find weights File")
    find_folder_label.grid(row=0,column = 0)
    weights_folderpath_entry = Entry(gui,textvariable=weightsfilePath)
    weights_folderpath_entry.grid(row=0,column=1)
    weights_browse_button = Button(gui, text="Browse",command=lambda: getFolderPath(weightsfilePath, file_type="weights File", file_extension="*.weights"))
    weights_browse_button.grid(row=0,column=2)

    cfgfilepath = StringVar()
    find_folder_label = Label(gui ,text="Find cfg File")
    find_folder_label.grid(row=1,column = 0)
    cfg_folderpath_entry = Entry(gui,textvariable=cfgfilepath)
    cfg_folderpath_entry.grid(row=1,column=1)
    cfg_browse_button = Button(gui, text="Browse",command=lambda: getFolderPath(cfgfilepath, file_type="cfg File", file_extension="*.cfg"))
    cfg_browse_button.grid(row=1,column=2)

    use_settings_folder_button = Button(gui, text="Next Page", command=checkandmoveoniffieldsfilled)
    use_settings_folder_button.grid(row=2, column=0,  pady=10, padx=10)


# This is a page that is used to pick the folder that images will taken from
def convertpage():
    for widget in gui.winfo_children():
        widget.destroy()

    waiting_text = StringVar()
    waiting_text.set("")

    loading_indicator_label = Label(gui, textvariable=waiting_text)
    loading_indicator_label.grid(row=5, column=0)

    def getFolderPath():
        global folder_path
        folder_selected = filedialog.askdirectory()
        folderPath.set(folder_selected)
        folder_path = folderPath.get() + '/*'

    def convert_and_save():
        print(folder_path.strip())
        if folder_path is None or folder_path.strip() == "":
            messagebox.showerror(title="Error", message="No Folder Selected")
        else:
            waiting_text.set("Loading...")
            # Needs to add wait statement to ensure waiting text UI change
            gui.after(10, load_photo_and_end_program)

    def load_photo_and_end_program():
        # code to save stuff
        folder_selected = filedialog.askdirectory()
        if folder_selected == "":
            waiting_text.set("")
            return

        path_list = glob.glob(folder_path)
        for file in path_list:
            path = file
            head, tail = os.path.split(path)
            print(tail)
            try:
                img = Image.open(path)
                custom_detector = CustomDetector(cfg_file_path, yolo_weights_path)
                new_img = custom_detector.crop(img)
                photo = MyImage(img, new_img, tail)
                img_list.append(photo)
            except:
                None

        for photo in img_list:
            save_path = folder_selected + "/" + str(photo)
            photo.processed_img.save(save_path)
        gui.destroy()

    folderPath = StringVar()
    find_folder_label = Label(gui, text="Find Folder")
    find_folder_label.grid(row=0, column=0)
    folderpath_entry = Entry(gui, textvariable=folderPath)
    folderpath_entry.grid(row=0, column=1)
    browse_button = Button(gui, text="Browse", command=getFolderPath)
    browse_button.grid(row=0, column=2)

    next_page_button = Button(gui, text="Convert", command=convert_and_save)
    next_page_button.grid(row=4, column=0)


ask_how_crop_settings_are_initialized()
gui.mainloop()