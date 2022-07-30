from django.core.exceptions import ObjectDoesNotExist

from meetups.models import Event, Section, Visitor, Question


def get_active_events():
    return Event.objects.filter(is_closed=False)


def get_event_with_sections(event_id):
    event = Event.objects.get(pk=event_id)
    sections = Section.objects.filter(event=event)

    event_with_sections = {
        'event': event,
        'sections': sections
    }

    return event_with_sections


def get_section_with_speakers(section_id):
    section = Section.objects.get(pk=section_id)
    speakers = section.speaker.all()

    section_with_speakers = {
        'section': section,
        'speakers': speakers
    }

    return section_with_speakers


def save_question(section_id, visitor_id, question):
    try:
        section = Section.objects.get(pk=section_id)
        visitor = Visitor.objects.get(pk=visitor_id)
    except ObjectDoesNotExist:
        return False

    question = Question.objects.create(
        section=section,
        visitor=visitor,
        question=question
    )

    if not question:
        return False

    return True
