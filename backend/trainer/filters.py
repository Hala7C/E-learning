import django_filters
from django.db.models import Q
from .models import Course

class CourseFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(method='filter_title')
    content = django_filters.CharFilter(method='filter_content')

    class Meta:
        model = Course
        fields = {
            'trainer__id': ['exact'],
            'category__id': ['exact'],
        }

    def filter_title(self, queryset, name, value):
        return queryset.filter(translations__title__icontains=value)

    def filter_content(self, queryset, name, value):
        return queryset.filter(translations__content__icontains=value)
