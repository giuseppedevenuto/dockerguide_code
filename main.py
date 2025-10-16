import sys
import os
from utils.metrics import *

def main():
    if len(sys.argv) < 2:
        print("Required: python main.py <data_folder>")
        sys.exit(1)

    data_dir = os.path.normpath(sys.argv[1])
    print(f"Selected folder: {data_dir}")

    if not os.path.isdir(data_dir):
        print(f"Error: {data_dir} is not a valid folder")
        sys.exit(1)

    eventPath = data_dir
    '''PARAMETERS'''
    proc = "bipWithChClusters"
    suffix = "ieeg"
    ext = ".fif"
    wdw_length = 2*60           # seconds
    ratio_wdw_overlap = 0.5     # percentage of the wdw_length

    compute_cplv(eventPath, wdw_length, ratio_wdw_overlap, proc, suffix, ext)

if __name__ == "__main__":
    main()