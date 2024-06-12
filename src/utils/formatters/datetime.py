from datetime import datetime


def to_date(date_str):
    if not date_str  == "null":
        return None
    try:
        return datetime.strptime(date_str, "%d%m%Y").date()
    except ValueError:
        return None

def to_datetime_iso(date):
    if date:
        return date.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


# Function to calculate the difference between two dates
def get_datetime_difference(start_date, end_date):
    if not start_date or not end_date:
        return None
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        difference = end_date - start_date

        return difference.days
    
    except ValueError:
        return None

# Function to convert date time into different units
def to_datetime_unit(difference, unit = 'D'):
    if not difference:
        return None
    try:
        if unit == "Y":
            return difference // 365
        elif unit == "M":
            return difference // 30
        elif unit == "W":
            return difference // 7
        else:
            return difference
    except ValueError:
        return None