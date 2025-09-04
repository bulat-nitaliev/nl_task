from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ContentBase(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    counter = models.PositiveIntegerField(default=0, verbose_name="Счетчик просмотров")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, editable=False)

    def save(self, *args, **kwargs):
        if not self.content_type_id:
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.content_type.model})"

    class Meta:
        abstract = True

class Video(ContentBase):
    video_file_url = models.URLField(max_length=500, verbose_name="Ссылка на видео")
    subtitles_file_url = models.URLField(max_length=500, blank=True, verbose_name="Ссылка на субтитры")

class Audio(ContentBase):
    text = models.TextField(verbose_name="Текст")

class Text(ContentBase):
    content = models.TextField(verbose_name="Текст")

class Page(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['id']  # Добавляем сортировку по умолчанию

class PageContent(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, verbose_name="Страница")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = "Элемент контента"
        verbose_name_plural = "Элементы контента"