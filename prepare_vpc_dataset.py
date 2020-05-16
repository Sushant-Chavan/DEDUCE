'''
This script crawls through the vpc dataset directories and copies the images
from every home/floor directory into respective class directories
/home/floor/class and deletes the rest of the files.
'''

import os
import copy
import re
import errno
import shutil
import zipfile
import numpy as np

from config import vpc_dir

def parse_dataset_labels(labels):
    label_sequences = {}
    label_dict = {}
    with open(labels) as label_data:
        label_sequences = {}
        floor_id = -1
        for line in label_data:
            if '/' in line:
                # Set the current floor id
                floor_id = line.strip().split('/')[0]
                label_sequences[floor_id] = []
                continue
            if '-1' not in line and re.search('[a-zA-Z]', line):
                # extract only those lines that contain an alphabetic label name
                label_sequences[floor_id].append(line.strip())

    for floor_id, label_infos in label_sequences.items():
        # create a new key-value pair for the current floor id
        label_dict[floor_id] = {}
        for l_info in label_infos:
            start, end, label = l_info.split()
            extrapolated_label_ids = np.arange(int(start),
                                               int(end)+1).astype(int).tolist()
            if label in label_dict[floor_id].keys():
                label_dict[floor_id][label].extend(extrapolated_label_ids)
            else:
                label_dict[floor_id][label] = extrapolated_label_ids
    return label_dict

def parse_desired_labels():
    with open('categories_places365_home.txt') as label_data:
        labels = [line.split()[0].split('/')[-1] for line in label_data]
    return labels

def remove_all_directories():
    for name in os.listdir(vpc_dir):
        path = os.path.join(vpc_dir, name)
        if os.path.isdir(path):
            print('Removing existing directory:', path)
            shutil.rmtree(path)

def unzip_files():
    remove_all_directories()
    for name in os.listdir(vpc_dir):
        if 'zip' in name:
            zip_file_path = os.path.join(vpc_dir, name)
            print('Unziping file:', zip_file_path)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(vpc_dir)

def main():
    unzip_files()
    homes = [os.path.join(vpc_dir, home) for home in os.listdir(vpc_dir) 
            if 'Home' in home and os.path.isdir(os.path.join(vpc_dir, home))]
    desired_labels = parse_desired_labels()

    for home in homes:
        home_id = home.split('/')[-1]
        print('\nProcessing', home_id, '...')
        labels = parse_dataset_labels(os.path.join(home, 'label.txt'))
        floors = sorted([floor for floor in os.listdir(home)
                    if os.path.isdir(os.path.join(home, floor))])
        for floor in floors:
            print('  Processing Floor', floor, '...')
            floor_path = os.path.join(home, floor)
            for desired_label in desired_labels:
                if desired_label in labels[floor].keys():
                    print('    Extracting images with the label', desired_label)
                    label_dir = os.path.join(floor_path, str(desired_label))
                    # Create a directory with the current label name
                    if not os.path.exists(label_dir):
                        os.makedirs(label_dir)
                    # Move the relevant images to the label directory
                    for image in labels[floor][desired_label]:
                        src = os.path.join(floor_path, "{0:0=8d}.jpg".format(image))
                        dest = os.path.join(label_dir, "{0:0=8d}.jpg".format(image))
                        if not os.path.isfile(src):
                            raise FileNotFoundError(errno.ENOENT, 
                                                    os.strerror(errno.ENOENT), 
                                                    src)
                        elif not os.path.isfile(dest):
                            shutil.move(src, dest)
            print('  Clearing all the extra images...')
            for image in os.listdir(floor_path):
                image_path = os.path.join(floor_path, image)
                if os.path.isfile(image_path):
                    os.remove(image_path)
        print('  Renaming the home directory')
        parent_dir = os.path.dirname(home)
        os.rename(home, os.path.join(parent_dir, 'data_'+home_id.lower()))
    print('\nProcessing VPC dataset complete!')

if __name__ == "__main__":
    main()
