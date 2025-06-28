import sys
import os
from datetime import datetime
from exif import Image, Flash
from pathlib import Path

IMG_TYPE = { ".jpg", ".jpeg", ".png", ".gif", ".bmp" }
FLASH_ATTR = { "flash_fired", "flash_mode", "flash_return", "flash_function_not_presen", "red_eye_reduction_supported", "reserved" }
META = { "file name", "creation date", "modified date", "last access date" }
USAGE = '''\
-----------------------------------------------------------------------------------------
USAGE: ./scorpion FILE1 [FILE2 ...]
-----------------------------------------------------------------------------------------
Option: 
 • -m        : modify/delete the metadata of a given file as parameter.
-----------------------------------------------------------------------------------------
Supporting the following extensions by default:  [ .jpg / .jpeg / .png / .gif / .bmp ]
-----------------------------------------------------------------------------------------
'''

def main() -> int:
    try:
        if len(sys.argv) <= 1:
            print(USAGE)
            return 1
        if sys.argv[1] == '-m':
            if len(sys.argv) < 3:
                return error("Invalid argument. need file path.", 1)
            try:
                modify_data(Path(sys.argv[2]), os.stat(sys.argv[2]))
            except FileNotFoundError:
                return error(f"[{sys.argv[2]}] is not found.")
        else:
            for i, path in enumerate(sys.argv[1:]):
                try:
                    print_data(Path(path), os.stat(path), i + 1)
                except FileNotFoundError:
                    error(f"IMAGE[{i + 1:03d}]::[{path}] is not found.")
        return 0
    except KeyboardInterrupt:
        return 1

def print_data(path, stats, count: int=0):
    if not path.suffix.lower() in IMG_TYPE:
        return error(f"IMAGE[{count:03d}]::[{path}]Invalid file type")
    print(f"{'-' * 69}")
    print(f"IMAGE-[{count:03d}]::[{os.path.abspath(path)}]")
    print(f"|{'=' * 29}METADATA]{'=' * 30}|")
    print(f"| File Name:        {path.name}".ljust(68), "|")
    print(f"| File Type:        {path.suffix.upper().strip('.')} image".ljust(68), "|")
    print(f"| Size (KB):        {stats.st_size / 1024:.2f} KB".ljust(68), "|")
    print(f"| Creation Date:    {time(stats.st_birthtime)}".ljust(68), "|")
    print(f"| Modified Date:    {time(stats.st_mtime)}".ljust(68), "|")
    print(f"| Last Access Date: {time(stats.st_atime)}".ljust(68), "|")
    print(f"|{'=' * 30}[EXIF]{'=' * 32}|")
    try:
        with open(path, 'rb') as image_file:
            my_image = Image(image_file)
        if my_image.has_exif:
            for i in my_image.list_all():
                key = i.replace("_", " ").strip().title()
                if (key == 'Copyright'): continue
                try:
                    if isinstance(my_image[i], Flash):
                        print(f"| • {key}:".ljust(68), "|")
                        for attr in dir(my_image[i]):
                            if attr in FLASH_ATTR:
                                print(f"| |- • {attr}: {getattr(my_image[i], attr)}".ljust(68), "|")
                    else:
                        print(f"| • {key}: {my_image[i]}".ljust(68), "|")
                except Exception as e:
                    pass
        else:
            print(f"|{' ' * 17}This image file does not has EXIF{' ' * 18}|")
    except Exception:
        print(f"|{' ' * 17}This image file does not has EXIF{' ' * 18}|")
    print(f"[IMAGE]::[{count:03d}]--".rjust(70, '-'))
    if not count:
        return my_image.list_all()
    return


def modify_data(path, stats):
    tags = print_data(path, stats)
    print_promt()
    for line in sys.stdin:
        splited = line.split(' ')
        command = splited[0].lower().strip()
        if command in [ "add", "delete", "update" ]:
            count = 0
            print(f"[TAG]: ", end="", flush=True)
            for l in sys.stdin:
                tag = '_'.join(l.split(' ')).strip().lower()
                if command == "delete" and (tag in tags or '_' + tag in tags):
                    modification_data(path, command, tag);
                    break
                elif tag == "cancel": break;
                elif tag == "exit": exit();
                elif command == "add" or (command == "update" and (tag in tags or '_' + tag in tags)):
                    value = input(f"[VALUE]: ")
                    if (value.lower().strip() == "exit"): exit()
                    elif (value.lower().strip() == "cancel"): break
                    modification_data(path, command, tag, value);
                    break
                else:
                    error('Invalid tag.')
                    print(f"[TAG]: ", end="", flush=True)
            clear()
            tags = print_data(path, stats)
            print_promt()
        elif command == "exit": exit()
        else:
            error('Invalid commands.')
            print(f"[COMMAND]: ", end="", flush=True)
    return

def modification_data(path, mode: str, tag: str, value: str = ""):
    try:
        with open(path, 'rb') as image_file:
            my_image = Image(image_file)
        if mode == "delete":
            del my_image[tag]
        else:
            my_image[tag] = value
        with open(path, 'bw') as image_file:
            image_file.write(my_image.get_file())
            time = datetime.now().timestamp()
        os.utime(path, (time, time))
    except Exception as e:
        print(e)
    return

def print_promt():
    print(f"{'-' * 70}")
    print(f"| [ AVAILABLE COMMANDS ] ".ljust(68), "|")
    print(f"|• add    [TAG] [VALUE]  : Add a new metadata tag and its value.".ljust(68), "|")
    print(f"|• delete [TAG]          : Delete the specified metadata tag.".ljust(68), "|")
    print(f"|• update [TAG] [VALUE]  : Update the value of an existing tag.".ljust(68), "|")
    print(f"|• cencel                : Cancel the current metadata modification.".ljust(68), "|")
    print(f"|• exit                  : Update the value of an existing tag.".ljust(68), "|")
    print(f"{'-' * 70}")
    print(f"[COMMAND]: ", end="", flush=True)
    return

def clear() -> None:
	os.system('cls' if os.name == 'nt' else 'clear')

def size(byte: int) -> int:
    return format(int(bytes)/1024, ".2f")

def time(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return str(dt).split('.')[0]

def error(message: str, return_code: int=None):
    print(f"[ERROR]: {message}")
    return return_code

if __name__ == "__main__":
    main()
