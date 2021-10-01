class RenamingDictionary():

    def __init__(self, dict):
        self.dict = dict

    def rename(self):
        new_dict = {}
        for key in self.dict:
            key2 = 'frame_' + str(key)
            new_dict[key2] = self.dict[key]
        return new_dict


class LabelSeparator():

    def __init__(self, mask_dict_new):
        self.mask_dict_new = mask_dict_new

    def createlabellist(self, list_of_labels):

        list_for_every_l = []

        for key in self.mask_dict_new:
            newer_mask_dict = self.mask_dict_new[key]

            for key2 in newer_mask_dict:
                if key2 in list_of_labels:
                    list_for_every_l.append([key, key2, newer_mask_dict[key2]])

        return list_for_every_l


class PolygonSeparator():

    def __init__(self, list_for_every_label):
        self.list_for_every_label = list_for_every_label

    def createpolygonlist(self):

        list_for_every_p = []

        for i in range(len(self.list_for_every_label)):
            coordinates = self.list_for_every_label[i][2]
            for j in range(len(coordinates)):
                list_for_every_p.append([self.list_for_every_label[i][0], self.list_for_every_label[i][1], coordinates[j]])

        return list_for_every_p


class XYSeparator():

    def __init__(self, list_for_every_polygon):
        self.list_for_every_polygon = list_for_every_polygon

    def separatexy(self):
        list_of_o_x_y = []

        for k in range(len(self.list_for_every_polygon)):
            ordered_x_y = reorderingcoordinates(self.list_for_every_polygon[k])
            list_of_o_x_y.append(ordered_x_y)

        return list_of_o_x_y


def reorderingcoordinates(frame):
    list_of_x = []
    list_of_y = []
    coord = frame[2]

    for corner in range(len(coord)):
        list_of_x.append(coord[corner][0])
        list_of_y.append(coord[corner][1])

    return [frame[0], frame[1], list_of_x, list_of_y]


def creating_final_json_dict(json_dict_final, list_of_ordered_x_y):
    for pos in range(len(list_of_ordered_x_y)):
        current_frame = list_of_ordered_x_y[pos][0]
        for key in json_dict_final:
            if key == current_frame:
                polygon_properties = {
                    "shape_attributes": {"name": "polygon", "all_points_x": list_of_ordered_x_y[pos][2],
                                         "all_points_y": list_of_ordered_x_y[pos][3], },
                    "region_attributes": {"label": list_of_ordered_x_y[pos][1]}}
                json_dict_final[key]['regions'].append(polygon_properties)
    return json_dict_final
