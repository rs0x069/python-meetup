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


def save_question(section_id, visitor_id, speaker_id, question):
    try:
        section = Section.objects.get(pk=section_id)
        visitor = Visitor.objects.get(telegram_id=visitor_id)
        speaker = Visitor.objects.get(pk=speaker_id)
    except ObjectDoesNotExist:
        return False

    question = Question.objects.create(
        section=section,
        visitor=visitor,
        speaker=speaker,
        question=question
    )

    if not question:
        return False

    return question, speaker


def get_questions(speaker_id):
    try:
        speaker = Visitor.objects.get(telegram_id=speaker_id)
    except ObjectDoesNotExist:
        return False

    questions = speaker.speaker_questions.filter(answer='')

    return questions


def get_question(question_id, speaker_id):
    try:
        speaker = Visitor.objects.get(telegram_id=speaker_id)
        question = Question.objects.get(pk=question_id)
    except ObjectDoesNotExist:
        return False

    if not question.speaker.pk == speaker.pk:
        return False

    return question


def answer_question(question_id, speaker_id, answer):
    try:
        speaker = Visitor.objects.get(telegram_id=speaker_id)
        question = Question.objects.get(pk=question_id)
    except ObjectDoesNotExist:
        return False

    if not question.speaker.pk == speaker.pk:
        return False

    question.answer = answer
    question.save()

    return speaker, question.visitor, question
