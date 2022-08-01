from django.db import models


class Event(models.Model):
    """
    Мероприятия
    """
    title = models.CharField(max_length=64, verbose_name='Заголовок', db_index=True)
    start_date = models.DateField(verbose_name='Дата начала', db_index=True)
    description = models.TextField(verbose_name='Описание')
    is_closed = models.BooleanField(default=0, verbose_name='Закрыто')

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return self.title


class Visitor(models.Model):
    """
    Посетители, гости. Могут быть спикерами
    """
    firstname = models.CharField(max_length=32, verbose_name='Имя', db_index=True)
    lastname = models.CharField(max_length=32, verbose_name='Фамилия', db_index=True)
    company = models.CharField(max_length=64, blank=True, verbose_name='Компания', db_index=True)
    position = models.CharField(max_length=64, blank=True, verbose_name='Должность', db_index=True)
    phone_number = models.CharField(max_length=16, blank=True, verbose_name='Телефон', db_index=True)
    email = models.EmailField(max_length=32, blank=True, verbose_name='Email', db_index=True)
    telegram_id = models.CharField(max_length=16, verbose_name='Telegram ID', unique=True)
    about_oneself = models.TextField(blank=True, verbose_name='О себе')
    is_speaker = models.BooleanField(default=0, verbose_name='Спикер')

    class Meta:
        verbose_name = 'Посетитель'
        verbose_name_plural = 'Посетители'

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Section(models.Model):
    """
    Блоки мероприятия
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие', related_name='sections')
    speaker = models.ManyToManyField(Visitor, verbose_name='Спикер', related_name='section_speakers')
    title = models.CharField(max_length=64, verbose_name='Заголовок', db_index=True)
    start_time = models.TimeField(verbose_name='Время начала', db_index=True)
    end_time = models.TimeField(verbose_name='Время завершения', db_index=True)
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Вопросы гостей спикерам
    """
    section = models.ForeignKey(Section, verbose_name='Блок мероприятия', on_delete=models.CASCADE,
                                related_name='questions')
    visitor = models.ForeignKey(Visitor, verbose_name='Посетитель', on_delete=models.CASCADE, related_name='questions')
    speaker = models.ForeignKey(Visitor, on_delete=models.CASCADE, verbose_name='Спикер', related_name='speaker_questions')
    question = models.TextField(verbose_name='Вопрос', db_index=True)
    answer = models.TextField(verbose_name='Ответ', blank=True, db_index=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.question
