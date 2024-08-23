import signal
import sys
from time import sleep, time

import pandas as pd
from pandas.core.groupby.generic import DataFrameGroupBy
import pyautogui as pag

from offsets import *


def click(right_click: bool = False) -> None:
    button: str = pag.PRIMARY if not right_click else pag.SECONDARY

    sleep(CLICK_DELAY)
    pag.click(button=button)
    sleep(CLICK_DELAY)


def clear() -> None:
    """ Clicks off screen to clear the calendar or anything else that might be pulled up. """
    pag.moveTo(OFF_SCREEN_CLEAR_X, OFF_SCREEN_CLEAR_Y)
    click()


def save() -> None:
    clear()
    pag.moveTo(SAVE_ICON_X, SAVE_ICON_Y)
    click()
    sleep(SAVE_DELAY)


def load() -> None:
    """ Clicks the load icon, then waits a little bit for the page to load """
    pag.moveTo(LOAD_ICON_X, LOAD_ICON_Y)
    click()

    # 6 second load time might be excessive, but it should always be enough.
    # A couple of my tests got fairly close to 5 seconds, though on average it
    # took ~3 seconds.
    sleep(LOAD_DELAY)


def go_to_date(date: str) -> None:
    """
    Goes to the specified date.

    @param date: The date in the format "YYYY-MM-DD"
    """
    clear()

    pag.moveTo(CALENDAR_TEXT_FIELD_X, CALENDAR_TEXT_FIELD_Y)
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
    for hour in HOURS:
        pag.moveTo(hour.coord.x, hour.coord.y)
        click(right_click=True)

        pag.moveTo(
            hour.coord.x + HOUR_MARK_ALL_PRESENT_OFFSET_X,
            hour.coord.y + HOUR_MARK_ALL_PRESENT_OFFSET_Y,
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
        pag.moveTo(ATTENDANCE_ICON_START_X + (hour * ATTENDANCE_ICON_OFFSET_X), name_positions[student].y)
        click()

        pag.moveTo(ATTENDANCE_ICON_START_X + (hour * ATTENDANCE_ICON_OFFSET_X), name_positions[student].y + ABSENSE_ICON_OFFSET_Y)
        click()


def set_attendance_for_date(group: DataFrameGroupBy, date: str) -> None:
    """ Sets the attendance for the specified date. """
    go_to_date(date)
    set_all_present()

    # Get list of students for the date and create the student: position map
    name_positions = get_name_positions(sorted([name for name in group.name], key=lambda name: name.split()[-1]))

    partial_attendance_list: list[PartialAttendanceRecord] = get_partial_attendance_list(group)
    for student, num_hours in partial_attendance_list:
        set_partial_attendance(student, num_hours, name_positions)

    save()


def get_name_positions(names: list[str]) -> dict[str, Coord]:
    return {name: Coord(x=NAME_POSITION_START_X, y=NAME_POSITION_START_Y + (NAME_POSITION_OFFSET * i)) for i, name in enumerate(names)}


def test_icons() -> None:
    sleep(2)
    pag.moveTo(OFF_SCREEN_CLEAR_X, OFF_SCREEN_CLEAR_Y)
    sleep(1)
    pag.moveTo(CALENDAR_TEXT_FIELD_X, CALENDAR_TEXT_FIELD_Y)
    sleep(1)
    pag.moveTo(LOAD_ICON_X, LOAD_ICON_Y)
    sleep(1)
    pag.moveTo(SAVE_ICON_X, SAVE_ICON_Y)
    sleep(1)


def test_attendance_arrow_icons() -> None:
    sleep(2)

    name1 = "Christopher Cooley"
    name2 = "Mathew Zamacona"

    for hour in range(4):
        pag.moveTo(ATTENDANCE_ICON_START_X + (hour * ATTENDANCE_ICON_OFFSET_X), name_positions[name1].y)
        sleep(1)

    for hour in range(4):
        pag.moveTo(ATTENDANCE_ICON_START_X + (hour * ATTENDANCE_ICON_OFFSET_X), name_positions[name2].y)
        sleep(1)


def test_hours() -> None:
    """ Tests the location of where you'd right click to mark all present. """
    sleep(2)
    for hour in HOURS:
        pag.moveTo(hour.coord.x, hour.coord.y)
        sleep(1)


def test_all() -> None:
    """ Just a way to test mouse positions """
    test_icons()
    test_hours()
    test_attendance_arrow_icons()


def signal_handler(signal: int, frame) -> None:
    print(f"Time spent: {time() - start}")
    sys.exit(0)


start = time()
def main():
    if len(sys.argv) != 2:
        print("Usage: python update_northstar_attendance.py <attendance-xlsx-file>")
        sys.exit(1)

    # Read in spreadsheet and group by date
    df = pd.read_excel(sys.argv[1])
    filtered = df[df["AttendDate"] > pd.Timestamp("2024-04-25")]
    attendance_groups: DataFrameGroupBy = filtered.groupby("AttendDate")

    # Start date for when to start putting in attendance
    cutoff_date = pd.Timestamp("2024-04-25")

    # Give time to switch to RDP tab
    sleep(2)

    # Register signal handler for CTRL+C
    signal.signal(signal.SIGINT, signal_handler)

    for date, group in attendance_groups:
        set_attendance_for_date(group, date.strftime("%Y-%m-%d"))

    print(f"Finished in {time() - start} seconds")

if __name__ == "__main__":
    main()
