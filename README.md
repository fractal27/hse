# HSE
An explorer for multiple directories

## Quickstart
first, The window is divided into two parts:

- folder 1
- folder 2

And then sectioned in 4 parts:

- Name
- Extension
- Size 
- Protection Bits

*These are the comands currently avaiable:*
~~~
    tab              : move to the next section
    q  / ^C  /  esc  : quit
    s                : move down in the current section
    w                : move up in the current section
    Enter            : open the selected element
    '/' / ?          : search in the current section
    c                : compress the item currently selected
    1-9              : select the n-th item in the current section
    r                : rename the item currently selected
    'Any Other'      : refresh the current section and do nothing
~~~
by the command line, you can use the following arguments:

~~~
usage: hse.py [-h] [-l LOG] [-c CONFIG] [-c1 COMPRESS_LEVEL] [-c4 {lz4,bz2,gzip,zlib}] [-e] [-s] [-p][-v]

options:
  -h, --help            show this help message and exit
  -l LOG, --log LOG     Path to the log file
  -c CONFIG, --config CONFIG
                        Path to the config file
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
- The explorer is divided into sections
- The sections are divided into items
- The items are divided into coordinates
- Coordinates are the y-axis of the items
- The explorer can be configured
- explorer can compress the items
- explorer has automatic log
- explorer can be used in a terminal
- is cross-platform