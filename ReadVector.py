import sys
import re

class Read():
    def __init__(self, fid):
        in_fid = open(fid, "r")
        self.in_file = in_fid.readlines()
        in_fid.close()
        self.scene = {}
        self.read_scene()

    def read_scene(self):
        for line in self.in_file:
            line = line.strip()
            split_line = line.split()
            obj_id = split_line[0]
            feature = split_line[1]
            try:
                self.scene[obj_id][feature] = {}
            except KeyError:
                self.scene[obj_id] = {feature:{}}
            if len(split_line[2:]) == 9:
                for cell in split_line[2:]:
                    split_cell = cell.split(":")
                    self.scene[obj_id][feature][int(split_cell[0])] = split_cell[1]
            else:
                self.scene[obj_id][feature] = split_line[2]
