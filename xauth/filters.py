import django_filters

from xauth.models import User


class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["structure"]
