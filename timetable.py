#!/usr/bin/python3
import os
import argparse
import time
import math
import yaml
import signal
import sys
import random

#  times in (hours, minutes)
Tbell_times = [
    (8, 55),
    (10, 8),
    (10, 30),
    (11, 43),
    (12, 58),
    (13, 40),
    (14, 53),
    (16, 13),
    (24 + 8, 55),  # next day
]
# for friday
Tbell_timesF = [
    (8, 55),
    (10, 8),
    (10, 30),
    (11, 43),
    (12, 15),
    (13, 28),
    (14, 10),
    (15, 23),
    (3 * 24 + 8, 55),  # next week
]

classes = [
    [  # week A
        [7, 0, 4, 5, 0, 1, 6],  # M
        [3, 0, 4, 2, 0, 7, 0],  # T
        [6, 0, 2, 1, 0, 3, 0],  # W
        [5, 0, 1, 4, 0, 7, 0],  # T
        [6, 0, 2, 8, 3, 0, 5],  # F
    ],
    [  # week B
        [3, 0, 5, 2, 0, 6, 1],  # M
        [6, 0, 3, 4, 0, 7, 0],  # T
        [4, 0, 1, 5, 0, 2, 0],  # W
        [1, 0, 5, 3, 0, 7, 0],  # T
        [7, 0, 2, 8, 4, 0, 6],  # F
    ],
]


def hours2seconds(hours: int, minutes: int) -> float:
    return hours * 3600 + minutes * 60


def time2seconds(Ttime: time.struct_time) -> float:
    # converts time in hours to seconds of the day
    return Ttime.tm_hour * 3600 + Ttime.tm_min * 60 + Ttime.tm_sec + time.time() % 1


def seconds2hours(secs: float) -> float:
    # converts time in seconds of the day to hours
    return list(map(math.floor, ((secs / 3600, (secs % 3600) / 60, secs % 60))))


def get_time_seconds() -> float:
    # gets the number of seconds since the start of the day
    curr_time = time.localtime()
    return time2seconds(curr_time)


def get_day() -> int:
    curr_time = time.localtime()
    return curr_time.tm_wday


def get_next_bell():
    # if num return the index of the bell not the bell time
    Stime = get_time_seconds()
    if get_day() == 4:
        return min(x for x in Sbell_timesF if x > Stime)
    return min(x for x in Sbell_times if x > Stime)

day_seconds = 60*60*24
def get_time_to_next_bell():
    if get_day() == 5:
        return Sbell_times[-1] - get_time_seconds() + day_seconds
    if get_day() == 6:
        return Sbell_times[-1] - get_time_seconds()
    return get_next_bell() - get_time_seconds()


this_file = os.path.dirname(os.path.abspath(__file__))
subjects_file = os.path.join(
    this_file, "subjects.yaml"
)
with open(subjects_file) as f:
    lines = yaml.load(f, Loader=yaml.FullLoader)

def get_classes(day, week, raw=False):
    prefix = ""
    if day >= 5: # if tomorrow on a weeked
        day = 0
        week = not week
        if day != 7: # 7 means monday the next week
            prefix = "That day is a weekend, classes on monday: "
        
    return prefix + format_list(classes[week][day], raw)

# the monday of this terms first week
# in days since the start of the year
zero_time = time.gmtime(0)
t1 = time.strptime("25 Apr", "%d %b").tm_yday
term_starts = [t1]
term_start = max(x for x in term_starts if x <= time.localtime().tm_yday)
def get_term_week() -> int:
    return (time.localtime().tm_yday - term_start) // 7


def get_week() -> int:
    # 0 A
    # 1 B
    return get_term_week() % 2


def format_list(classes, truncate=False):
    new_classes = [lines["subjects"][x] for x in classes if x != 0]
    if truncate:
        new_classes = [x[:4] for x in new_classes]
    return ", ".join(new_classes[:-1]) + " and " + new_classes[-1]

def format_table(classes, truncate=False):
    new_classes = [lines["subjects"][x] for x in classes if x != 0]
    if truncate:
        new_classes = [x[:5] for x in new_classes]
    # new_classes = [x.center(10) for x in new_classes]
    return " | ".join(new_classes)

def get_bells(day):
    if day == 4:
        return format_list( [seconds2hours(x) for x in Tbell_timesF] )
    else:
        return Tbell_times


Sbell_times = [
    hours2seconds(*x) for x in Tbell_times
]  # times in seconds since start of day
# the * does positional unpacking
Sbell_timesF = [
    hours2seconds(*x) for x in Tbell_timesF
]  # times in seconds since start of day

if lines["exceptions"] != None:
    for i in lines["exceptions"]:
        classes[i[0]][i[1]][i[2]] = i[3]

parser = argparse.ArgumentParser(description="Help with class times")
parser.add_argument(
    "--today",
    dest="today",
    action="store_const",
    const=True,
    default=False,
    help="Shows classes for today, default",
)

parser.add_argument(
    "--tomorrow",
    "-t",
    dest="tomorrow",
    action="store_const",
    const=True,
    default=False,
    help="Shows classes for tomorrow",
)

parser.add_argument(
    "--timetable",
    "-s",
    dest="timetable",
    action="store_const",
    const=True,
    default=False,
    help="Opens the timetable pdf and bell times img",
)

parser.add_argument(
    "--top_bar",
    dest="top_bar",
    action="store_const",
    const=True,
    default=False,
    help="Updates the sys tray"
)

parser.add_argument(
    "--loop",
    dest="loop",
    action="store_const",
    const=True,
    default=False,
    help="Runs itself in a loop every second"
)

def handleArgs(args, redraw=True):
    if args.today or (not args.top_bar and not args.tomorrow and not args.timetable):
        print(f"Classes for today: {get_classes(get_day(), get_week())}")

    if args.tomorrow:
        print(f"Classes for tomorrow: {get_classes(get_day()+1, get_week())}")
    
    next_class = seconds2hours(get_time_to_next_bell())

    if args.timetable:
        bells_file = os.path.join(this_file, "bells.png")
        timetable_file = os.path.join(this_file, "timetable.pdf")
        os.system(f"xdg-open {bells_file}")
        os.system(f"xdg-open {timetable_file}")

    if args.top_bar:
        # only update timetable occasionaly
        if redraw:
            week = get_week()
            day = get_day()
            if day >= 5:
                day = 0
                week = not week
            pictureObj.create_popup(f"{format_table(classes[week][day])}")
        next_class_time = seconds2hours(get_time_to_next_bell())
        next_class_text = f"Next class: {next_class_time[0]}h {next_class_time[1]}m {next_class_time[2]}s"
        pictureObj.set_text(next_class_text)
        # os.system('gdbus call --session --dest org.gnome.Shell --object-path /com/soutade/GenericMonitor --method com.soutade.GenericMonitor.notify \'{"group":"new","items":[{"name":"first","text":"'+next_class_text+'","style":"color:white"}]}\' >/dev/null 2>&1')
    else:
        print(f"Next class in {next_class[0]}h {next_class[1]}m {next_class[2]}s")



if __name__ == "__main__":

    args = parser.parse_args()
    if args.top_bar:
        import topbarSetter.picture as p
        pictureObj = p.PicturePopup()
        pictureObj.create_popup("Loading...")
        pictureObj.set_text("set by timetabler")
        def signal_handler(sig, frame):
            pictureObj.deleteGroups(['PicturePopup'])
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    if args.loop:
        counter = 0
        while True:
            error = time.time()%1
            time.sleep(1-error)
            # re calculate timetable every minute
            handleArgs(args, counter > 60)
            if counter > 60: counter = 0
            counter += 1
    else:
        handleArgs(args)
