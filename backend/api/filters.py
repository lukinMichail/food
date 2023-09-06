# import django_filters
from rest_framework import filters
# from recipes.models import Recipe, Tag


class IngredientSearch(filters.BaseFilterBackend):
    """Поиск по вхождению в начало имени ингредиента."""

    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('name', None)
        if search_query:
            queryset = queryset.filter(name__istartswith=search_query)
        return queryset


# class RecipeFilter(django_filters.FilterSet):
#     """Фильтр для модели Recipe."""

#     author = django_filters.ModelChoiceFilter(field_name='author__id__in')
#     is_in_shopping_cart = django_filters.BooleanFilter(
#         method='get_is_in_shopping_cart'
#     )
#     is_favorited = django_filters.BooleanFilter(method='get_favorite')
#     tags = django_filters.AllValuesMultipleFilter(
#         field_name='tags__slug__in',
#         to_field_name='slug',
#         queryset=Tag.objects.all(),
#     )

#     class Meta:
#         model = Recipe
#         fields = ['author', 'tags']

    # fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
    # def get_favorite(self, queryset, name, value):
    #     if value and self.request.user.is_authenticated:
    #         return queryset.filter(favorites__user=self.request.user)
    #     return queryset

    # def get_is_in_shopping_cart(self, queryset, name, value):
    #     if value and self.request.user.is_authenticated:
    #         return queryset.filter(shopping_cart__user=self.request.user)
    #     return queryset
