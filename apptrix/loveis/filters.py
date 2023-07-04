import django_filters
from .models import Client


class ClientFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    gender = django_filters.ChoiceFilter(choices=Client.gender_choices)

    class Meta:
        model = Client
        fields = ["gender", "first_name", "last_name"]
