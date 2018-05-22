from multiprocessing.dummy import Pool
import sys, os
import fnmatch
from ocrpdf import OCRPDF

if __name__ == '__main__':
    """ OCR a directory of PDFs with 2 Threads. Program argument is directory"""
    
    input_dir = sys.argv[1]

    if os.path.exists(input_dir) and os.path.isdir(input_dir):
        file_list = []
        
        # get a list of all the pdf files in the given directory
        for file in os.listdir(input_dir):
            if fnmatch.fnmatch(file, '*.pdf'):
                file_path = os.path.join(os.path.dirname(input_dir), file)
                # only append file to list if we don't already have a .json of it
                file_json = file_path.replace('.pdf', '.json')
                if not os.path.isfile(file_json):
                    file_list.append(file_path)

        # not guaranteed to be in alphabetical order from os.listdir() so sort list
        file_list.sort()

        print(len(file_list), 'files to OCR in directory')

        # actually uses 2 threads for small speed boost, not processes
        pool = Pool(processes=2)
        pool.map(OCRPDF, file_list)

        print('Done')

    else:
        print('error with input dir')