from django.db import models


class Event(models.Model):
    """
    Мероприятия
    """
    title = models.Model(verbose_name='Заголовок', db_index=True)
    start_date = models.DateField(verbose_name='Дата начала', db_index=True)
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return self.title


class Section(models.Model):
    """
    Блоки мероприятия
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sections')
    title = models.Model(verbose_name='Заголовок', db_index=True)
    start_date = models.DateField(verbose_name='Дата начала', db_index=True)
    start_time = models.TimeField(verbose_name='Время начала', db_index=True)
    end_time = models.TimeField(verbose_name='Время завершения', db_index=True)
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'

    def __str__(self):
        return self.title


class Speaker(models.Model):
    """
    Спикеры
    """
    section = models.ManyToManyField(Section, related_name='speakers')
    firstname = models.CharField(verbose_name='Имя', db_index=True)
    lastname = models.CharField(verbose_name='Фамилия', db_index=True)
    telegram_id = models.CharField(verbose_name='Telegram ID', db_index=True)

    class Meta:
        verbose_name = 'Спикер'
        verbose_name_plural = 'Спикеры'

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Visitor(models.Model):
    """
    Посетители, гости
    """
    firstname = models.CharField(verbose_name='Имя', db_index=True)
    lastname = models.CharField(verbose_name='Фамилия', db_index=True)
    company = models.CharField(verbose_name='Компания', db_index=True)
    position = models.CharField(verbose_name='Должность', db_index=True)
    phone_number = models.CharField(verbose_name='Телефон', db_index=True)
    email = models.EmailField(verbose_name='Email', db_index=True)
    telegram_id = models.CharField(verbose_name='Telegram ID', db_index=True)
    about_oneself = models.TextField(verbose_name='О себе')

    class Meta:
        verbose_name = 'Посетитель'
        verbose_name_plural = 'Посетители'

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Question(models.Model):
    """
    Вопросы гостей спикерам
    """
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions')
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField(verbose_name='Вопрос', db_index=True)
    answer = models.TextField(verbose_name='Ответ', db_index=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.pk
