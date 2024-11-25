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
    logging.info(f"::[-1]\"{path}\"")
    if not os.path.isfile(path):
        logging.error('Path to decompress is not a file')
        return NotImplemented
    #get the compression algorithm of the file
    if path.endswith('.zip'):
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall()
        return

    if path.endswith('.tar.gz'):
        with tarfile.open(path,'r:gz') as tf: #gzip
            tf.extractall(path=path.removesuffix(".tar.gz"))
    elif path.endswith('.tar.lz4'):
        """with tarfile.open(path,"w")
            #lz4
            data = lz4.decompress(f.read(),wbits=0)
            ext = ".lz4"""""
        return NotImplemented
    elif path.endswith(".tar.zlib"):
        """#zlib
        if path.endswith(".zlib"):
            #zlib
            data = zlib.decompress(f.read())
            ext = ".zlib"""""
        return NotImplemented
    elif path.endswith(".tar.bz2"):
        with tarfile.open(path,"r:bz2") as tf: #bz2
            tf.extractall(path=path.removesuffix(".tar.gz"))
    return

def compress(path,algo)->bytes:
    #print("compressing",path,level)
    logging.info(f"::\"{path}\",\"{algo}\".")
    if os.path.isfile(path):
        with open(path,'rb') as fp:
            content=fp.read()
            if algo == 'lz4':
                return lz4.frame.compress(content),"lz4"
            elif algo == 'bz2':
                return bz2.compress(content),"bz2"
            elif algo == 'gzip':
                return gzip.compress(content),"gz"
            elif algo == 'zlib':
                return zlib.compress(content,level=9),"zlib"
            else:
                raise Exception("Compression algorithm not valid.")
    elif os.path.isdir(path):
        #approaching directory
        if algo == 'lz4':
            #TODO: make lz4 adaptation with tar
            """with tempfile.NamedTemporaryFile("rb+") as tmp: ## doestn' work
                with tarfile.open(tmp.name,'w') as tar:
                    tar.add(path)
                return lz4.frame.compress(tar.read()),"tar.lz4"""
            return NotImplemented
        elif algo == 'bz2':
            #bz2
            with tempfile.NamedTemporaryFile("rb+") as tmp:
                with tarfile.open(tmp.name,'w:bz2') as tar:
                    tar.add(path)
                data = tmp.read()
            return data,"tar.bz2"
        elif algo == 'gzip':
            #gzip
            with tempfile.NamedTemporaryFile("rb+") as tmp:
                with tarfile.open(tmp.name,'w:gz') as tar:
                    tar.add(path)
                data = tmp.read()
            return data,"tar.gz"
        elif algo == 'zlib':
            #TODO: make zlib adaptation with tar
            """with tempfile.NamedTemporaryFile("rb+") as tmp:
                with tarfile.open(tmp.name,'w') as tar:
                    tar.add(path)
                return zlib.compress(tar.read(),level=9),"tar.zlib"""
            return NotImplemented
        else:
            raise Exception("Compression algorithm not valid.")
    else:
        raise FileNotFoundError('File not found')

