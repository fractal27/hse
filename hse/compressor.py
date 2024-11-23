import gzip
import lz4.frame
import zlib
import bz2
import os
import zipfile
import tarfile
import tempfile
import logging


def decompress(path):
    """
    Decompress a file.
    :param path: path to the file
    :return: the decompressed file
    """
    if not os.path.isfile(path):
        logging.error('Path to decompress is not a file')
    #get the compression algorithm of the file
    if path.endswith('.zip'):
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall()
        return
    elif path.endswith('.tar'):
        with tempfile.TemporaryDirectory() as tmp:
            tarfile.open(path,'rb').extractall(tmp.name)
            return tmp.name

    with open(path,'rb') as f:
        if path.endswith('.gzip'):
            #gzip
            return gzip.decompress(f.read())
        if path.endswith('.lz4'):
            #lz4
            return lz4.decompress(f.read())
        #zlib
        if path.endswith(".zlib"):
            #zlib
            return zlib.decompress(f.read())
        if path.endswith('.bz2'):
            #bz2
            return bz2.decompress(f.read())
        return f.read()

def compress(path,level):
    if os.path.isfile(path):
        with open(path,'rb') as fp:
            content=fp.read()
            if level<=0:
                return lz4.frame.compress(content)
            elif level==1:
                return bz2.compress(content)
            elif 1>level>9:
                return gzip.compress(content,level)
            else:
                return zlib.compress(content,level=9)
    elif os.path.isdir(path):
        #approaching directory
        if level<=0:
            #lz4
            with tempfile.TemporaryDirectory() as tmp:
                with tarfile.open(tmp,'w') as tar:
                    tar.add(path)
                return lz4.frame.compress(tar.read())
        elif level==1:
            #bz2
            with tempfile.TemporaryDirectory() as tmp:
                with tarfile.open(tmp,'w') as tar:
                    tar.add(path)
                return bz2.compress(tar.read())
        elif 1>level>9:
            #gzip
            with tempfile.TemporaryDirectory() as tmp:
                with tarfile.open(tmp,'w') as tar:
                    tar.add(path)
                return gzip.compress(tar.read(),level)
        else:
            #zlib
            with tempfile.TemporaryDirectory() as tmp:
                with tarfile.open(tmp,'w') as tar:
                    tar.add(path)
                return zlib.compress(tar.read(),level=9)
    else:
        raise FileNotFoundError('File not found')

