from dataclasses import dataclass


NAME_POSITION_START_X = 375
NAME_POSITION_START_Y = 310
NAME_POSITION_OFFSET = 31

ATTENDANCE_ICON_START_X: int = 595
ATTENDANCE_ICON_OFFSET_X: int = 72

ABSENSE_ICON_OFFSET_Y: int = 72

CLICK_DELAY = 0.5
LOAD_DELAY = 18
SAVE_DELAY = 20

OFF_SCREEN_CLEAR_X: int =600
OFF_SCREEN_CLEAR_Y: int = 100

# Field where you can click and manually put in the date
CALENDAR_TEXT_FIELD_X: int = 345
CALENDAR_TEXT_FIELD_Y: int = 175

LOAD_ICON_X: int = 620
LOAD_ICON_Y: int = 175

SAVE_ICON_X: int = 280
SAVE_ICON_Y: int = 1050


# These are the hours where you right click to set the attendance for the hour
HOUR_OFFSET: int = 75
HOUR_START_X: int = 570
HOUR_START_Y: int = 280

HOUR_MARK_ALL_PRESENT_OFFSET_X: int = 50
HOUR_MARK_ALL_PRESENT_OFFSET_Y: int = 15

NUM_HOURS: int = 4


@dataclass
class PartialAttendanceRecord:
    name: str
    num_hours: int


@dataclass
class Coord:
    x: int
    y: int


@dataclass
class Hour:
    hour: str
    coord: Coord


# These are the hours where you right click to set the attendance for the hour
HOURS: list[Hour] = [Hour(hour=f"hour_{i}", coord=Coord(x=HOUR_START_X + (HOUR_OFFSET * i), y=HOUR_START_Y)) for i in range(NUM_HOURS)]