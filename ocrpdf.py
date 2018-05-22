import argparse
import io
import os
import sys
import fnmatch
import subprocess
import ujson as json
from enum import Enum
from google.cloud import vision
from google.cloud.vision import types
import shutil

# Instantiates a Google Cloud Vision client. Requires environment variable cedentials set.
client = vision.ImageAnnotatorClient()

class BreakType(Enum):
    """ Google's Enum for detected breaks in symbol.property.detected_break """
    UNKNOWN = 0
    SPACE = 1
    SURE_SPACE = 2 # IS_PREFIX_FIELD_NUMBER 2
    EOL_SURE_SPACE = 3
    HYPHEN = 4
    LINE_BREAK = 5

def pdf_to_images(pdf_filename):
    """ Use ImageMagick6 to convert pdf file into list of png image files where each image is a page """
    base_name = os.path.basename(pdf_filename).replace('.pdf', '')
    cmd = "convert -quiet -density 300 %s ./tmp/%s.png" % (pdf_filename, base_name)
    process = subprocess.run(cmd, shell=True)
    #process = subprocess.run(cmd, shell=True, cwd="./")
    pages = []
    for file in os.listdir('./tmp/'):
        if fnmatch.fnmatch(file, '%s*.png' % base_name):
            pages.append('./tmp/' + file)
    # not guaranteed to be in alphabetical order from os.listdir() so sort list
    pages.sort()
    return pages

def OCR_image_to_text_and_dict(filein):
    """ Use Google Cloud Vision to OCR given image file into a text string and dictionary """
    # load the image into memory
    with io.open(filein, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # send image to Google Cloud Vision to perform document text detection
    response = client.document_text_detection(image=image)
    document = response.full_text_annotation
    # document.text contains full text response

    # build the text document with pages, blocks, paragraph heirarchy
    for page in document.pages:
        block_list = []
        for block in page.blocks:
            paragraph_list = []
            for paragraph in block.paragraphs:
                p_text = str()
                for word in paragraph.words:
                    for symbol in word.symbols:
                        p_text += symbol.text
                        # add best guesses for word breaks
                        if symbol.property.detected_break.type == BreakType.SPACE.value:
                            p_text += ' '
                        elif symbol.property.detected_break.type == BreakType.SURE_SPACE.value:
                            p_text += ' '
                        elif symbol.property.detected_break.type == BreakType.EOL_SURE_SPACE.value:
                            p_text += '\n'
                        elif symbol.property.detected_break.type == BreakType.HYPHEN.value:
                            p_text += '-'
                        elif symbol.property.detected_break.type == BreakType.LINE_BREAK.value:
                            p_text += '\n'
                paragraph_list.append(p_text)
            paragraph_dict = { "paragraphs": paragraph_list }
            block_list.append(paragraph_dict)
        block_dict = { "blocks": block_list }

    return document.text, block_dict


def OCRPDF(input_pdf):
    """ OCR a PDF into a text file and json file """

    # convert pdf to a list of images where each is a page
    image_pages = pdf_to_images(input_pdf)

    text_doc = str()
    pages_list = []

    # send each image page to OCR cloud and append document text
    for image_page in image_pages:
        text_page, page_dict = OCR_image_to_text_and_dict(image_page)
        
        text_doc += text_page
        pages_list.append(page_dict)

    doc_dict = { "pages": pages_list }

    # save the marked up document text to a file
    output_text_file = input_pdf.replace('.pdf', '.txt')
    f = open(output_text_file, 'w')
    f.write(text_doc)
    f.close()

    # save the structured dict into a pretty json file
    output_json_file = input_pdf.replace('.pdf', '.json')
    f = open(output_json_file, 'w')
    json.dump(doc_dict, f, indent=2)
    f.close()

    print('Finished', input_pdf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input PDF file to structured text by OCR')
    parser.add_argument('input_pdf', nargs='?', help='Input PDF file')
    args = parser.parse_args()

    OCRPDF(args.input_pdf)

