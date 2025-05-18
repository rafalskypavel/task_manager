from django.db import models

class Task(models.Model):
    class Status(models.TextChoices):
        DONE = 'done', 'Выполнено'
        UNDONE = 'undone', 'Не выполнено'

    title = models.CharField(null=False,
                             blank=False,
                             max_length=255,
                             verbose_name='Название задачи')
    description = models.TextField(blank=True,
                                   verbose_name='Описание')
    deadline = models.DateTimeField(null=False,
                                    blank=False,
                                    verbose_name='Срок выполнения')
    telegram_user_id = models.IntegerField(verbose_name='ID пользователя Telegram')
    status = models.CharField(
        max_length=6,
        choices=Status.choices,
        default=Status.UNDONE,
        verbose_name='Статус'
    )
    notification_sent = models.BooleanField(default=False,
                                            verbose_name='Уведомление отправлено')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['deadline']

    def __str__(self):
        return f'#{self.id} {self.title} ({self.get_status_display()})'