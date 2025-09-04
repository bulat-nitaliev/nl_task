import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.contrib.contenttypes.models import ContentType
from .models import Page, Video, Audio, Text, PageContent

fake = Faker()

class PageFactory(DjangoModelFactory):
    class Meta:
        model = Page
        django_get_or_create = ('title',)  # Избегаем дубликатов
    
    title = factory.LazyAttribute(lambda _: fake.unique.sentence(nb_words=3))

class VideoFactory(DjangoModelFactory):
    class Meta:
        model = Video
        django_get_or_create = ('title',)
    
    title = factory.LazyAttribute(lambda _: fake.unique.sentence(nb_words=3))
    video_file_url = factory.LazyAttribute(lambda _: fake.unique.url())
    subtitles_file_url = factory.LazyAttribute(lambda _: fake.unique.url())

class AudioFactory(DjangoModelFactory):
    class Meta:
        model = Audio
        django_get_or_create = ('title',)
    
    title = factory.LazyAttribute(lambda _: fake.unique.sentence(nb_words=3))
    text = factory.LazyAttribute(lambda _: fake.unique.paragraph())

class TextFactory(DjangoModelFactory):
    class Meta:
        model = Text
        django_get_or_create = ('title',)
    
    title = factory.LazyAttribute(lambda _: fake.unique.sentence(nb_words=3))
    content = factory.LazyAttribute(lambda _: fake.unique.paragraph())

class PageContentFactory(DjangoModelFactory):
    class Meta:
        model = PageContent
    
    page = factory.SubFactory(PageFactory)
    order = factory.Sequence(lambda n: n)
    
    @factory.post_generation
    def set_content_object(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            self.content_object = extracted
        else:
            # Случайным образом выбираем тип контента
            content_types = [VideoFactory, AudioFactory, TextFactory]
            content_factory = fake.random_element(content_types)
            self.content_object = content_factory()
        
        # Устанавливаем content_type и object_id
        self.content_type = ContentType.objects.get_for_model(self.content_object.__class__)
        self.object_id = self.content_object.id