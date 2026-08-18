from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from mainAuth.models import CustomUser
# from trainer.models import  Course ,LiveSessionDetails 
from django.contrib.contenttypes.fields import GenericRelation


class Rating(models.Model):
    RATE_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    rate_value = models.IntegerField(choices=RATE_CHOICES)
    limit = models.Q(app_label='trainer', model='course') | \
            models.Q(app_label='trainer', model='livesessiondetails') | \
            models.Q(app_label='mainAuth', model='customuser')
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=limit,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course_rating = GenericRelation('trainer.Course', related_query_name='ratings')


    def __str__(self):
        return f'{self.content_type} rated {self.rate_value} stars'

    class Meta:
        unique_together = ('user', 'object_id', 'content_type')
