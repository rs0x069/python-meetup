from environs import Env
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path
from telegram import Bot, error as telegram_error

from meetups.models import Event, Section, Visitor, Question


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'start_time', 'end_time')
    ordering = ('event__start_date', 'title', 'event', 'start_time')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'speaker':
            kwargs['queryset'] = Visitor.objects.filter(is_speaker=True)
        return super(SectionAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'is_speaker', 'lastname', 'email')
    list_filter = ('is_speaker',)
    change_list_template = "admin/visitor_change_list.html"

    env = Env()

    telegram_token = env("TELEGRAM_TOKEN")
    telegram_bot = Bot(token=telegram_token)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send_to_telegram/', self.mass_sending_to_telegram),
        ]
        return custom_urls + urls

    def mass_sending_to_telegram(self, request):
        visitors = self.model.objects.all().values('telegram_id')
        telegram_message = request.POST['telegram_message']
        messages_error = []

        for visitor in visitors:
            try:
                self.telegram_bot.send_message(chat_id=visitor['telegram_id'], text=telegram_message)
            except telegram_error.TelegramError as err:
                messages_error.append(f"{visitor['telegram_id']}: {err}")

        messages.success(request, f'Рассылка завершена')

        if messages_error:
            messages.error(request, f'Сообщение не отправлено: {messages_error}')
        else:
            messages.success(request, 'Сообщение отправлено всем')

        return HttpResponseRedirect('../')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass
