# import django_filters
from rest_framework import filters
# from recipes.models import Recipe, Tag


class IngredientSearch(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('name', None)
        if search_query:
            queryset = queryset.filter(name__istartswith=search_query)
        return queryset
