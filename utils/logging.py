import datetime


def get_formatted_timestamp_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


