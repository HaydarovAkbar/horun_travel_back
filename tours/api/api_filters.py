import django_filters as df
from tours.models import Tour

class TourFilter(df.FilterSet):
    price_min = df.NumberFilter(field_name="price_after_discount", lookup_expr="gte")
    price_max = df.NumberFilter(field_name="price_after_discount", lookup_expr="lte")
    days_min  = df.NumberFilter(field_name="days", lookup_expr="gte")
    days_max  = df.NumberFilter(field_name="days", lookup_expr="lte")
    category  = df.NumberFilter(field_name="category__id")
    tag       = df.NumberFilter(field_name="tags__id")
    country   = df.NumberFilter(field_name="tour_stops__country__id")
    city      = df.NumberFilter(field_name="tour_stops__city__id")
    featured  = df.BooleanFilter(field_name="is_featured")
    status    = df.CharFilter(field_name="status")

    class Meta:
        model = Tour
        fields = []
