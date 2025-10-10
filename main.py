import sys
import os
from utils import *

def main():
    if len(sys.argv) < 2:
        print("Required: python main.py <data_folder>")
        sys.exit(1)

    data_dir = os.path.normpath(sys.argv[1])
    print(f"Selected folder: {data_dir}")

    if not os.path.isdir(data_dir):
        print(f"Error: {data_dir} is not a valid folder")
        sys.exit(1)

    '''PARAMETERS'''
    text_to_add = 'dockerguide'

    append_string_2_txt(data_dir, text_to_add)

if __name__ == "__main__":
    main()