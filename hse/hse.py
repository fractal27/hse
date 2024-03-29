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
import subprocess
from translate_pb import human_readable
import shutil

WIDTH, HEIGHT = os.get_terminal_size()
WIDTH = int(WIDTH/8)
HEIGHT -= 2
errors = []

if sys.platform.startswith("win32"):
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
    BS_KEY = "\b"

else:
    # setting getch for linux
    from getch import getch
    from curses.ascii import BS

    BS_KEY = chr(BS)

    def clear(): return os.system("clear")

def gettext(x):
    return str(x).center(WIDTH, ' ')[:WIDTH]


def display_paths(path_1: str, path_2: str, y: int, scrolled1: int = 0, scrolled2: int = 0, panel: Literal[0, 1] = 0):

    try:
        logging.debug("Displaying {0}, {1}".format(path_1, path_2))
        paths_1, paths_2 = os.listdir(path_1)[
            scrolled1:scrolled1+HEIGHT-1], os.listdir(path_2)[scrolled2:scrolled2+HEIGHT-1]

        paths_1 += [' ']*(abs(len(paths_1)-HEIGHT)-1)
        paths_2 += [' ']*(abs(len(paths_2)-HEIGHT)-1)

        exts_1 = [os.path.splitext(path)[1] for path in paths_1]
        exts_2 = [os.path.splitext(path)[1] for path in paths_2]

        logging.debug("Extensions Calculated.")

        dims_1 = [os.path.getsize(os.path.join(path_1, x))
                  if x != ' ' else 0 for x in paths_1]
        dims_2 = [os.path.getsize(os.path.join(path_2, x))
                  if x != ' ' else 0 for x in paths_2]

        logging.debug("Dimensions Calculated.")

        attrs_1 = list(map(human_readable, [os.stat(os.path.join(path_1, x)).st_mode & 0o777 if x !=
                                            ' ' else '?' for x in paths_1]))
        attrs_2 = list(map(human_readable, [os.stat(os.path.join(path_2, x)).st_mode & 0o777 if x !=
                                            ' ' else '?' for x in paths_2]))

        logging.debug("Protection Bits Calculated.")
    except Exception as e:
        logging.error(f"Error: {e}")
        return

    mat = np.zeros((HEIGHT, 8), dtype=object)

    for i in range(2):
        mat[0, 0+i*4] = gettext("Name")
        mat[0, 1+i*4] = gettext("Extension")
        mat[0, 2*(1+i*2)] = gettext("Size")
        mat[0, 3+i*4] = gettext("Protection Bits")
    mat[1:, 0] = [x.ljust(WIDTH, ' ')[:WIDTH] for x in paths_1]
    mat[1:, 1] = list(map(gettext, exts_1))
    mat[1:, 2] = [str(x).rjust(WIDTH, ' ')[:WIDTH]for x in dims_1]
    # mat[1:, 2] = list(map(gettext, dims_1))
    mat[1:, 3] = list(map(gettext, attrs_1))
    mat[1:, 4] = [x.ljust(WIDTH, ' ')[:WIDTH] for x in paths_2]
    mat[1:, 5] = list(map(gettext, exts_2))
    # mat[1:, 6] = list(map(gettext, dims_2))
    mat[1:, 6] = [str(x).rjust(WIDTH, ' ')[:WIDTH] for x in dims_2]
    mat[1:, 7] = list(map(gettext, attrs_2))

    ORIZZ_SLICE = slice(0, 3) if not panel else slice(4, 7)

    mat[y, ORIZZ_SLICE] = [f'\033[7m{x}\033[0m' for x in mat[y, ORIZZ_SLICE]]

    logging.debug("Matrix Calculated.")
    logging.debug("Matrix displayed properly.")

    name = mat[y, 0] if not panel else mat[y, 4]

    return mat


def cli_interface(config,config_path):


    path_1, path_2 = config.get("path_1"),config.get("path_2")
    path_1, path_2 = os.path.abspath(path_1), os.path.abspath(path_2)

    y = 1
    panel = 0
    scrolled1, scrolled2 = 0, 0
    SEARCH = None
    while 1:
        try:
            clear()
            if not SEARCH:
                mat = display_paths(path_1, path_2, y, scrolled1, scrolled2, panel)
            else:
                if not panel:
                    mat = [x for x in display_paths(
                        path_1, path_2, y, scrolled1, scrolled2, panel) if SEARCH in x[0]]
                else:
                    mat = [x for x in display_paths(
                        path_1, path_2, y, scrolled1, scrolled2, panel) if SEARCH in x[4]]

            char = getch()
            logging.debug("Key pressed: {0}".format(char))
            if char.isdigit():
                if not panel:
                    y = 1+(int(char)%len([x for x in mat[1:, 0] if x.endswith(' '*HEIGHT)]))
                    continue
                y = int(char)%len([x for x in mat[1:, 4] if x.endswith(' '*HEIGHT)])

            if char == 'q':
                logging.debug("Exiting")
                break

            elif char == '\t':
                print("\033[7mSwitching panels\033[0m")
                panel = 1-panel
                y = 1

            elif char in ['w',"k"]:
                y -= 1
                if y < 1:
                    y = 1

                    if not panel and scrolled1 > 0:
                        scrolled1 -= 1
                    elif panel and scrolled2 > 0:
                        scrolled2 -= 1

            elif char in ['s' ,'j']:
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
                name = name.removesuffix("\033[0m").removeprefix("\033[7m").strip()
                ext = mat[y, 1] if panel == 0 else mat[y, 5]
                ext = ext.removeprefix("\033[7m").removesuffix("\033[0m").strip()
                if ext in name:
                    ext = ''
                y = 1
                scrolled1, scrolled2 = 0, 0
                logging.info("Opening {0}".format(mat[y, 0]))
                clear()

                if os.path.isdir(os.path.join(path_1, name)) if not panel else os.path.isdir(os.path.join(path_2, name)):
                    logging.debug("Is a directory:")
                    to_change = path_1 if not panel else path_2
                    path_1 = os.path.join(
                        to_change, name) if not panel else path_1
                    path_2 = path_2 if not panel else os.path.join(
                        to_change, name)
                    mat = display_paths(path_1, path_2, y,
                                        scrolled1, scrolled2, panel)
                elif os.path.isfile(os.path.join(path_1, name)) if not panel else os.path.isfile(os.path.join(path_2, name)):
                    data = compressor.decompress(os.path.join(
                        path_1, ''.join((name, ext))) if not panel else os.path.join(path_2, ''.join((name, ext))))
                    if isinstance(data, str):
                        mat = display_paths(*
                                            ((data, path_2) if not panel else (path_1, data)), y, scrolled1, scrolled2, panel)
                    elif isinstance(data, bytes):
                        with tempfile.TemporaryFile("wb") as tmp:
                            tmp.write(data)
                            subprocess.Popen(
                                f'"{tmp.path}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        logging.error("Unknown type")
                else:
                    logging.error("File not found")
            elif char == BS_KEY:
                logging.info("Returning to main directory")
                if not panel:
                    path_1 = os.path.dirname(path_1)
                else:
                    path_2 = os.path.dirname(path_2)
                clear()
                mat = display_paths(path_1, path_2, y, scrolled1, scrolled2, panel)
            elif char == '/':
                logging.info("Searching")
                SEARCH = input("/")
                if not panel:
                    mat = [x for x in display_paths(
                        path_1, path_2, y, scrolled1, scrolled2, panel) if SEARCH in x[0]]
                    continue
                mat = [x for x in display_paths(
                    path_1, path_2, y, scrolled1, scrolled2, panel) if SEARCH in x[4]]
            elif char == 'c':
                logging.info("Compressing {0}".format(mat[y, 0]))
                if not panel:
                    compressor.compress(os.path.join(
                        path_1, mat[y, 0]), config.get("compress", 5))
                else:
                    compressor.compress(os.path.join(
                        path_2, mat[y, 4]), config.get("compress", 5))
            elif char == 'd':

                logging.info("Decompressing {0}".format(mat[y, 0]))
                if not panel:
                    compressor.decompress(os.path.join(
                        path_1, mat[y, 0]))
                else:
                    compressor.decompress(os.path.join(
                        path_2, mat[y, 4]))
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
            elif char == 'x' or char == "\x7F":
                logging.info("Deleting file...")
                if not panel:
                    filename = mat[y, 0].replace("\033[7m","").replace("\033[0m","").strip()
                    os.remove(os.path.join(path_1, filename))
                else:
                    filename = mat[y, 4].replace("\033[7m","").replace("\033[0m","").strip()
                    os.remove(os.path.join(path_2, filename))
            #if is f5
            elif char in ['.', '=']:
                #copy the file to the other panel
                filename = mat[y, 0].replace("\033[7m","").replace("\033[0m","").strip()
                if not panel:
                    shutil.copy(os.path.join(path_1, filename), os.path.join(
                        path_2, filename))
                else:
                    shutil.copy(os.path.join(path_2, filename), os.path.join(
                        path_1, filename))
            else:
                logging.error(f"{ord(char)}not supported.")


        except Exception as e:
            logging.error(e)
            errors.append(repr(e))

    logging.info("Saving to file")
    today = datetime.today()
    logging.debug("changing data...")
    config["last_save"] = {"year":today.year,"month":today.month,"day":today.day}
    config["path_1"] = path_1
    config["path_2"] = path_2
    config["errors"] = errors
    logging.debug("Encoding configuration and saving...")
    to_save = json.encoder.JSONEncoder().encode(config)
    with open(config_path,'w') as fp:
        fp.write(to_save)
    logging.info("Saved configuration to file")


def argument_parsing():
    parser = argparse.ArgumentParser()
    #parser.add_argument("-l", "--log", type=str, default=os.path.join(os.path.dirname(__file__),
    #                    "logs", f'{datetime.now().strftime("%Y%m%d-%H%M%S")}.log'), help="Path to the log file")
    parser.add_argument("-l", "--log", type=str, default=None, help="Path to the log file")


    parser.add_argument("-c","--config", type=str, help="configuration file to use", default=os.path.join(os.path.dirname(__file__),'save.json'))
    parser.add_argument("-o", "--output", type=str,
                        help="Path to the output file")
    parser.add_argument("-c1", "--compress-level",
                        type=int, help="level of compression")
    parser.add_argument("-c4", "--compress-algorithm", type=str,
                        choices=["lz4", "bz2", "gzip", "zlib"], help="algorithm of compression")
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="verbose mode")
    return parser.parse_args()


def main():
    args = argument_parsing()
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

    logger=logging.getLogger("hse")

    logger.debug("Started")
    logger.debug(f"Config file initialized: {args.config}")
    logger.debug(f"Log file initialized: {args.log}")
    logger.debug(f"Compression level: {args.compress_level}")
    logger.debug(f"Compression algorithm: {args.compress_algorithm}")
    logger.debug("Arguments parsed")
    logger.info("Starting cli interface")
    cli_interface(config,os.path.join(os.path.dirname(__file__),args.config))
    logger.info("Done: Leaving...")

if __name__=='__main__':
    main()
