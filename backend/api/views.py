from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow

from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination

from .serializers import (SubscriptionsSerializer, IngredientSerializer,
                          PasswordSerializer, RecipeListSerializer,
                          RecipeCreateUpdateSerializers, FavoriteSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserCreateSerializer, UserSerializer)
from .filters import IngredientSearch
from api.permissions import IsAuthenticatedOrReadOnly
User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
  
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearch,)
    pagination_class = None


class UserViewSet(UserViewSet):

    queryset = User.objects.all().order_by("id")
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    serializer_class = UserCreateSerializer()
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "set_password":
            return PasswordSerializer
        if self.action == "subscriptions":
            return SubscriptionsSerializer
        return UserSerializer

    @action(("get",), detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request):
    
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(
        methods=("post",),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
       
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.data.get("new_password"))
        user.save()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("post", "delete",),
        permission_classes=(IsAuthenticated,),
        url_path=r"subscribe"
    )
    def subscribe(self, request, id=None):
      
        current_user = request.user
        following_user = get_object_or_404(User, id=id)
        follow = Follow.objects.filter(
            follower=current_user,
            following=following_user
        ).exists()

        if request.method == "POST":
            if current_user == following_user:
                return Response(
                    {"message": "Вы не можете подписываться на самого себя"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if follow:
                return Response(
                    {"message": "Вы уже подписаны на этого пользователя"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(
                follower=current_user, following=following_user
            )
            serializer = SubscriptionsSerializer(following_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if follow:
                follow = Follow.objects.get(
                    follower=current_user, following=following_user
                ).delete()
            return Response(
                {"message": "Вы отписались от этого пользователя."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"message": "Вы не подписаны на этого пользователя!"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r"subscriptions"
    )
    def subscriptions(self, request):
    
        user = request.user
        queryset = User.objects.filter(followers__follower=user.id)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
  
    queryset = Recipe.objects.all().order_by("-pub_date")
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        tags = self.request.query_params.getlist('tags')
        user = self.request.user
        author = self.request.query_params.get('author')
        is_favorite = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )

        if author:
            queryset = queryset.filter(author_id=author)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        if is_favorite:
            queryset = queryset.filter(favorite__user=user)

        if is_in_shopping_cart:
            queryset = queryset.filter(shopping__cart__user=user)

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeListSerializer
        return RecipeCreateUpdateSerializers

    @action(
        detail=True,
        methods=("post", "delete",),
        permission_classes=(IsAuthenticated,),
        url_path=r"shopping_cart"
    )
    def shopping_cart(self, request, pk=None):
      
        recipes = get_object_or_404(Recipe, pk=pk)
        cart = ShoppingCart.objects.filter(
            recipe=recipes, user=request.user
        ).exists()

        if request.method == "POST":
            if cart:
                return Response(
                    {"message": "Рецепт уже добавлен в корзину!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            shopping_cart = ShoppingCart.objects.create(
                recipe=recipes, user_id=request.user.id
            )
            serializer = ShoppingCartSerializer(shopping_cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if not cart:
                return Response(
                    {"message": "Рецепт нет в корзине!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.filter(
                recipe=recipes, user_id=request.user.id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("post", "delete",),
        permission_classes=(IsAuthenticated,),
        url_path=r"favorite"
    )
    def favorite(self, request, pk=None):
      
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = Favorite.objects.filter(
            recipe=recipe, user=request.user
        ).exists()

        if request.method == "POST":
            if favorite:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            favorite_add = Favorite.objects.create(
                recipe=recipe, user_id=request.user.id
            )
            serializer = FavoriteSerializer(favorite_add)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if favorite:
                favorite = Favorite.objects.get(
                    recipe=recipe, user=request.user
                ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def create_ingredients_file(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
            ).order_by('ingredient__name').values(
                "ingredient__name", "ingredient__measurement_unit"
            ).annotate(amount=Sum("amount"))
        shopping_cart = []
        for ingredient in ingredients:
            shopping_cart.append(
                f'{ingredient["ingredient__name"]}'
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )
        return shopping_cart

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r"download_shopping_cart"
    )
    def download_shopping_cart(self, request):
        try:
            ingredients = self.create_ingredients_file(request)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        content = self.create_ingredients_file(ingredients)
        response = FileResponse(content, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="ingredients.txt"'
        )
        return response
