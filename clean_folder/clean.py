from pathlib import Path
import re
import shutil
import sys

# images
jpeg_files = list()
png_files = list()
jpg_files = list()
svg_files = list()
# video
avi_files = list()
mp4_files = list()
mov_files = list()
mkv_files = list()
# documents
doc_files = list()
docx_files = list()
txt_files = list()
pdf_files = list()
xlsx_files = list()
pptx_files = list()
# audio
mp3_files = list()
ogg_files = list()
wav_files = list()
amr_files = list()
# archives
zip_files = list()
gz_files = list()
tar_files = list()
# unknown files
unknown = set()
# All Folders
folders = list()
# Files not have extensions
others = list()
# Extensions of files
extensions = set()

registered_extensions = {
    "JPEG": jpeg_files,
    "PNG": png_files,
    "JPG": jpg_files,
    "SVG": svg_files,
    "AVI": avi_files,
    "MP4": mp4_files,
    "MOV": mov_files,
    "MKV": mkv_files,
    "DOC": doc_files,
    "DOCX": docx_files,
    "TXT": txt_files,
    "PDF": pdf_files,
    "XLSX": xlsx_files,
    "PPTX": pptx_files,
    "MP3": mp3_files,
    "OGG": ogg_files,
    "WAV": wav_files,
    "AMR": amr_files,
    "ZIP": zip_files,
    "GZ": gz_files,
    "TAR": tar_files
}

UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()


def normalize(name):
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', "_", new_name)
    return f"{new_name}.{'.'.join(extension)}"


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ("images", "video", "documents", "audio", "archives", "unknown"):
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                container.append(new_name)
            except KeyError:
                unknown.add(extension)
                others.append(new_name)


def handle_file(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))


def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name)
    if new_name.endswith('.zip'):
        new_name = new_name.replace('.zip', '')

    if new_name.endswith('tar.gz'):
        new_name = new_name.replace('tar.gz', '')
        
    if new_name.endswith('.gz'):
        new_name = new_name.replace('.gz', '')
        
    if new_name.endswith('.tar'):
        new_name = new_name.replace('.tar', '')

    archive_folder = root_folder / dist / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def get_folder_objects(root_path):
    for folder in root_path.iterdir():
        if folder.is_dir():
            remove_empty_folders(folder)
            try:
                folder.rmdir()
            except OSError:
                pass


def sorting_files(folder_path):
    scan(folder_path)

    for file in jpeg_files:
        handle_file(file, folder_path, "images")
    
    for file in png_files:
        handle_file(file, folder_path, "images")

    for file in jpg_files:
        handle_file(file, folder_path, "images")

    for file in svg_files:
        handle_file(file, folder_path, "images")
    
    for file in avi_files:
        handle_file(file, folder_path, "video")

    for file in mp4_files:
        handle_file(file, folder_path, "video")

    for file in mov_files:
        handle_file(file, folder_path, "video")

    for file in mkv_files:
        handle_file(file, folder_path, "video")

    for file in doc_files:
        handle_file(file, folder_path, "documents")

    for file in docx_files:
        handle_file(file, folder_path, "documents")

    for file in txt_files:
        handle_file(file, folder_path, "documents")

    for file in pdf_files:
        handle_file(file, folder_path, "documents")

    for file in xlsx_files:
        handle_file(file, folder_path, "documents")

    for file in pptx_files:
        handle_file(file, folder_path, "documents")

    for file in mp3_files:
        handle_file(file, folder_path, "audio")

    for file in ogg_files:
        handle_file(file, folder_path, "audio")

    for file in wav_files:
        handle_file(file, folder_path, "audio")

    for file in amr_files:
        handle_file(file, folder_path, "audio")

    for file in zip_files:
        handle_archive(file, folder_path, "archives")

    for file in gz_files:
        handle_archive(file, folder_path, "archives")

    for file in tar_files:
        handle_archive(file, folder_path, "archives")
    
    for file in unknown:
        handle_archive(file, folder_path, "unknown")

    get_folder_objects(folder_path)


def main():
    path = sys.argv[1]
    print(f"Start in {path}")
    arg = Path(path)
    sorting_files(arg.resolve())

if __name__ == '__main__':
    main()