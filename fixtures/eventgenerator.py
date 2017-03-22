from datetime import datetime, date, time, timedelta
import random
import sys
import os
import json

# Costant
creator_id = 1  # Pk of user fixture-loader
start_time = [time(14, 0), time(16, 0), time(18, 0)]


class Event:
    # Status choices
    APPROVED = 0
    WAITING = 1
    REJECTED = 2
    STATUS_CHOICES = [
        (APPROVED, "Approved"),
        (WAITING, "Waiting"),
        (REJECTED, "Rejected"),
    ]

    def __init__(self, pk, room_id, activity_id, start, end, status, creator_id):
        self.pk = pk
        self.room_id = room_id
        self.activity_id = activity_id
        self.start = start
        self.end = end
        self.status = status
        self.creator_id = creator_id

    def str_json(self):
        event_json = """  {{
    "model": "events.event",
    "pk": {},
    "fields": {{
      "room_id": {},
      "activity_id": {},
      "start": "{}+0100",
      "end": "{}+0100",
      "status": {},
      "creator_id": {}
    }}
  }}"""  # 2016-03-01 18:00:00
        return event_json.format(
            self.pk,
            self.room_id,
            self.activity_id,
            self.start,
            self.end,
            self.status,
            self.creator_id
        )


def get_hour_and_room(day, start_time_set):
    start = None
    random.shuffle(start_time)
    j = 0
    while start is None and j < len(room_ids):
        i = 0
        room_id = random.choice(room_ids)
        while start is None and i < len(start_time):
            start = datetime.combine(day, start_time[i])
            datetime_room_string = str(room_id) + start.isoformat()
            if datetime_room_string in start_time_set:
                start = None
                i += 1
        j += 1
    return (start, room_id)


def get_day_hour_and_room(days_in_period, start_time_set):
    start = None
    while start is None:
        days_to_be_added = random.randrange(days_in_period)
        day = date_interval["start"] + timedelta(days=days_to_be_added)
        while day.isoweekday() > 5:  # If it is a weekend
            days_to_be_added = random.randrange(days_in_period)
            day = date_interval["start"] + timedelta(days=days_to_be_added)
        start, room_id = get_hour_and_room(day, start_time_set)
    return (day, start, room_id)


def print_file(events):
    # Print json
    try:
        os.delete(output_file)
    except:
        pass
    try:
        with open(output_file, "w") as out_file:
            out_file.write("[\n")
            for e in events[0:-1]:
                out_file.write(e.str_json() + ",\n")
            out_file.write(events[-1].str_json() + "\n")
            out_file.write("]\n")
    except:
        print("ERROR: Error writing file.")


def get_random_events(days_in_period, number_of_events):
    # Generate random event
    events = []
    start_time_set = set()
    while len(events) < number_of_events:
        # Random date not weekend
        day, start, room_id = get_day_hour_and_room(days_in_period, start_time_set)
        start_time_set.add(str(room_id) + start.isoformat())
        activity_id = random.choice(activity_ids)
        r = random.random()
        if r < 0.7:
            status = Event.STATUS_CHOICES[0][0]
        elif r < 0.85:
            status = Event.STATUS_CHOICES[1][0]
        else:
            status = Event.STATUS_CHOICES[2][0]
        event = Event(len(events) + 1, room_id, activity_id, start, start + timedelta(hours=2),
                      status, creator_id)
        events.append(event)
    return events


def get_input():
    usage = """Random events generator

Usage: python3 eventgenerator.py <number-of-events> <from-date> <to-date>

<from-date> and <to-date> have to be in the format yyyy-mm-dd"""

    if len(sys.argv) != 4:
        print(usage)
    else:
        try:
            number_of_events = int(sys.argv[1])
            from_date = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
            to_date = datetime.strptime(sys.argv[3], "%Y-%m-%d").date()
            return number_of_events, {"start": from_date, "end": to_date}
        except:
            print(usage)


def get_room_ids():
    with open("rooms.json", "r") as source:
        rooms = json.load(source)
        room_ids = []
        for room in rooms:
            room_ids.append(room["pk"])
        return room_ids


def get_activities_ids():
    with open("activities.json", "r") as source:
        activities = json.load(source)
        activity_ids = []
        for activity in activities:
            if not activity["fields"]["archived"]:
                activity_ids.append(activity["pk"])
        return activity_ids


input_got = get_input()
if input_got:
    number_of_events, date_interval = input_got
    days_in_period = (date_interval["end"] - date_interval["start"]).days
    output_file = "events.json"
    activity_ids = get_activities_ids()
    room_ids = get_room_ids()
    print("Generating random events...")
    events = get_random_events(days_in_period, number_of_events)
    print("Saving file...")
    print_file(events)
    print("Events generated.")
