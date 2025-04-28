import os,shutil,zipfile
from lxml import etree as ET
from libretranslatepy import LibreTranslateAPI

# Definitions to stay safe
UPLOAD_DIR = "/app/tmp"
TRANSLATED_DIR = "/app/tmp_translated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSLATED_DIR, exist_ok=True)

# translate function
def translate(original_text_list, source_language, target_language):
    lt_url = os.getenv("LIBRETRANSLATE_URL", "http://localhost:5000")
    lt = LibreTranslateAPI(lt_url)

    translated_list = []
    for idx, element in enumerate(original_text_list, start=1):
        translated_element = lt.translate(element, source_language, target_language)
        translated_list.append(translated_element)
        print(f'translation {idx}/{len(original_text_list)}', end='\r')
    return translated_list


# document functions
# unzip docx to xml
def unzip_docx(docx_file, output_folder):
    # Make sure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Unzip the DOCX file without renaming
    with zipfile.ZipFile(docx_file, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    

# get text from unzipped xml 
def extract_text_from_docx(xml_file):
    # Create an XML parser
    parser = ET.XMLParser(remove_blank_text=True)

    # Parse the document.xml file using lxml with the parser
    tree = ET.parse(xml_file, parser)
    root = tree.getroot()

    # Define the WordprocessingML namespace
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    # Extract text from each XML element (w:t stores text in DOCX)
    text_elements = root.xpath('//w:t', namespaces=namespaces)
    original_text_list = [elem.text for elem in text_elements]

    # Return the original text list and the parsed XML tree
    return original_text_list, tree

# replace text in xml after translation
def replace_text_in_xml(original_list, translated_list, tree, xml_file):
    # namespace
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    root = tree.getroot()

    # Extract text elements in the same order as original_list
    text_elements = root.xpath('//w:t', namespaces=ns)

    # Replace each node's text 
    for node, new_text in zip(text_elements, translated_list):
        node.text = new_text

    # Save modified XML 
    os.makedirs(os.path.dirname(xml_file), exist_ok=True)
    tree.write(xml_file, xml_declaration=True, encoding='UTF-8', standalone=True)

# rezip xml to docx
def repackage_docx(folder_to_zip, output_docx):
    # Create zip file
    with zipfile.ZipFile(output_docx, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
        # Walk through folder structure
        for root, dirs, files in os.walk(folder_to_zip):
            for file in files:
                # Create correct relative path
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_to_zip)
                docx_zip.write(file_path, arcname)

# clean temp folder
def clean_temp_folder(folder=UPLOAD_DIR):
    try:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    except Exception as e:
        print(f"Error cleaning {folder}: {str(e)}")


# operation function 
def full_operation(filepath,source_language,target_language):
    # Unzip docx 
    path = filepath.split('.')[0] # get path without .docx
    outputfolder = f"{path}_xml"
    unzip_docx(filepath,outputfolder)

    # Extract text
    xml_text_file = f"{outputfolder}/word/document.xml"
    original_text_list, tree = extract_text_from_docx(xml_text_file)

    # Translate text 
    translated_text_list = translate(original_text_list,source_language,target_language)

    # Reinsert text
    replace_text_in_xml(original_text_list, translated_text_list, tree, xml_text_file)

    # Repackage docx 
    filename = path.split('/')[-1]
    translated_path = f"{TRANSLATED_DIR}/{filename}_translated.docx"
    repackage_docx(outputfolder,translated_path) 
    
    # Clean up /tmp
    clean_temp_folder()
    return translated_path
