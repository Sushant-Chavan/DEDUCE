'''
This script extracts and restructures the places365 dataset from the tar file.
'''

import os
import copy
import re
import errno
import shutil
import tarfile
import numpy as np

from config import places_dir

env_types = ['home', 'office']

def parse_desired_labels():
    labels = {}

    for env in env_types:
        with open('categories_places365_{}.txt'.format(env)) as label_data:
            labels[env] = [line.split()[0].split('/')[-1] for line in label_data]
    return labels

def create_dataset_directories(desired_labels):
    for env in env_types:
        training_path = os.path.join(places_dir, 'Places365', env, 'train')
        val_path = os.path.join(places_dir, 'Places365', 'val')
        for label in desired_labels[env]:
            # Create training directories
            train_label_dir_path = os.path.join(training_path, label)
            if os.path.isdir(train_label_dir_path):
                print('Remove existing train dataset directory:', train_label_dir_path)
                shutil.rmtree(train_label_dir_path)
            os.makedirs(train_label_dir_path)

            # Create evaluation directories
            val_label_dir_path = os.path.join(val_path, label)
            if os.path.isdir(val_label_dir_path):
                print('Remove existing val dataset directory:', val_label_dir_path)
                shutil.rmtree(val_label_dir_path)
            os.makedirs(val_label_dir_path)

def extraction_path(env, label, is_train_label=True):
    return os.path.join(places_dir, 'Places365', env, 'train', label) \
        if is_train_label else os.path.join(places_dir, 'Places365', 'val', label)

def extract_desired_places(desired_labels):
    tar_file_path = os.path.join(places_dir, 'places365standard_easyformat.tar')
    tar = tarfile.open(tar_file_path)
    print("\nOpened tarfile. Extracting members (this will take some time and memory)...")
    members = tar.getmembers()
    print("Member extraction complete")

    print("\nExtracting and building the dataset structure for training and evaluation...")
    for member in tar.getmembers():
        if member.isreg():
            class_name = str(member.name).split('/')[-2]
            if '/train/' in member.name:
                member.name = os.path.basename(member.name) # remove relative path
                for env in env_types:
                    if class_name in desired_labels[env]:
                        tar.extract(member, extraction_path(env, class_name))
            elif '/val/' in member.name:
                member.name = os.path.basename(member.name)
                for env in env_types:
                    if class_name in desired_labels[env]:
                        tar.extract(member, extraction_path(env, class_name, False))
                        break
    print('\nProcessing Places365 dataset complete!')

def main():
    desired_labels = parse_desired_labels()
    create_dataset_directories(desired_labels)
    extract_desired_places(desired_labels)


if __name__ == "__main__":
    main()
