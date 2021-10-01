import tkinter as tk
from IPython.display import display, Image
from PIL import Image, ImageTk
import sys

line_crossing_counter = 0
list_of_pixel_values = []
mask_number = 1

def create_final_mask(w, h, image_number, label):
    global mask_number
    global list_of_pixel_values
    im = Image.new("RGB", (w, h))
    gray = im.convert('L')
    bw = gray.point(lambda x: 0, '1')
    pix = bw.load()
    pixel_position = 0

    for x in range(w):
        for y in range(h):
            pix[x, y] = list_of_pixel_values[pixel_position]
            pixel_position += 1
    ''' 
    for x in range(w):
        for y in range(h):
            if (x % 2 != 0) and (y % 2 != 0):
                pix[x,y] = 1
            elif (x % 2 == 0) and (y % 2 == 0):
                pix[x,y] = 0
    '''




    name_of_mask = 'mask' + str(mask_number) + '_img_nr_' + str(image_number) + '_label_' + label + '.png'
    mask_number += 1
    bw.save(name_of_mask, "PNG")
    list_of_pixel_values = []








def is_left_or_right(x_coord_pt_1,  y_coord_pt_1,  x_coord_pt_2, y_coord_pt_2, x, y):

    cross_product = (y_coord_pt_2 - y) * (x_coord_pt_2 - x_coord_pt_1) - (x_coord_pt_2 - x) * (y_coord_pt_2 - y_coord_pt_1)
    return cross_product

def check_winding_number_2(coord_pt_1, coord_pt_2, x, y):
    x_coord_pt_1 = coord_pt_1[0]
    y_coord_pt_1 = coord_pt_1[1]
    x_coord_pt_2 = coord_pt_2[0]
    y_coord_pt_2 = coord_pt_2[1]

    if y_coord_pt_1 >= y:
        if y_coord_pt_2 < y:
            if is_left_or_right(x_coord_pt_1,  y_coord_pt_1,  x_coord_pt_2, y_coord_pt_2, x, y) < 0:  # checking if point is on left

                return 1  # if on left, valid upward intersect

            else:
                return 0

        else:
            return 0

    elif y_coord_pt_1 < y:
        if y_coord_pt_2 >= y:
            if is_left_or_right(x_coord_pt_1,  y_coord_pt_1,  x_coord_pt_2, y_coord_pt_2, x, y) > 0: # checking if point is on right

                return -1 # if on right, valid downward intersect
            elif is_left_or_right(x_coord_pt_1, y_coord_pt_1, x_coord_pt_2, y_coord_pt_2, x, y) == 0:
                return 5
            else:
                return 0
        else:
            return 0
    else:

        return 0


    # Checks, if point of interest is on the right or left side of the two corner points
    #on_left_or_right = is_left(x_coord_pt_1, y_coord_pt_1, x_coord_pt_2, y_coord_pt_2, x, y):





def check_winding_number(x, y, coordinates_of_one_label):
    winding = 0
    for coord_pt in range(len(coordinates_of_one_label)-1):
        wind_count = check_winding_number_2(coordinates_of_one_label[coord_pt], coordinates_of_one_label[coord_pt+1],x,y)
        winding += wind_count

    wind_count_2 = check_winding_number_2(coordinates_of_one_label[-1], coordinates_of_one_label[0],x,y)
    winding += wind_count_2
    if winding == 0:
        list_of_pixel_values.append(0)
    else:
        list_of_pixel_values.append(1)


def mask_creation_per_label(w, h, coordinates_of_one_label, image_number, label):


    for x in range(w):
        for y in range(h):
            check_winding_number(x, y, coordinates_of_one_label)

    create_final_mask(w, h, image_number, label)









def mask_creation_per_image(w, h, labels_on_this_image_number, list_of_labels, image_number):
    # We loop through the labels on this image. For each label, we loop through every single mask. We pass the
    # corner coordinates with the image widht and height and image number and label into the mask_creation_per_label
    # function

    for label in list_of_labels:
        if label in labels_on_this_image_number.keys():
            corner_coordinates_of_labels_on_image_number = labels_on_this_image_number[label]
            for coordinates_of_one_label in corner_coordinates_of_labels_on_image_number:
                mask_creation_per_label(w, h, coordinates_of_one_label, image_number, label)



def mask_creation(w, h, number_of_images, list_of_labels, big_global_label_dict_select_area):
    # looping through the single images. We take hold of one image and we call the function mask_creation_per_image
    # where we pass the labels on this page, the list of labels and the image number. also the image width and height
    print(big_global_label_dict_select_area)
    for image_number in range(number_of_images):
        if image_number in big_global_label_dict_select_area.keys():
            labels_on_this_image_number  = big_global_label_dict_select_area[image_number]
            mask_creation_per_image(w, h, labels_on_this_image_number, list_of_labels, image_number)

