from meetups.models import Event, Section, Visitor, Question


def get_active_events():
    return Event.objects.filter(is_closed=False)


def get_event_info_with_section(event_id):
    event = Event.objects.get(pk=event_id)
    return event


# from meetups.views import *