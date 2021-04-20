from django.contrib import admin
from django.forms import ModelForm, ChoiceField, forms

from api.models import Category, Comment, Favorite, Ingredient, Rating, Recipe, RecipeIngredient, Step, Unit


# Register your models here.


class RecipeIngredientAdminForm(ModelForm):

    def clean_unit(self):
        if self.cleaned_data['unit'] in self.cleaned_data['ingredient'].allowedUnits.all():
            return self.cleaned_data['unit']
        raise forms.ValidationError(
            "This unit is not allowed with this ingredient!"
        )


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    form = RecipeIngredientAdminForm


class StepsInline(admin.TabularInline):
    model = Step


class CommentsInline(admin.TabularInline):
    model = Comment


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientsInline, StepsInline, CommentsInline]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    form = RecipeIngredientAdminForm


admin.site.register(Rating)
admin.site.register(Favorite)
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(Comment)
admin.site.register(Step)
admin.site.register(Unit)
