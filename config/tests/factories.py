import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.contrib.contenttypes.models import ContentType
from nl_task.models import Page, Video, Audio, Content

fake = Faker()

class PageFactory(DjangoModelFactory):
    class Meta:
        model = Page
    
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))

class VideoFactory(DjangoModelFactory):
    class Meta:
        model = Video
    
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    video_url = factory.LazyAttribute(lambda _: fake.url())
    subtitle_url = factory.LazyAttribute(lambda _: fake.url())
    counter = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=100))

class AudioFactory(DjangoModelFactory):
    class Meta:
        model = Audio
    
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    text = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=5))
    counter = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=100))

class ContentFactory(DjangoModelFactory):
    class Meta:
        model = Content
    
    page = factory.SubFactory(PageFactory)
    order = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=10))
    
    @factory.lazy_attribute
    def content_type(self):
        return ContentType.objects.get_for_model(self.content_object)
    
    @factory.lazy_attribute
    def object_id(self):
        return self.content_object.id

class VideoContentFactory(ContentFactory):
    content_object = factory.SubFactory(VideoFactory)

class AudioContentFactory(ContentFactory):
    content_object = factory.SubFactory(AudioFactory)