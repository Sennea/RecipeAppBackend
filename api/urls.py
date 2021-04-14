from api.views import CategoryViewSet, CommentViewSet, IngredientViewSet, RatingViewSet, RecipeCategoryViewSet, RecipeIngredientViewSet, RecipeViewSet, StepViewSet, UserViewSet, FavoriteViewSet
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from rest_framework import routers

router = routers.DefaultRouter()
router.register('ratings', RatingViewSet)
router.register('recipes', RecipeViewSet)
router.register('categories', CategoryViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipeIngredients', RecipeIngredientViewSet)
router.register('recipeCategories', RecipeCategoryViewSet)
router.register('comments', CommentViewSet)
router.register('users', UserViewSet)
router.register('steps', StepViewSet)
router.register('favorite', FavoriteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
