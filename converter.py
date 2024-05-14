import os
from pdf2image import convert_from_path
import easyocr

PATH = os.path.dirname(os.path.abspath(__file__))

def pdf_to_images(pdf_path: str):
    try:
        with open(pdf_path, 'rb') as f:
            pages = convert_from_path(pdf_path)
            for count, page in enumerate(pages):
                page.save(f'out{count}.jpg', 'JPEG')
    except IOError as e:
        print('Could not open pdf file')
        print(e)

def docx_to_images(docx_path: str):
    pass

def find_images(folder_path: str):
    image_path_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.jpg'):
                image_path_list.append(os.path.join(root, file))
    return image_path_list
def ocr_to_text(image_path_list: list):
    languages = ['ru', 'en']
    reader = easyocr.Reader(languages, gpu=False)
    
    image_path_list = find_images(PATH + 'images/')

    extracted_text_list = []
    for image in image_path_list:
        extracted_text_list.append(reader.readtext(image, detail=0))
    
    with open(PATH + 'tmp/' + 'result.txt', 'w') as res_txt:
        for i in range(len(extracted_text_list)):
            res_txt.write('Contents of page '+ str(i) + ': \n')
            res_txt.write(extracted_text_list[i])
    res_txt.close()



