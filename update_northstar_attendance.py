from dataclasses import dataclass
import pyautogui as pag
from time import sleep


@dataclass
class Coord:
    x: int
    y: int


@dataclass
class Hour:
    hour: str
    coord: Coord


click_delay = 0.2
load_delay = 6
save_delay = 10

off_screen_clear: Coord = Coord(x=600, y=100)

calendar_icon: Coord = Coord(x=375, y=175)
load_icon: Coord = Coord(x=610, y=175)
save_icon: Coord = Coord(x=280, y=1050)

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
    """Clicks off screen to clear the calendar or anything else that might be pulled up."""
    pag.moveTo(off_screen_clear.x, off_screen_clear.y)
    click()


def save() -> None:
    clear()
    pag.moveTo(save_icon.x, save_icon.y)
    click()
    sleep(save_delay)


def load() -> None:
    """Clicks the load icon, then waits a little bit for the page to load"""
    pag.moveTo(load_icon.x, load_icon.y)
    click()

    # 6 second load time might be excessive, but it should always be enough.
    # A couple of my tests got fairly close to 5 seconds, though on average it
    # took ~3 seconds.
    sleep(load_delay)


def load_day(day: int, week: int) -> None:
    """Loads a specific day. Note that `day` is 0 based, so day 0 is the Monday of the top week."""
    clear()

    pag.moveTo(calendar_icon.x, calendar_icon.y)
    click()

    pag.moveTo(
        calendar_start.x + (calendar_day_offset_pixels_x * day),
        calendar_start.y + (calendar_day_offset_pixels_y * week),
    )
    click()

    load()


def set_week_attendance(week: int) -> None:
    """Sets the attendance for the whole week"""
    for i in range(5):
        load_day(day=i, week=week)
        set_all_present()
        save()


def set_all_present() -> None:
    """Sets everyone to present for the current selected day."""
    for hour in hours:
        clear()
        pag.moveTo(hour.coord.x, hour.coord.y)
        click(right_click=True)

        pag.moveTo(
            hour.coord.x + hour_mark_all_present_offset_x,
            hour.coord.y + hour_mark_all_present_offset_y,
        )

        click()
        sleep(0.5)


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


def test_hours() -> None:
    sleep(2)
    for hour in hours:
        pag.moveTo(hour.coord.x, hour.coord.y)
        sleep(1)


def test_days() -> None:
    """This relies on the calendar being open."""
    sleep(2)
    pag.moveTo(calendar_start.x, calendar_start.y)
    sleep(1)

    for i in range(5):
        pag.moveTo(
            calendar_start.x + (calendar_day_offset_pixels_x * i),
            calendar_start.y + (calendar_day_offset_pixels_y * i),
        )
        sleep(1)


def test_positions() -> None:
    """Just a way to test mouse positions"""
    test_icons()
    test_hours()
    test_days()


def main():
    # Give time to switch to RDP tab
    sleep(2)

    # load_day(day=0, week=3)
    # set_all_present()

    set_week_attendance(3)


if __name__ == "__main__":
    main()
