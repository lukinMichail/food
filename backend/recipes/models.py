from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

from backend.settings import LIMITATION, MIN_VALUE_COOKING_TIME, VALUE_AMOUNT

User = get_user_model()


class Tag(models.Model):

    name = models.CharField(max_length=LIMITATION, unique=True)
    color = models.CharField(max_length=LIMITATION, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):

    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(
        "Единица измерения", max_length=LIMITATION
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient_name_unit_unique'
            )
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.measurement_unit}."


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Автор",
    )
    name = models.CharField("Имя рецепта", max_length=LIMITATION)
    image = models.ImageField(
        "Изображение рецепта",
        upload_to="static/recipe"
    )
    text = models.TextField("Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient"
    )
    cooking_time = models.BigIntegerField(
        "Время готовки",
        validators=(MinValueValidator(MIN_VALUE_COOKING_TIME),),
        error_messages={
            "errors":
            f"Минимальное время готовки {MIN_VALUE_COOKING_TIME} минута."
        },
        default=MIN_VALUE_COOKING_TIME,
    )
    pub_date = models.DateField(auto_now_add=True)
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes"
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    """Моедль, связывающая количество ингридиентов и рецепт."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.IntegerField(
        'Количество',
        validators=(MinValueValidator(VALUE_AMOUNT),),
        default=1
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = "Колличество ингридиентов"
        verbose_name_plural = "Колличество ингридиентов"

    def __str__(self) -> str:
        return (
            f"{self.recipe.name} {self.ingredient.name} "
            f"{self.amount} {self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    """Модель избранного рецепта пользователя."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.recipe.name}"


class ShoppingCart(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart"
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        ordering = ["-recipe"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="shopping_list",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.recipe.name}"
