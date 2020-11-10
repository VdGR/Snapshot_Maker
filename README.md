# Snapshot_maker



### Description

Snapshot maker will try to record a rtps stream for a few seconds after that it will try to make a picture out of this captured footage (gets deleted after making the picture). During a run of the program log messages are created. 

-X* number of pictures gets saved (oldest ones be deleted)   

### Dependencies

- ffmpeg**
- The ini file: "config_snapshot_maker.ini"

### Setup

1. Create a "photo" and "processing" folder. Add the "path" (details) to the ini file.

2. Change settings in the ini file. The most import settings: 

   *ffmpeg* (folder)
   *location* (ip) 
   *authentication* (username/password)



Side 

##### Windows??

If you want to use Snapshot maker on windows you need to change the logging file (currently line 59).

##### Pyhton 2.7??

Module `configparser` (line 14) has the name `ConfigParser` in Python 2.7.



*setting in ini file
** [`ffmpeg download link`](http://ffmpeg.org/download.html?aemtn=tg-on)



