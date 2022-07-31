from django.contrib import admin

from meetups.models import Event, Section, Visitor, Question


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'start_time', 'end_time')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'speaker':
            kwargs['queryset'] = Visitor.objects.filter(is_speaker=True)
        return super(SectionAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'is_speaker', 'lastname', 'email')
    list_filter = ('is_speaker',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass
