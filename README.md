# HSE
An explorer for multiple directories

## Quickstart
first, The window is divided into two parts:

- panel 0
- panel 1

And then sectioned in 4 parts:

- Name
- Extension
- Size 
- Protection Bits

It is avaiable in linux and windows although some features might not work for linux.


*These are the comands currently avaiable:*
~~~
    tab               : move to the next section
    q                 : quit
    c                 : Compress the item selected with the chosen algorithm
    d                 : Decompress the item selected with the chosen algorithm
    s                 : move down in the current section
    w                 : move up in the current section
    Enter             : open the selected element
    '/'               : search in the current section
    c                 : compress the item currently selected - (**currently not working**)
    1-9               : select the n-th item in the current section
    r                 : rename the item currently selected
    m                 : Move the item currently selected to the other folder open
    <F5>(Win32), =, . : Copy the item selected to the other folder open
    x                 : Delete an item
    
    'Any Other'      : refresh the current section and do nothing
    
~~~
by the command line, you can use the following arguments:

~~~
usage: hse.py [-h] [-l LOG] [-c CONFIG] [-o OUTPUT] [-c1 COMPRESS_LEVEL] [-c4 {lz4,bz2,gzip,zlib}] [-v]

options:
  -h, --help            show this help message and exit
  -l LOG, --log LOG     Path to the log file (if not specified the default file is stdout)
  -c CONFIG, --config CONFIG
                        configuration file to use

  -c1 COMPRESS_LEVEL, --compress-level COMPRESS_LEVEL
                        level of compression
  -c4 {lz4,bz2,gzip,zlib}, --compress-algorithm {lz4,bz2,gzip,zlib}
                        algorithm of compression
  -v, --verbose         verbose mode
~~~

The default configuration is structured as follows:
~~~json
{
    "log":{
        "verbose":false,
        "path":"./logs/info.log",
        "format":"[ %(asctime)s ] %(levelname)s: %(message)s",
        "datefmt":"%Y-%m-%d %H:%M:%S %p"},
    "path_1":".",
    "path_2":".",
    "last_save":{
        "year":2022,
        "month":6,
        "day":6
    },
    "last_load":{
        "year":2022,
        "month":6,
        "day":6
    }
}
~~~
Obviously, you can change the configuration as long as you don't change the name of the file.

## Features
- The explorer can be configured
- explorer can compress/decompress the items using various algorithms
- explorer has log which can be redirected in any file.
- will make you see also protection bits and extension.
- explorer can be used in a terminal.
- is cross-platform.
