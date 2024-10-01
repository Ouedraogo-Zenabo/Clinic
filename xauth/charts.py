from django.db import models as dj_models, transaction
from web.views import CustomBaseLineOptionsChartView

from xauth.models import User


class SubscriptionByGenderChartView(CustomBaseLineOptionsChartView):

    def get_queryset(self):
        if hasattr(self.request.user, "assign"):
            structures = self.request.user.assign.structure.get_children()
        elif self.request.user.is_staff:
            structures = User.objects.all()
        else:
            structures = User.objects.none()
        data = (
            User.objects.filter(
                structure__in=structures,
            )
            .values("gender")
            .annotate(total=dj_models.Count("gender"))
            .order_by("gender")
        )
        data = list(data)

        return data

    def get_labels_value(self, label):
        return label

    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return [self.get_labels_value(datum["gender"]) for datum in self.get_queryset()]

    def get_providers(self):
        """Return names of datasets."""
        return ["Nombre de militaire"]

    def get_title(self):
        return "Nombre de militaire par genre"

    def get_data(self):
        """Return 3 datasets to plot."""
        return [[datum["total"] for datum in self.get_queryset()]]
