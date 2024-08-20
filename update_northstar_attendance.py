from dataclasses import dataclass
from time import sleep

import pandas as pd
from pandas.core.groupby.generic import DataFrameGroupBy
import pyautogui as pag


@dataclass
class Coord:
    x: int
    y: int


@dataclass
class Hour:
    hour: str
    coord: Coord

@dataclass
class PartialAttendanceRecord:
    name: str
    num_hours: int


# Read in spreadsheet and group by date
df = pd.read_excel("attendance.xlsx")
attendance_groups: DataFrameGroupBy = df.groupby("AttendDate")

name_position_start: Coord = Coord(x=375, y=310)
name_position_offset = 31

attendance_icon_start_x: int = 595
attendance_icon_offset_x: int = 72

absense_icon_offset_y: int = 72

click_delay = 0.2
load_delay = 6
save_delay = 10

off_screen_clear: Coord = Coord(x=600, y=100)

# Icons
calendar_icon: Coord = Coord(x=375, y=175)
load_icon: Coord = Coord(x=610, y=175)
save_icon: Coord = Coord(x=280, y=1050)

# Field where you can click and manually put in the date
calendar_text_field_offset: int = 30
calendar_text_field: Coord = Coord(x=calendar_icon.x - calendar_text_field_offset, y=calendar_icon.y)

# First day on the calendar
calendar_start: Coord = Coord(x=380, y=245)

calendar_day_offset_pixels_x: int = 29
calendar_day_offset_pixels_y: int = 21

# These are the hours where you right click to set the attendance for the hour
hour_offset: int = 75
hour_start: Coord = Coord(x=570, y=280)
hour_mark_all_present_offset_x: int = 50
hour_mark_all_present_offset_y: int = 15

hours: list[Hour] = [
    Hour(
        hour="hour_1", coord=Coord(x=hour_start.x + (hour_offset * 0), y=hour_start.y)
    ),
    Hour(
        hour="hour_2", coord=Coord(x=hour_start.x + (hour_offset * 1), y=hour_start.y)
    ),
    Hour(
        hour="hour_3", coord=Coord(x=hour_start.x + (hour_offset * 2), y=hour_start.y)
    ),
    Hour(
        hour="hour_4", coord=Coord(x=hour_start.x + (hour_offset * 3), y=hour_start.y)
    ),
]


def click(right_click: bool = False) -> None:
    button: str = pag.PRIMARY if not right_click else pag.SECONDARY

    sleep(click_delay)
    pag.click(button=button)
    sleep(click_delay)


def clear() -> None:
    """ Clicks off screen to clear the calendar or anything else that might be pulled up. """
    pag.moveTo(off_screen_clear.x, off_screen_clear.y)
    click()


def save() -> None:
    clear()
    pag.moveTo(save_icon.x, save_icon.y)
    click()
    sleep(save_delay)


def load() -> None:
    """ Clicks the load icon, then waits a little bit for the page to load """
    pag.moveTo(load_icon.x, load_icon.y)
    click()

    # 6 second load time might be excessive, but it should always be enough.
    # A couple of my tests got fairly close to 5 seconds, though on average it
    # took ~3 seconds.
    sleep(load_delay)


def go_to_date(date: str) -> None:
    """
    Goes to the specified date.

    @param date: The date in the format "YYYY-MM-DD"
    """
    clear()

    pag.moveTo(calendar_text_field.x, calendar_text_field.y)
    click()

    # Clear out the text
    pag.hotkey("command", "a")

    # Type in the date
    pag.typewrite(date)

    pag.press("enter")

    load()


def set_all_present() -> None:
    """ Sets everyone to present for the current selected day. """
    clear()
    for hour in hours:
        pag.moveTo(hour.coord.x, hour.coord.y)
        click(right_click=True)

        pag.moveTo(
            hour.coord.x + hour_mark_all_present_offset_x,
            hour.coord.y + hour_mark_all_present_offset_y,
        )

        click()


def get_partial_attendance_list(group: DataFrameGroupBy) -> list[PartialAttendanceRecord]:
    """ Returns a list of PartialAttendanceRecord objects for the given date. """
    partial_attendance_group = group[group["Hours Attended"] < 4]
    return [(row["name"], row["Hours Attended"]) for _, row in partial_attendance_group.iterrows()]


def set_partial_attendance(student: str, num_hours: int, name_positions: dict[str, Coord]) -> None:
    """ Sets the number of absenses for the selected day."""
    clear()
    for hour in range(4 - num_hours):
        pag.moveTo(attendance_icon_start_x + (hour * attendance_icon_offset_x), name_positions[student].y)
        click()

        pag.moveTo(attendance_icon_start_x + (hour * attendance_icon_offset_x), name_positions[student].y + absense_icon_offset_y)
        click()

def set_attendance_for_date(group: DataFrameGroupBy, date: str) -> None:
    """ Sets the attendance for the specified date. """
    go_to_date(date)
    set_all_present()

    # Get list of students for the date and create the student: position map
    names: list[str] = sorted([name for name in group.name], key=lambda name: name.split()[-1])
    name_positions: dict[str, Coord] = {name: Coord(x=name_position_start.x, y=name_position_start.y + (name_position_offset * i)) for i, name in enumerate(names)}


    partial_attendance_list: list[PartialAttendanceRecord] = get_partial_attendance_list(group)
    for student, num_hours in partial_attendance_list:
        set_partial_attendance(student, num_hours, name_positions)


def test_icons() -> None:
    sleep(2)
    pag.moveTo(off_screen_clear.x, off_screen_clear.y)
    sleep(1)
    pag.moveTo(calendar_icon.x, calendar_icon.y)
    sleep(1)
    pag.moveTo(load_icon.x, load_icon.y)
    sleep(1)
    pag.moveTo(save_icon.x, save_icon.y)
    sleep(1)


def test_attendance_arrow_icons() -> None:
    sleep(2)

    name1 = "Christopher Cooley"
    name2 = "Mathew Zamacona"

    for i in range(4):
        pag.moveTo(attendance_icon_start_x + (i * attendance_icon_offset_x), name_positions[name1].y)
        sleep(1)

    for i in range(4):
        pag.moveTo(attendance_icon_start_x + (i * attendance_icon_offset_x), name_positions[name2].y)
        sleep(1)


def test_hours() -> None:
    sleep(2)
    for hour in hours:
        pag.moveTo(hour.coord.x, hour.coord.y)
        sleep(1)


def test_days() -> None:
    """ This relies on the calendar being open. """
    sleep(2)
    pag.moveTo(calendar_start.x, calendar_start.y)
    sleep(1)

    for i in range(5):
        pag.moveTo(
            calendar_start.x + (calendar_day_offset_pixels_x * i),
            calendar_start.y + (calendar_day_offset_pixels_y * i),
        )
        sleep(1)


def test_all() -> None:
    """ Just a way to test mouse positions """
    test_icons()
    test_hours()
    test_days()
    test_attendance_arrow_icons()


def main():
    # Give time to switch to RDP tab
    sleep(2)

    for date, group in attendance_groups:
        set_attendance_for_date(group, date.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    main()
