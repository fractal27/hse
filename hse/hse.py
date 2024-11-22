import tempfile
import compressor as compressor
import argparse
import os
import numpy as np
import logging
import json
from datetime import datetime
import sys
from typing import Literal
from translate_pb import human_readable
import shutil
import fileopener

WIDTH, HEIGHT = os.get_terminal_size()
WIDTH = int(WIDTH/8)
HEIGHT -= 2
errors = []
LINUX = True

if sys.platform.startswith("win32"):
    LINUX = False
    # changing kernel mode in Windows to enable ansii escape sequences

    import ctypes
    try:
        ctypes.windll.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception as e:
        logging.warning(f"{e}")

    # setting getch for windows
    import msvcrt

    def getch():
        try:
            return msvcrt.getch().decode()
        except:
            return '\x03'

    def clear(): return os.system("cls")

else:
    # setting getch for linux
    import sys
    import tty
    import termios

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def clear(): return os.system("clear")


def gettext(x):
    return str(x).center(WIDTH, ' ')[:WIDTH]


def display_paths(path_1: str, path_2: str, y: int, scrolled1: int = 0, scrolled2: int = 0, panel: Literal[0, 1] = 0,
                  showextension : bool=False, showsize : bool=False, showprotectionbits : bool=False):

    try:
        logging.info("Displaying {0}, {1}".format(path_1, path_2))

        paths_1, paths_2 = os.listdir(path_1)[
            scrolled1:scrolled1+HEIGHT-1], os.listdir(path_2)[scrolled2:scrolled2+HEIGHT-1]


        paths_1 += [' ']*(abs(len(paths_1)-HEIGHT)-1)
        paths_2 += [' ']*(abs(len(paths_2)-HEIGHT)-1)

        if showextension:
            exts_1 = [os.path.splitext(path)[1] for path in paths_1]
            exts_2 = [os.path.splitext(path)[1] for path in paths_2]
        else:
            exts_1 = [' ']*len(paths_1)
            exts_2 = [' ']*len(paths_2)
        logging.debug("Extensions Calculated.")

        if showsize:
            dims_1 = [os.path.getsize(os.path.join(path_1, x))
                  if x != ' ' else 0 for x in paths_1]
            dims_2 = [os.path.getsize(os.path.join(path_2, x))
                  if x != ' ' else 0 for x in paths_2]
        else:
            dims_1 = [' ']*len(paths_1)
            dims_2 = [' ']*len(paths_2)

        logging.debug("Dimensions Calculated.")

        if showprotectionbits:
            attrs_1 = list(map(human_readable, [os.stat(os.path.join(path_1, x)).st_mode & 0o777 if x !=
                                            ' ' else '?' for x in paths_1]))
            attrs_2 = list(map(human_readable, [os.stat(os.path.join(path_2, x)).st_mode & 0o777 if x !=
                                            ' ' else '?' for x in paths_2]))
        else:
            attrs_1 = [' ']*len(paths_1)
            attrs_2 = [' ']*len(paths_2)

        logging.debug("Protection Bits Calculated.")
    except Exception as e:
        logging.error(f"Error: {e}")
        return
    else:
        logging.debug("Display setup ran Succesfully!")

    mat = np.zeros((HEIGHT, 8), dtype=object)

    for i in range(2):
        mat[0, 0+i*4] = gettext("Name")
        mat[0, 1+i*4] = gettext("Extension")
        mat[0, 2*(1+i*2)] = gettext("Size")
        mat[0, 3+i*4] = gettext("Protection Bits")
    mat[1:, 0] = list(map(lambda x: x.ljust(WIDTH, ' ')[:WIDTH], paths_1))
    mat[1:, 1] = list(map(gettext, exts_1))
    mat[1:, 2] = list(map(lambda x: str(x).rjust(WIDTH, ' ')[:WIDTH], dims_1))
    # mat[1:, 2] = list(map(gettext, dims_1))
    mat[1:, 3] = list(map(gettext, attrs_1))
    mat[1:, 4] = list(map(lambda x: x.ljust(WIDTH, ' ')[:WIDTH], paths_2))
    mat[1:, 5] = list(map(gettext, exts_2))
    # mat[1:, 6] = list(map(gettext, dims_2))
    mat[1:, 6] = list(map(lambda x: str(x).rjust(WIDTH, ' ')[:WIDTH], dims_2))
    mat[1:, 7] = list(map(gettext, attrs_2))

    ORIZZ_SLICE = slice(0, 3) if not panel else slice(4, 7)

    mat[y, ORIZZ_SLICE] = [f'\033[7m{x}\033[0m' for x in mat[y, ORIZZ_SLICE]]

    logging.debug("Matrix Displayed properly.")

    name = mat[y, 0] if not panel else mat[y, 4]

    print(*[''.join(x) for x in mat], name, sep='\n')
    return mat


def cli_interface(config,config_path):


    path_1, path_2 = config.get("path_1"),config.get("path_2")
    if path_1 == None:
        if LINUX: path_1="/home"
        else:     path_1="C:\\Users"
    if path_2 == None:
        if LINUX:path_2="/home"
        else:    path_2="C:\\Users"
    if not os.path.isdir(path_1) or not os.path.isdir(path_2):
        logging.error("Error: directory not found(%(path1)s,%(path2)s)"%{"path1":path_1,"path2":path_2});
        return
    #ext size prot_bits
    showd = config.get("show",{}).get("extension",False),\
            config.get("show",{}).get("size",False),\
            config.get("show",{}).get("protection_bits",False)

    path_1, path_2 = os.path.abspath(path_1), os.path.abspath(path_2)

    y = 1
    panel = 0
    scrolled1, scrolled2 = 0, 0
    SEARCH = None
    while 1:
        try:
            clear()
            if not SEARCH:
                mat = display_paths(path_1, path_2, y, scrolled1, scrolled2, panel, *showd)
            else:
                if not panel:
                    mat = [x for x in display_paths(
                        path_1, path_2, y, scrolled1, scrolled2, panel, *showd) if SEARCH in x[0]]
                else:
                    mat = [x for x in display_paths(
                        path_1, path_2, y, scrolled1, scrolled2, panel, *showd) if SEARCH in x[4]]

            char = getch()
            logging.debug("Key pressed: {0}".format(char))
            if not panel:
                mat[y, 0] = mat[y, 0].removeprefix("\033[7m")\
                                     .removesuffix("\033[0m").strip()
                path = path_1
            else:
                mat[y, 4] = mat[y, 4].removeprefix("\033[7m")\
                                     .removesuffix("\033[0m").strip()
                path = path_2

            if char.isdigit():
                if not panel:
                    y = 1+(int(char)%len([x for x in mat[1:, 0] if x.endswith(' '*HEIGHT)]))
                    continue
                y = int(char)%len([x for x in mat[1:, 4] if x.endswith(' '*HEIGHT)])

            if char in ['q', "\x1b", "\x03", "\x04"]:
                logging.debug("Exiting")
                break

            elif char == '\t':
                # print("\033[7mSwitching panels\033[0m")
                panel = 1-panel
                y = 1

            elif char in ['w', 'k']:
                y -= 1
                if y < 1:
                    y = 1

                    if not panel and scrolled1 > 0:
                        scrolled1 -= 1
                    elif panel and scrolled2 > 0:
                        scrolled2 -= 1

            elif char in ['s', 'j']:
                if y == HEIGHT-1:
                    if not panel:
                        scrolled1 += 1
                    else:
                        scrolled2 += 1

                # getting the lenght of the column to be able to scroll
                if panel == 0:
                    c = len(mat[1:, 0]) - \
                        len([x for x in mat[1:, 0] if x.endswith(' '*WIDTH)])
                else:
                    c = len(mat[1:, 4]) - \
                        len([x for x in mat[1:, 4] if x.endswith(' '*WIDTH)])

                y += 1
                y = c if y > c else y

            elif char in ['\n', '\r']:

                name = mat[y, 0] if panel == 0 else mat[y, 4]
                ext = mat[y, 1] if panel == 0 else mat[y, 5]
                ext = ext.removeprefix("\033[7m").removesuffix("\033[0m").strip()
                if ext in name:
                    ext = ''
                y = 1
                scrolled1, scrolled2 = 0, 0
                logging.info("Opening {0}".format(f"{name}/{path}"))
                clear()

                if os.path.isdir(os.path.join(path, name)):
                    logging.debug("Is a directory:")
                    to_change = path
                    path_1 = path_1 if     panel else os.path.join(
                        to_change, name)
                    path_2 = path_2 if not panel else os.path.join(
                        to_change, name)
                    mat = display_paths(path_1, path_2, y,
                                        scrolled1, scrolled2, panel,*showd)
                elif os.path.isfile(os.path.join(path, name)):
                    path_c2 = os.path.join(path,name)
                    if ext in ["lz4","bd2","zip","gz","zlib"]:
                        all_c2 = compressor.decompress(os.path.join(path_c2,ext))
                    else:
                        with open(path_c2) as fp:
                            all_c2 = fp.read()

                    if isinstance(all_c2, tuple):
                        data_c2, ext_c2 = all_c2
                        with tempfile.TemporaryFile("wb") as tmp:
                            tmp.write(data_c2)
                            fileopener.readonly(tmp.name,HEIGHT,WIDTH,False)
                    else:
                        to_open = path_c2
                        fileopener.readonly(to_open,HEIGHT,WIDTH,False)
                else:
                    logging.error("File not found")
            elif char == '\b':
                logging.info("Returning to main directory")
                if not panel:
                    path_1 = os.path.dirname(path_1)
                else:
                    path_2 = os.path.dirname(path_2)
                clear()
                mat = display_paths(path_1, path_2, y, scrolled1, scrolled2, panel,*showd)
            elif char == '/':
                logging.info("Searching")
                SEARCH = input(":")
                if not panel:
                    mat = [x for x in display_paths(
                        path_1, path_2, y, scrolled1, scrolled2, panel, *showd) if SEARCH in x[0]]
                    continue
                mat = [x for x in display_paths(
                    path_1, path_2, y, scrolled1, scrolled2, panel, *showd) if SEARCH in x[4]]
            elif char == 'c':
                name = mat[y,0] if path == path_1 else mat[y,4]
                logging.info("Compressing {0}".format(name))

                data_c, ext_c = compressor.compress(os.path.join(
                            path, name), config.get("compression-algo", "gzip"))
                with open(os.path.join(path,name)+f".{ext_c}","wb") as fp:
                    fp.write(data_c)

            elif char == 'd':

                if not panel:
                    logging.info("Decompressing {0}".format(mat[y, 0]))

                    result = compressor.decompress(os.path.join(
                            path_1, mat[y, 0]))
                    if result:
                        data_c, ext_c = result
                        with open(os.path.join(path_1,mat[y, 0]).removesuffix(ext_c),"wb") as fp:
                            fp.write(data_c)
                else:
                    result = compressor.decompress(os.path.join(
                            path_2, mat[y, 4]))
                    if result:
                        data_c, ext_c = result
                        with open(os.path.join(path_2,mat[y, 0]).removesuffix(ext_c),"wb") as fp:
                            fp.write(data_c)
            elif char == 'r':
                logging.info("Renaming {0}".format(mat[y, 0]))
                if not panel:
                    os.rename(os.path.join(path_1, mat[y, 0]), os.path.join(
                        path_1, input("New name: ")))
                else:
                    os.rename(os.path.join(path_2, mat[y, 4]), os.path.join(
                        path_2, input("New name: ")))
            elif char == 'm':
                logging.info("Moving {0}".format(mat[y, 0]))
                if not panel:
                    os.rename(os.path.join(path_1, mat[y, 0]), os.path.join(
                        path_2, mat[y, 0]))
                else:
                    os.rename(os.path.join(path_2, mat[y, 4]), os.path.join(
                        path_1, mat[y, 4]))
            elif char == 'x':
                name = mat[y,0] if path == path_1 else mat[y,4]
                logging.info("Deleting {0}".format(name))
                i = input("Are you sure you want to delete '{}'? (N/y)".format(name))
                if i.upper() == 'Y':
                    if os.path.isdir(os.path.join(path,name)):
                        shutil.rmtree(os.path.join(path, name))
                    else:
                        logging.info("Deleting {0}".format(name))
                        os.remove(os.path.join(path, name))

            elif char == 'z':  ##changed from F5 to cease cross-compatibility issues
                #copy the file to the other panel
                logging.info("Copying {0}".format(mat[y, 0]))


                if os.path.isdir(os.path.join(path,mat[y,0] if not panel else mat[y,4])):
                    copy_function = shutil.copytree
                    logging.info("copy function: copytree")
                else:
                    copy_function = shutil.copy
                    logging.info("copy function: copy")

                if not panel:
                    copy_function(os.path.join(path_1, mat[y, 0]), os.path.join(
                        path_2, mat[y, 0]))
                else:
                    copy_function(os.path.join(path_2, mat[y, 4]), os.path.join(
                        path_1, mat[y, 4]))


        except Exception as e:
            logging.exception(e)
            errors.append(repr(e))
            y = 1
            if not panel:
                path_1 = os.path.dirname(path_1)
                mat = [x for x in display_paths(path_1,path_2,y,scrolled1,scrolled2,panel,*showd) if not x[0].endswith(" "*WIDTH)]
            else:
                path_2 = os.path.dirname(path_2)
                mat = [x for x in display_paths(path_1,path_2,y,scrolled1,scrolled2,panel,*showd) if not x[4].endswith(" "*WIDTH)]


    logging.info("Saving to file")
    today = datetime.today()
    logging.debug("changing data...")
    config["last_save"] = {"year":today.year,"month":today.month,"day":today.day}
    config["path_1"] = path_1
    config["path_2"] = path_2
    config["errors"] = errors
    logging.debug("Encoding configuration and saving...")
    #prettify the json
    to_save = json.dumps(config, indent=4)
    with open(config_path,'w') as fp:
        fp.write(to_save)
    logging.info("Saved configuration to file")


def argument_parsing():
    if not os.path.isdir("logs"):
        os.mkdir("logs");
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", type=str, default=os.path.join(os.path.dirname(__file__),
                        "logs", f'{datetime.now().strftime("%Y%m%d-%H%M%S")}.log'), help="Path to the log file")
    #parser.add_argument("-l", "--log", type=str, default=None, help="Path to the log file")


    parser.add_argument("-c","--config", type=str, help="configuration file to use", default=os.path.join(os.path.dirname(__file__),'save.json'))
    parser.add_argument("-o", "--output", type=str,
                        help="Path to the output file")
    parser.add_argument("-V", "--version", help="print version and exit")
    parser.add_argument("-ca", "--compression-algorithm", type=str,
                        choices=["lz4", "bz2", "gzip", "zlib"], help="algorithm of compression")
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="verbose mode")
    return parser.parse_args()


def main():
    args = argument_parsing()
    if args.version:
        from . import __version__
        print(__version__)
        return
    if not os.path.isfile(args.config):
        print("Config file not found")
        return
    config = json.load(open(os.path.join(os.path.dirname(__file__),args.config),'r'))
    if args.log:
        logging.basicConfig(filename=args.log,level=logging.DEBUG if args.verbose else logging.INFO,
                format=config["log"].get("format"), datefmt=config["log"].get("datefmt"))
    else:
        logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                format=config["log"].get("format"), datefmt=config["log"].get("datefmt"))

    if args.compression_algorithm:
        config["compression-algo"] = args.compression_algorithm;


    logger=logging.getLogger("hse")

    logger.debug("Started")
    logger.debug(f"Config file initialized: {args.config}")
    logger.debug(f"Log file initialized: {args.log}")
    logger.debug(f"Compression algorithm: {args.compression_algorithm}")
    logger.debug("Arguments parsed")
    logger.info("Starting cli interface")
    cli_interface(config,os.path.join(os.path.dirname(__file__),args.config))
    logger.info("Done: Leaving...")

if __name__=='__main__':
    main()
