"""Update the profile's age locally, without GitHub API calls or dependencies."""

import calendar
import datetime as dt
from pathlib import Path
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

BIRTHDAY = dt.date(2002, 4, 19)
SVG_NAMESPACE = "http://www.w3.org/2000/svg"


def daily_readme(birthday, today=None):
    """Return age in completed years, months and days."""
    today = today or dt.datetime.now(ZoneInfo("Asia/Karachi")).date()
    if today < birthday:
        raise ValueError("The current date must not precede the birthday")
    months = (today.year - birthday.year) * 12 + today.month - birthday.month

    def anniversary(month_count):
        year, month = divmod(birthday.year * 12 + birthday.month - 1 + month_count, 12)
        month += 1
        day = min(birthday.day, calendar.monthrange(year, month)[1])
        return dt.date(year, month, day)

    if anniversary(months) > today:
        months -= 1
    years, months_part = divmod(months, 12)
    days = (today - anniversary(months)).days
    values = [(years, "year"), (months_part, "month"), (days, "day")]
    age = ", ".join(f"{count} {unit}{'' if count == 1 else 's'}" for count, unit in values)
    return age + (" 🎂" if today.month == birthday.month and today.day == birthday.day else "")


def update_profile(path, today=None):
    """Preserve the portrait and keep the age row's existing right alignment."""
    ET.register_namespace("", SVG_NAMESPACE)
    tree = ET.parse(path)
    root = tree.getroot()
    age = root.find(".//*[@id='age_data']")
    if age is None:
        raise ValueError("Profile SVG is missing the age_data element")
    parent = next(node for node in root.iter() if age in list(node))
    dots = list(parent)[list(parent).index(age) - 1]
    if dots.get("class") != "cc":
        raise ValueError("Age element must be preceded by its alignment dots")
    new_age = daily_readme(BIRTHDAY, today)
    if age.text == new_age:
        return False
    dot_count = dots.text.count(".") + len(age.text or "") - len(new_age)
    if dot_count < 0:
        raise ValueError("Age text exceeds available row width")
    dots.text = " " + "." * dot_count + " "
    age.text = new_age
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return True


if __name__ == "__main__":
    svg = Path(__file__).resolve().with_name("dark_mode.svg")
    changed = update_profile(svg)
    print("Profile age updated." if changed else "Profile age already current.")
