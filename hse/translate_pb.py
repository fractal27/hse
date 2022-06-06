import argparse
import os

# for pb i mean protection bits
# for octal i mean octal protection bits


def human_readable(pb: int) -> str:
    """
    Convert a protection bits to a human readable string
    :param pb: protection bits
    :return: human readable string
    """
    if isinstance(pb, int):
        _final = [format(int(x),'b').ljust(3,'0') for x in oct(pb)[2:]]
        final = ''.join([f'{"r" if x[0]=="1" else "-"}{"w" if x[1]=="1" else "-"}{"x" if x[2]=="1" else "-"}' for x in _final])
        return final
    return pb


def main():
    parser = argparse.ArgumentParser("translate_pb")
    parser.add_argument("-o", "--octal", type=str,
                        help="octal protection bits")
    parser.add_argument("-b", "--binary", type=str,
                        help="binary protection bits")
    parser.add_argument("-H", "--human", action="store_true",
                        help="human readable protection bits")

    args = parser.parse_args()
    if args.human:
        if args.octal:
            human_readable(int(args.octal, 8))
        elif args.binary:
            human_readable(int(args.binary, 2))
        else:
            print("No argument")
    elif args.octal:
        print(oct(args.octal))
    elif args.binary:
        print(bin(args.binary))
    else:
        print("No argument")

if __name__=='__main__':
    main()
