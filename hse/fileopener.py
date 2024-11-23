import os
import sys
import argparse

if sys.platform=='win32':
    clear=lambda: os.system('cls')
    import msvcrt

    def getch():
        try:
            return msvcrt.getch().decode()
        except:
            return '\x03'

else:
    clear=lambda: os.system('clear')
    import termios,tty,sys
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def readonly(filename,winheight,winwidth,nums):
    with open(os.path.abspath(filename),'rb') as fp:
        contents=fp.read().decode("utf-8")
    y,scroll = 0,0
    if nums:
        winwidth += len(str(len(contents.splitlines())))
    lines=contents.splitlines()

    while 1:
        clear()
        if nums:
            print(*[f"{str(i+1).center(len(str(len(contents))),' ')}{''.join(x)}".ljust(winwidth,' ') for i,x in enumerate(lines)][y:y+winheight],sep='\n')
        else:
            print(*lines[y:y+winheight],sep='\n')
        c = getch()
        #print(c)
        if c in ('q','\x03'):
            break
        elif c=='w':
            if y>0:
                y-=1
            if scroll>0:
                scroll-=1
        elif c=='s':
            y+=1
            if y>=len(lines):
                y=len(lines)-1
                scroll+=1
        elif c=='n':
            nums^=1
def edit():... #TODO: implement edit mode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default=None, help='file to open')
    parser.add_argument("-V", "--version", action="version")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    parser.add_argument("-r", "--readonly", action="store_true", help="readonly mode")
    args = parser.parse_args()
    HEIGHT,WIDTH = os.get_terminal_size()
    if args.file:
        if args.readonly:
            readonly(args.file,winheight=HEIGHT,winwidth=WIDTH,nums=True)
        else:
            raise NotImplementedError
    else:
        parser.print_help()
if __name__=='__main__':
    main()
