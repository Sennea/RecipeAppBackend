from django.contrib import admin

from api.models import Category, Comment, Favorite, Ingredient, Rating, Recipe, RecipeIngredient, Step

# Register your models here.

admin.site.register(Recipe)
admin.site.register(Rating)
admin.site.register(Favorite)
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(Comment)
admin.site.register(RecipeIngredient)
admin.site.register(Step)
