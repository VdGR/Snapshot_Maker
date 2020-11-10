#!/usr/bin/env python3

"""snapshot_maker.py: Will try to record a rtps stream for a few seconds
after that it will try to make a picture out of this captured footage."""

__author__ = "Robin Van der Gucht"

# region Imports
import datetime as d
import glob
import os
import subprocess
import sys
import configparser  # different name  (ConfigParser) in Python 2.7
import platform

# endregion

# region Variables
ini_file = "config_snapshot_maker.ini"


def right_variables():
    if platform.system() == "Windows":
        change_variables("WINDOWS")
    elif platform.system() == "Linux":
        change_variables("LINUX")


def change_variables(os):
    with open(ini_file) as config_file:
        config.read_file(config_file)
        my_section_to_rename = os
        my_section_items = config.items(os)
        my_section_new_name = "EXPECTED"
        config.add_section(my_section_new_name)
        for option, value in my_section_items:
            config.set(my_section_new_name, option, value)
            config.remove_section(my_section_to_rename)


config = configparser.ConfigParser()
right_variables()
config.read(ini_file)
ffmpeg = config['EXPECTED']['ffmpeg']
video_folder = config['EXPECTED']['video_folder']
picture_folder = config['EXPECTED']['picture_folder']
location = config['LOCATION']['ip']
video_time = config['TIME']['video_time']
timeout = int((config['TIME']['timeout']).strip('"')) * 1000000  # -stimeout requires time in micro seconds
username = (config['AUTHENTICATION']['username']).strip("'")
password = (config['AUTHENTICATION']['password']).strip("'")
loglevel = (config['LOGLEVEL']['lglvl']).strip("'")
permitted_picutres = int((config['PICTURES']['permitted']).strip("'"))

# endregion

# region Logging
log = open("/usr/lib/check_mk_agent/local/Snapshot_maker.py", "w+")
log.write("#!/usr/bin/env python\n")
warn_log = ""


def logging():
    if len(warn_log) > 1:
        log.write('print("1 Snapshot_maker - WARN -  ' + warn_log + '")\n')
    else:
        log.write('print("0 Snapshot_maker - OK - Everything went according to plan")\n')


# endregion

# region These functions make the file name
def file_name(type):  # This function wil make the filename
    types = {
        "video": str(video_folder + 'video' + get_filename_number() + '.mov'),
        "picture": str(picture_folder + 'picture' + get_filename_number() + '.jpg'),

    }
    return types.get(type, "Invalid type")


def get_filename_number():
    minute = int(d.datetime.now().strftime("%M"))
    number = minute - (minute % 5)
    return str(number)


# endregion

# region ffmpeg functions


def make_video(file):
    if subprocess.call(
            'ffmpeg  -loglevel ' + str(loglevel) + ' -y -rtsp_transport tcp -stimeout ' + str(
                timeout) + '  -i  rtsp://' + str(
                username) + ':' + str(
                password) + '@' + str(
                location)
            + '/videoMain -t ' + video_time + ' -acodec copy  -vcodec copy ' + file,
            shell=True) == 0:
        return print("0 Check_Video_Made - OK - Making: ", file, ' succeeded')
    else:
        print("Something went wrong making:" + str(file))
        log.write('print("2 Snapshot_maker - CRIT - Something went wrong making: ' + str(file) + '!!!")\n')
        sys.exit(2)


def make_picture(file):
    if subprocess.call(
            'ffmpeg  -loglevel panic -y -i ' + str(find_latest_video()) + ' -vframes 1 '
            + file, shell=True) == 0:
        return print("0 Check_Picture_Made - OK - Making: ", file, " succeeded")
    else:
        log.write('print("2 Snapshot_maker - CRIT - Something went wrong making: ' + str(file) + '!!!")\n')
        sys.exit(2)


# endregion

# region These functions find the desired files
def check_exists(file):
    return os.path.isfile(file)


def find_latest_video():
    try:
        list_of_videos = glob.glob(video_folder + str('*.mov'))
        if len(list_of_videos) <= 0:
            return print('No videos were found')
        return max(list_of_videos, key=os.path.getctime)
    except ImportError:
        print("Didn't find last video")


def find_first_picture(warn_log=warn_log):
    list_of_pictures = glob.glob(picture_folder + str('*.jpg'))
    if len(list_of_pictures) <= 0:
        warn_log += 'print("' + str(picture_folder) + 'is empty")'
        return print("Picture folder is empty")
    return min(list_of_pictures, key=os.path.getctime)


# endregion

# region These functions will delete the right files
def delete_made_video(video, warn_log=warn_log):
    os.remove(video)
    if not check_exists(video):
        return print('0 Check_Video_Deleted - OK - ', video, ' was successful deleted')
    else:
        warn_log += (video, 'was not deleted')


def delete_old_picture():
    if len(os.listdir(picture_folder)) > permitted_picutres:
        return os.remove(find_first_picture())


def delete(video, warn_log=warn_log):
    delete_made_video(video)
    delete_old_picture()
    if len(os.listdir(picture_folder)) == 5:
        return print('0 Check_Amount_Pictures - OK - Permitted pictures are okay')
    else:
        warn_log += ('Permitted pictures are NOT okay')


# endregion

# region Initialize ffmpeg
def check_ffmpeg():
    return check_exists("ffmpeg")


def cd(ffmpeg):
    return os.chdir(ffmpeg)


def ffmpeg_ready():
    cd(ffmpeg)
    if not check_ffmpeg():
        log.write('print("2 Snapshot_maker - CRIT - FFmpeg was not found!!!")\n')
        sys.exit(2)
    else:
        return check_ffmpeg()


# endregion

# region Main function
def run():
    video = file_name("video")
    picture = file_name("picture")
    make_video(video)
    if check_exists(video):
        make_picture(picture)
        if not check_exists(picture):
            sys.exit(2)  # When the picture was not made stop the program.
        delete(video)  # When the picture was made the video can be deleted.
    else:
        sys.exit(2)  # When the video was not made the program stops and the picture will not be made.
    logging()


# endregion

if __name__ == "__main__":
    if ffmpeg_ready():
        run()
