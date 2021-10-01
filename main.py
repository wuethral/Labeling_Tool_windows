from tkinter import *
from IPython.display import display, Image
from PIL import Image, ImageTk
import sys
import image_upload as imgupload
import keyboard as keyboard
from create_mask import mask_creation
from list_of_colors import colors
import os, os.path
import glob
from create_json import CreateJsonPolygonLabels
import cv2

canvas = 0
label_buttons = []
rectangle_coordinates_one_label = []
select_area_coordinates_one_label = []
big_global_label_dict_rectangle = {}
big_global_label_dict_select_area = {}
image_list = []
img_nr = 0
start_x = 0
start_y = 0
first_line = True


class TKButtonWrapper:
    def __init__(self, root, which_column, callback_arg, callback, counting, nr_of_labels, w, h, color):
        self.root = root
        self.which_column = which_column
        self.callback_arg = callback_arg
        self.callback = callback
        self.counting = counting
        self.nr_of_labels = nr_of_labels
        self.w = w
        self.h = h
        self.color = color
        self.create_button()

    def create_button(self):
        self.button = Button(self.root, text=self.callback_arg, fg = self.color, state='normal',
                             command=lambda: self.callback(self.root, self.callback_arg,
                                                           self.w, self.h, self.color), width=7,
                             height=int(20 / self.nr_of_labels))
        self.button.grid(column=self.which_column, row=self.counting)


def standard_button_callback(root, lab, w, h, color):

    root.bind('r', lambda x: draw_rectangle_outside(root, lab, color))
    root.bind('s', lambda x: area_selection(root, w, h, lab, color))
    root.bind('d', lambda x: clearing_of_label(root, lab))


    #toggle_label_buttons(lab)

def toggle_label_buttons(lab):
    global label_buttons
    for button_wrapper in label_buttons:
        if button_wrapper.button['text'] == lab:
            button_wrapper.button['fg'] = 'green'
        else:
            button_wrapper.button['fg'] = 'black'




def draw_rectangle_outside(root, lab, color):
    global canvas
    def draw_rectangle(event):
        if event.state == 0:
            canvas.old_cords = event.x, event.y
        if event.state == 256:
            global rectangle_coordinates_one_label
            x, y = event.x, event.y
            x1, y1 = canvas.old_cords
            canvas.create_rectangle(x1, y1, x, y, outline=color,
                                    tags="rect")  # Frage: Spielt Anordnung von x1,y1,x,y eine rolle?

            root.unbind('<ButtonPress-1>')
            root.unbind('<ButtonRelease-1>')

            rectangle_coordinates_one_label = [(x1, y1), (x, y)]
            saving_corner_coordinates('rect', rectangle_coordinates_one_label, lab)

    root.bind('<ButtonPress-1>', draw_rectangle)
    root.bind("<ButtonRelease-1>", draw_rectangle)


def area_selection(root, w, h, lab, color):
    global canvas
    def start_line(event):
        global select_area_coordinates_one_label
        global start_x
        global start_y
        select_area_coordinates_one_label = []
        canvas.old_cords = event.x, event.y
        root.unbind('<ButtonPress-1>')
        start_x = event.x
        start_y = event.y
        select_area_coordinates_one_label.append((start_x, start_y))

    def mouse_move(event):
        canvas.delete('line')
        x_live, y_live = canvas.old_cords
        canvas.create_line(x_live, y_live, event.x, event.y, width=1, fill=color, tags='line')

    def draw_line(event):

        global first_line
        x, y = event.x, event.y
        x1, y1 = canvas.old_cords
        end_x = x
        end_y = y
        distance_end_start = (((end_y - start_y) ** 2) + ((end_x - start_x) ** 2)) ** (1 / 2)
        if distance_end_start < 20 and first_line == False:
            canvas.create_line(x1, y1, x, y, width=1, fill=color)
            canvas.create_line(end_x, end_y, start_x, start_y, width=1,
                               fill=color)  # Frage: Spielt Anordnung von x1,y1,x,y eine rolle?
            root.unbind('<ButtonRelease-1>')
            root.unbind("<B1-Motion>")
            select_area_coordinates_one_label.append((end_x, end_y))

            saving_corner_coordinates('sel_area', select_area_coordinates_one_label, lab)




        else:
            canvas.create_line(x1, y1, x, y, width=1, fill=color)  # Frage: Spielt Anordnung von x1,y1,x,y eine rolle?
            canvas.old_cords = x, y
            first_line = False
            select_area_coordinates_one_label.append((x, y))

    root.bind('<ButtonPress-1>', start_line)
    root.bind("<B1-Motion>", mouse_move)
    root.bind('<ButtonRelease-1>', draw_line)


def saving_corner_coordinates(modus, coordinates, lab):
    global big_global_label_dict_rectangle
    global big_global_label_dict_select_area
    if modus == 'rect':
        if not img_nr in big_global_label_dict_rectangle.keys():
            big_global_label_dict_rectangle[img_nr] = {}
            big_global_label_dict_rectangle[img_nr][lab] = [coordinates]
        elif img_nr in big_global_label_dict_rectangle.keys():
            if not lab in big_global_label_dict_rectangle[img_nr].keys():
                big_global_label_dict_rectangle[img_nr][lab] = [coordinates]
            elif lab in big_global_label_dict_rectangle[img_nr].keys():
                big_global_label_dict_rectangle[img_nr][lab].append(coordinates)
    elif modus == 'sel_area':
        if not img_nr in big_global_label_dict_select_area.keys():

            big_global_label_dict_select_area[img_nr] = {}
            big_global_label_dict_select_area[img_nr][lab] = [coordinates]
        elif img_nr in big_global_label_dict_select_area.keys():

            if not lab in big_global_label_dict_select_area[img_nr].keys():
                big_global_label_dict_select_area[img_nr][lab] = [
                    coordinates]
            elif lab in big_global_label_dict_select_area[img_nr].keys():
                big_global_label_dict_select_area[img_nr][lab].append(
                    coordinates)

def clearing_of_label(root, lab):
    global canvas


    if img_nr in big_global_label_dict_rectangle:
        current_page_rectangle = big_global_label_dict_rectangle[img_nr]
        if lab in current_page_rectangle:
            del big_global_label_dict_rectangle[img_nr][lab]
        else:
            pass
    else:
        pass

    if img_nr in big_global_label_dict_select_area:
        current_page_select_area = big_global_label_dict_select_area[img_nr]
        if lab in current_page_select_area:
            del big_global_label_dict_select_area[img_nr][lab]
        else:
            pass
    else:
        pass


    #print(big_global_label_dict_rectangle)
    #print(big_global_label_dict_select_area)



    displaying_current_image()


def displaying_current_image():
    global canvas
    global label_buttons
    current_color = 0
    canvas = Canvas(sub_root, width=int(1000), height=int(1000))
    canvas.grid(column=0, row=0, rowspan=15)
    canvas.create_image(0, 0, anchor=NW, image=image_list[img_nr])
    if img_nr in big_global_label_dict_rectangle.keys():
        for rect_labels in big_global_label_dict_rectangle[img_nr].keys():
            for button_wrapper in label_buttons:
                if button_wrapper.button['text'] == rect_labels:
                    current_color = button_wrapper.button['fg']
            for rect_coordinates in range(len(big_global_label_dict_rectangle[img_nr][rect_labels])):
                x_one = big_global_label_dict_rectangle[img_nr][rect_labels][rect_coordinates][0][0]
                y_one = big_global_label_dict_rectangle[img_nr][rect_labels][rect_coordinates][0][1]
                x_two = big_global_label_dict_rectangle[img_nr][rect_labels][rect_coordinates][1][0]
                y_two = big_global_label_dict_rectangle[img_nr][rect_labels][rect_coordinates][1][1]
                canvas.create_rectangle(x_one, y_one, x_two, y_two, outline=current_color)

    if img_nr in big_global_label_dict_select_area.keys():
        for select_area_labels in big_global_label_dict_select_area[img_nr].keys():
            for button_wrapper in label_buttons:
                if button_wrapper.button['text'] == select_area_labels:
                    current_color = button_wrapper.button['fg']
            for area_corner_coords in range(len(big_global_label_dict_select_area[img_nr][select_area_labels])):

                for i in range(len(
                        big_global_label_dict_select_area[img_nr][select_area_labels][area_corner_coords]) - 1):
                    corner1 = big_global_label_dict_select_area[img_nr][select_area_labels][area_corner_coords][i]
                    corner2 = big_global_label_dict_select_area[img_nr][select_area_labels][area_corner_coords][
                        i + 1]
                    canvas.create_line(corner1, corner2, width=1, fill=current_color)
                first_corner = big_global_label_dict_select_area[img_nr][select_area_labels][area_corner_coords][
                    0]
                last_corner = big_global_label_dict_select_area[img_nr][select_area_labels][area_corner_coords][
                    -1]
                canvas.create_line(last_corner, first_corner, width=1, fill=current_color)


def next_image(root, sub_root, image_list, labels_we_want, w, h):
    global img_nr
    global label_buttons
    img_nr += 1



    displaying_current_image()

    if img_nr == (len(image_list) - 1):
        # button_next_image = Button(root, text='>>', state=DISABLED,
        #                           command=lambda: next_image(root, image_list, img_nr, w, h))
        # button_next_image.grid(column=2, row=8)
        root.unbind("<Right>")
    else:
        # button_next_image = Button(root, text='>>', command=lambda: next_image(root, image_list, img_nr, w, h))
        # button_next_image.grid(column=2, row=8)
        root.bind("<Right>", lambda x: next_image(root, sub_root, image_list, labels_we_want, w, h))

    if img_nr == 0:
        # button_last_image = Button(root, text='<<', state=DISABLED,
        #                           command=lambda: last_image(root, image_list, img_nr, w, h))
        # button_last_image.grid(column=1, row=8)
        root.unbind("<Left>")
    else:
        # button_last_image = Button(root, text='<<', command=lambda: last_image(root, image_list, img_nr, w, h))
        # button_last_image.grid(column=1, row=8)
        root.bind("<Left>", lambda x: last_image(root, sub_root, image_list, labels_we_want, w, h))

    labeling_image_page = 'Image ' + str(img_nr) + '/' + str(len(image_list) - 1)
    image_nr = Label(sub_root, text=labeling_image_page)
    image_nr.grid(column=4, row=10)
    ''' 
    instruction = Label(root, text='Instructions: \n 1. Select Label '
                                   '\n 2. Press "r" for "Rectangle Label", Press "s" for "Area Selection" '
                                   '\n 3. Press "Right" or "Left" to change image')

    instruction.grid(column=0, row=8)

    count = 0
    label_buttons = []

    for label in labels_we_want:
        label_buttons.append(
            TKButtonWrapper(root, canvas, 1, label, standard_button_callback, count, len(labels_we_want), img_nr, w, h))
        count += 1
    '''

''' 
    count = 0


    for label in labels_we_want:
        label_buttons.append(
            TKButtonWrapper(root, canvas, 2, label, standard_button_callback, count, len(labels_we_want), image_number))
        count += 1

    count_2 = 0

    for label in labels_we_want:
        area_label_buttons.append(TKButtonWrapper(root, canvas, 3, label, standard_button_callback_select_area, count_2, len(labels_we_want), image_number))
        count_2 += 1

    count_3 = 0

    for label in labels_we_want:
        clear_tag = 'clear \n' + label
        clear_label_buttons.append(
            TKButtonWrapper(root, canvas, 4, clear_tag, clear_specific_label, count_3, len(labels_we_want), image_number))
        count_3 += 1

    rectangle_label_button = Button(root, text='Rectangle \n Label', command=lambda: draw_rectangle_outside(root, canvas), width = 7, height =4)
    rectangle_label_button.grid(column=1, row=0)
    #clear_button = Button(root, text='Clear all', command=lambda: delete_all_labels(canvas))
    #clear_button.grid(column=1, row=2)
    area_selection_button = Button(root, text='Select \n Area', command=lambda: area_selection(root, canvas, w, h, image_number), width = 7, height =4)
    area_selection_button.grid(column=1, row=1)
    labeling_image_page = 'Image ' + str(image_number) + '/' + str(len(image_list)-1)
    image_nr = Label(root, text=labeling_image_page)
    image_nr.grid(column=1, row=6)

    print_the_coords_button = Button(root, text = 'print Lab \n coords', command = lambda: print_lab_coords(), width = 7, height = 4)
    print_the_coords_button.grid(column = 1, row = 2)
    specific_clear_button = Button(root, text = 'Clear \n specific', command = lambda: activiate_clearing_buttons(), width = 7, height = 4)
    specific_clear_button.grid(column = 1,row = 3)
    clear_all_button = Button(root, text='Clear \n all', command=lambda: clear_all_labels(root, canvas, image_number),
                              width=7, height=4)
    clear_all_button.grid(column=1, row=7)
'''


def last_image(root, sub_root, image_list, labels_we_want, w, h):
    global img_nr
    img_nr -= 1

    displaying_current_image()

    if img_nr == (len(image_list) - 1):
        # button_next_image = Button(root, text='>>', state=DISABLED,
        #                           command=lambda: next_image(root, image_list, img_nr, w, h))
        # button_next_image.grid(column=2, row=8)
        root.unbind("<Right>")
    else:
        # button_next_image = Button(root, text='>>', command=lambda: next_image(root, image_list, img_nr, w, h))
        # button_next_image.grid(column=2, row=8)
        root.bind("<Right>", lambda x: next_image(root, sub_root, image_list, labels_we_want, w, h))

    if img_nr == 0:
        # button_last_image = Button(root, text='<<', state=DISABLED,
        #                           command=lambda: last_image(root, image_list, img_nr, w, h))
        # button_last_image.grid(column=1, row=8)
        root.unbind("<Left>")
    else:
        # button_last_image = Button(root, text='<<', command=lambda: last_image(root, image_list, img_nr, w, h))
        # button_last_image.grid(column=1, row=8)
        root.bind("<Left>", lambda x: last_image(root, sub_root, image_list, labels_we_want, w, h))

    labeling_image_page = 'Image ' + str(img_nr) + '/' + str(len(image_list) - 1)
    image_nr = Label(sub_root, text=labeling_image_page)
    image_nr.grid(column=4, row=10)
    ''' 
    instruction = Label(root, text='Instructions: \n 1. Select Label '
                                   '\n 2. Press "r" for "Rectangle Label", Press "s" for "Area Selection" '
                                   '\n 3. Press "Right" or "Left" to change image')

    instruction.grid(column=0, row=8)

    count = 0
    label_buttons = []

    for label in labels_we_want:
        label_buttons.append(
            TKButtonWrapper(root, canvas, 1, label, standard_button_callback, count, len(labels_we_want), img_nr, w, h))
        count += 1
    '''
def print_coordinates():
    print('hi')

if __name__ == '__main__':
    root = Tk()
    # imgupload.uploading_images()

    rspan = 15  # rowspan of image
    #o = open('cool')
    #list_of_labels = o.read()
    #list_of_labels = list_of_labels.split('\n')
    #list_of_labels.remove('')
    #list_of_labels.append("hello")
    list_of_labels = ['Car', 'Motorcycle', 'balblalb']

    ''' 
    for i in range(0, 10):  # 900
        image_name = 'frame' + str(i) + '.jpg'
        picture = Image.open(image_name)
        h = picture.height
        w = picture.width
        img = ImageTk.PhotoImage(picture.resize((int(w), int(h))))
        image_list.append(img)
    '''



    path = 'C:/Users/wuethral/Desktop/Labeling_Tool/images'
    for f in os.listdir(path):
        imagePath = os.path.join(path, f)
        if imagePath != path + '\\.DS_Store':
            picture = Image.open(imagePath)
            h = 600 #int(picture.height/5)
            w = 600 #int(picture.width/5)
            img = ImageTk.PhotoImage(picture.resize((w, h)))
            image_list.append(img)
    #print(image_list[1])

    for image in os.listdir('C:/Users/wuethral/Desktop/Labeling_Tool/images'):
        path_to_image = 'C:/Users/wuethral/Desktop/Labeling_Tool/images/' + image
        print(path_to_image)
        if path_to_image != 'C:/Users/wuethral/Desktop/Labeling_Tool/images/.DS_Store':
            img = Image.open(path_to_image)
            resized_image = img.resize((600, 600))
            path_to_resized_image = 'C:/Users/wuethral/Desktop/Labeling_Tool/images_resized/' + image
            resized_image.save(path_to_resized_image)

    print(img.size)  # Output: (1920, 1280)
    print(resized_image.size)  # Output: (400, 400)


    print(image_list)
    sub_root = Frame(root)
    sub_root.grid(column = 0, row = 0, rowspan = rspan)

    canvas = Canvas(sub_root, width=int(1000), height=int(1000))
    canvas.grid(column=0, row=0, rowspan=rspan)
    canvas.create_image(0, 0, anchor=NW, image=image_list[0])
    labeling_image_page = 'Image ' + str(img_nr) + '/' + str(len(image_list) - 1)
    image_nr = Label(sub_root, text=labeling_image_page)


    #instruction = Label(root, text='Instructions: \n 1. Press Label'
    #                               '\n 2. Press "r" for "Rectangle Label", Press "s" for "Area Selection" '
    #                               '\n 3. Press "Right" or "Left" to change image')

    #instruction.grid(column=0, row=8)

    root.bind("<Right>", lambda x: next_image(root, sub_root, image_list, list_of_labels, w, h))

    root.bind("<Left>", lambda x: last_image(root, sub_root, image_list, list_of_labels, w, h))
    root.bind('p', print_coordinates)

    count = 1
    label_title = Label(root, text = 'Labels:')
    label_title.grid(column=1, row=0)

    for label in list_of_labels:
        label_buttons.append(
            TKButtonWrapper(root, 1, label, standard_button_callback, count, len(list_of_labels), w, h, colors[count]))
        count += 1

    create_mask_button = Button(root, text = 'Create Mask', command = lambda: mask_creation(w, h, 10, list_of_labels, big_global_label_dict_select_area))
    create_mask_button.grid(column = 0, row = 8)

    json_creator = CreateJsonPolygonLabels(big_global_label_dict_select_area, list_of_labels)
    create_json_file = Button(root, text = 'Create Json', command = lambda: json_creator.createjson())
    create_json_file.grid(column = 0, row = 9)
    ''' 
    content = Frame(root)
    content.grid(column = 0, row = 1)
    bla = Button(content, text = 'hi', command = lambda: print_coordinates())
    bla.grid(column = 0, row = 0)
    '''
    mainloop()

