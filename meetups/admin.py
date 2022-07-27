from django.contrib import admin

from meetups.models import Event, Section, Speaker, Visitor, Question


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('event', 'title', 'start_date', 'start_time', 'end_time')


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'get_sections')

    def get_sections(self, obj):
        return "\n".join([s.title for s in obj.section.all()])
    get_sections.short_description = 'Блок мероприятия'


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass
