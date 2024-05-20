import os
from pdf2image import convert_from_path
import easyocr
import sqlite3
import re

PATH = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.dirname(PATH) + os.path.sep + 'db.sqlite3'
TMP_DIR = os.path.dirname(PATH) + os.path.sep + 'downloader' + os.path.sep + 'media' + os.path.sep + 'tmp' + os.path.sep
SAVED_FILES = os.path.dirname(PATH) + os.path.sep + 'downloader' + os.path.sep + 'media' + os.path.sep + 'saved_files' + os.path.sep

class NoFileProvidedException(Exception):
    def __str__(self):
        return 'NoFileProvidedException: No file provided to function'
    pass

def pdf_to_images(pdf_path: str) -> None:
    try:
        with open(pdf_path, 'rb') as f:
            pages = convert_from_path(pdf_path)
            for count, page in enumerate(pages):
                page.save(f'out{count}.jpg', 'JPEG')
    except IOError as e:
        print('Could not open pdf file')
        raise e

def docx_to_images(docx_path: str) -> None:
    pass

def find_images(folder_path: str) -> list:
    image_path_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.jpg'):
                image_path_list.append(os.path.join(root, file))
    return image_path_list

def ocr_to_text(image_path_list: list[str], orig_file_name: str) -> None:
    languages = ['ru', 'en']
    reader = easyocr.Reader(languages, gpu=False)

    extracted_text_list = []
    for image in image_path_list:
        words = reader.readtext(image, detail=0)
        extracted_text_list.append(' '.join(words))

    file_name = orig_file_name.split('.')[0]

    with open(TMP_DIR + f'{file_name}_result.txt', 'w', encoding="utf-8") as res_txt:
        for i in range(len(extracted_text_list)):
            res_txt.write(f'Contents of file \'{orig_file_name}\'' + ': \n')
            res_txt.write('Contents of page '+ str(i + 1) + ': \n')
            print(extracted_text_list[i])
            res_txt.write(extracted_text_list[i])
        res_txt.close()

def file_discoverer(path) -> dict:
    file_path_list = []
    file_count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path_list.append(os.path.join(root, file))
            file_count += 1
    return {'file_path_list': file_path_list, 'file_count': file_count}

# не clean code
def get_file_name(index) -> str | None: # переписать в -> str
    try:
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM downloader_uploadedfiles where id =?', (index,))
            rows = cur.fetchone()
            if rows[1] != None and rows[1] != '':
                return rows[1].split('/')[1]
    except Exception as e:
        raise e

def find_index(obj_name: str) -> str:
    return re.findall('\d+', obj_name)[0]

def ocr_resolver(file_name: str) -> None:
    img_names = []
    orig_file_name = file_name.split(os.path.sep)[-1]
    file_extention = orig_file_name.split('.')[-1]
    match file_extention:
        case 'jpg':
            img_names.append(file_name)
            ocr_caller(img_names, orig_file_name)
        case 'pdf':
            pdf_to_images(file_name)
            img_names = find_images(PATH + 'images/')
            ocr_caller(img_names, orig_file_name)
        case 'docx':
            docx_to_images(file_name)
            img_names = find_images(PATH + 'images/')
            ocr_caller(img_names, orig_file_name)
        case _:
            raise NoFileProvidedException

def file_name_is_latin(file_name: str) -> bool:
    return file_name.isascii()

def conditional_renamer(file_path: str, num: int) -> str:
    new_file_path = os.path.dirname(file_path)
    new_file_name = file_path.split('/')[-1]
    new_file_extention = new_file_name.split('.')[-1]
    new_file_name = new_file_path + os.path.sep + f'file_{num}' + '.' + new_file_extention
    os.rename(file_path, new_file_name)
    return new_file_name

def ocr_caller(img_list: list, orig_file_name) -> None:
    i = 0
    for img in img_list:
        i += 1
        if not file_name_is_latin(img):
            img = conditional_renamer(img, i)
    ocr_to_text(img_list, orig_file_name)

def res_finder(file_name: str) -> str:
    name = file_name.split('.')[0]
    return TMP_DIR + f'{name}_result.txt'

def cleaner() -> None:
    files = os.listdir(TMP_DIR)
    for item in files:
        print(f'Removed: {item}')
        os.remove(TMP_DIR + item)
    files = os.listdir(SAVED_FILES)
    for item in files:
        print(f'Removed: {item}')
        os.remove(SAVED_FILES + item)
    pass
