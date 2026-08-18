import django_filters
from django.db.models import Q
from .models import Transaction

class TransactionsFilter(django_filters.FilterSet):
    relatedUser = django_filters.CharFilter(method='filter_relatedUser')

    class Meta:
        model = Transaction
        fields = {
            'relatedUser': ['exact'],
    }
    def filter_relatedUser(self, queryset, name, value):
        return queryset.filter(relatedUser=value)

