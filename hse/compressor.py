from typing import Optional
import gzip
import lz4.frame
import zlib
import bz2
import os
import zipfile
import tarfile
import tempfile
import logging


def decompress(path)-> Optional[tuple[bytes,str]]:
    """
    Decompress a file.
    :param path: path to the file
    :return: [bytes] the decompressed file or [None] if transfering directory is not neccessary.
    """
    if not os.path.isfile(path):
        logging.error('Path to decompress is not a file')
    #get the compression algorithm of the file
    if path.endswith('.zip'):
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall()
        return
    elif path.endswith('.tar'):
        tarfile.open(path,'rb').extractall(path.removesuffix(".tar"))
        return

    with open(path,'rb') as f:
        if path.endswith('.gz'):
            #gzip
            data = gzip.decompress(f.read())
            ext = ".gz"

        if path.endswith('.lz4'):
            #lz4
            data = lz4.decompress(f.read(),wbits=0)
            ext = ".lz4"
        #zlib
        if path.endswith(".zlib"):
            #zlib
            data = zlib.decompress(f.read())
            ext = ".zlib"

        if path.endswith('.bz2'):
            #bz2
            data = bz2.decompress(f.read())
            ext = ".bz2"

    return data,ext

def compress(path,algo)->bytes:
    #print("compressing",path,level)
    if os.path.isfile(path):
        with open(path,'rb') as fp:
            if algo == 'lz4':
                content=fp.read()
                return lz4.frame.compress(content),"lz4"
            elif algo == 'bz2':
                return bz2.compress(content),"bz2"
            elif algo == 'gzip':
                return gzip.compress(content,level),"gz"
            elif algo == 'zlib':
                return zlib.compress(content,level=9),"zlib"
            else:
                raise Exception("Compression algorithm not valid.")
    elif os.path.isdir(path):
        #approaching directory
        if algo == 'lz4':
            #lz4
            with tempfile.TemporaryDirectory() as tmp:
                with tarfile.open(tmp,'w') as tar:
                    tar.add(path)
                return lz4.frame.compress(tar.read()),"tar.lz4"
        elif algo == 'bz2':
            #bz2
            with tempfile.TemporaryDirectory() as tmp:
                with tarfile.open(tmp,'w') as tar:
                    tar.add(path)
                return bz2.compress(tar.read()),"tar.bz2"
        elif algo == 'gzip':
            #gzip
            with tempfile.TemporaryDirectory() as tmp:
                with tarfile.open(tmp,'w') as tar:
                    tar.add(path)
                return gzip.compress(tar.read(),level),"tar.gz"
        elif algo == 'zlib':
            #zlib
            with tempfile.TemporaryDirectory() as tmp:
                with tarfile.open(tmp,'w') as tar:
                    tar.add(path)
                return zlib.compress(tar.read(),level=9),"tar.zlib"
        else:
            raise Exception("Compression algorithm not valid.")
    else:
        raise FileNotFoundError('File not found')

