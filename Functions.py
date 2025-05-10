import os
import shutil
import zipfile
import logging
from lxml import etree as ET
from libretranslatepy import LibreTranslateAPI

# Base directories
UPLOAD_DIR = "./tmp"
TRANSLATED_DIR = "./tmp_translated"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# translate function
def translate(original_text_list, source_language, target_language):
    lt = LibreTranslateAPI("https://localhost:5000/")

    translated_list = []
    total = len(original_text_list)
    for idx, element in enumerate(original_text_list, start=1):
        try:
            translated_element = lt.translate(element, source_language, target_language)
            translated_list.append(translated_element)
            logger.info(f"Translated {idx}/{total}")
        except Exception as e:
            logger.error(f"Error translating element {idx}: {e}")
            raise
    return translated_list

# document functions
# unzip docx to xml
def unzip_docx(docx_file, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with zipfile.ZipFile(docx_file, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

# get text from unzipped xml
def extract_text_from_docx(xml_file):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(xml_file, parser)
    root = tree.getroot()
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    text_elements = root.xpath('//w:t', namespaces=namespaces)
    original_text_list = [elem.text for elem in text_elements]
    return original_text_list, tree

# replace text in xml after translation
def replace_text_in_xml(original_list, translated_list, tree, xml_file):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    root = tree.getroot()
    text_elements = root.xpath('//w:t', namespaces=ns)
    for node, new_text in zip(text_elements, translated_list):
        node.text = new_text
    os.makedirs(os.path.dirname(xml_file), exist_ok=True)
    tree.write(xml_file, xml_declaration=True, encoding='UTF-8', standalone=True)

# rezip xml to docx
def repackage_docx(folder_to_zip, output_docx):
    with zipfile.ZipFile(output_docx, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
        for root_dir, dirs, files in os.walk(folder_to_zip):
            for file in files:
                file_path = os.path.join(root_dir, file)
                arcname = os.path.relpath(file_path, folder_to_zip)
                docx_zip.write(file_path, arcname)

# clean temp folder
def clean_temp_folder(folder=UPLOAD_DIR):
    try:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    except Exception as e:
        logger.error(f"Error cleaning {folder}: {e}")

# operation function
def full_operation(filepath, source_language, target_language):
    path = os.path.splitext(filepath)[0]
    outputfolder = f"{path}_xml"
    
    try:
        unzip_docx(filepath, outputfolder)
        
        xml_text_file = f"{outputfolder}/word/document.xml"
        
        original_text_list, tree = extract_text_from_docx(xml_text_file)
        translated_text_list = translate(original_text_list, source_language, target_language)
        
        replace_text_in_xml(original_text_list, translated_text_list, tree, xml_text_file)
        
        filename = path.split('/')[-1]
        translated_path = f"{TRANSLATED_DIR}/{filename}_translated.docx"
        repackage_docx(outputfolder, translated_path)

        clean_temp_folder(UPLOAD_DIR)
        
        return translated_path
    
    except Exception as e:
        
        logger.error(f"Full operation failed: {e}")
        raise
