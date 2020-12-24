import os
from pathlib import Path
import shutil
import configparser
import yaml
from glob import glob


class Renamer():
    def __init__(self):
        with open("my_config.yaml") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

            self.media_dir = config['Input']['media_dir']
            self.recursive_dir = config['Folder Names to Include in Scan']['RECURSIVE=YES']['type_dir']

            self.create_folder_tags = config['Label tags to move and create folder based on tag name']['tags']
            self.removed_from_folder_file_tags = config['Tags to be removed from folder/files']['tags']

            self.suffix_remove_tags = config['Suffix Deletion remove the last instance of tag and everything after last instance of']['tags']
            self.prefix_remove_tags = config['Prefix Deletion remove first instance of tag and everything before it']['tags']

            self.output_dir = config['Directory to output folder']

            self.copy_or_move = config['Copy or Move']['value']

    def start_clean_up(self):
        for recursive_dir in self.recursive_dir:
            self.clean_up(recursive_dir)

    def clean_up(self, recursive_dir):
        type_dir = recursive_dir

        full_recursive_dir = os.path.join(self.media_dir, recursive_dir)

        for root, dirs, files in os.walk(full_recursive_dir):
            for file in files:

                tag, fbody_re, ext = self.recognize_file_type(file)
                if tag:
                    fbody_re = self.remove_suffix(fbody_re)
                    fbody_re = self.remove_prefix(fbody_re)
                    fbody_re = self.remove_other(fbody_re)

                    file_re = f"{fbody_re}.{ext}"
                    # print(f"{file} ==> {file_re}")
                    root_body = root.replace(full_recursive_dir, '').strip('\\')
                    root_body_split = root_body.split('\\')

                    root_body_split_re = []

                    for seg in root_body_split:
                        seg_re = self.remove_suffix(seg)
                        seg_re = self.remove_prefix(seg_re)
                        seg_re = self.remove_other(seg_re)

                        root_body_split_re.append(seg_re)

                    root_body_re = '\\'.join(root_body_split_re).strip()

                    moved_dir = os.path.join(self.output_dir[tag][type_dir], tag, type_dir, root_body_re)
                    if not os.path.exists(moved_dir):
                        os.makedirs(moved_dir)

                    full_file = os.path.join(root, file)
                    full_file_re = os.path.join(moved_dir, file_re)

                    if self.copy_or_move == 'Copy':
                        if os.path.exists(full_file) and not os.path.exists(full_file_re):
                            shutil.copyfile(full_file, full_file_re)
                    elif self.copy_or_move == 'Move':
                        if os.path.exists(full_file) and not os.path.exists(full_file_re):
                            shutil.move(full_file, full_file_re)

                    print(f"{full_file}\n\t\t\t\t\t ==>\t{full_file_re}")
                    print('\n')

    def recognize_file_type(self, file):
        ext = file.split('.')[-1]
        fbody = ".".join(file.split('.')[:-1])

        fbody_re = fbody

        fbody_split = fbody.split()
        if fbody_split[-1] in self.create_folder_tags:
            tag = fbody_split[-1]
            fbody_re = " ".join(fbody_split[:-1]).strip()
        else:
            tag = None

        return tag, fbody_re, ext

    def remove_suffix(self, file):
        fbody_split = file.split()

        for i in range(len(fbody_split)):
            for tag in self.suffix_remove_tags:
                if tag in fbody_split[-1]:
                    fbody_split = fbody_split[:-1]

        return " ".join(fbody_split).strip()

    def remove_prefix(self, file):
        fbody_split = file.split()

        for i in range(len(fbody_split)):
            for tag in self.prefix_remove_tags:
                if tag in fbody_split[0]:
                    fbody_split = fbody_split[1:]

        return " ".join(fbody_split).strip()

    def remove_other(self, file):
        fbody_split = file.split()

        fbody_split_copy = fbody_split.copy()
        for seg in fbody_split:
            for tag in self.prefix_remove_tags:
                if tag in seg:
                    fbody_split_copy.remove(seg)

        return " ".join(fbody_split_copy).strip()

if __name__ == '__main__':
    app = Renamer()
    app.start_clean_up()
