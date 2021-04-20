from django.contrib import admin
from django.forms import ModelForm, ChoiceField, forms, CharField
from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe

from api.models import Category, Comment, Favorite, Ingredient, Rating, Recipe, RecipeIngredient, Step, Unit


# Register your models here.


class RecipeIngredientRecipeAdminForm(ModelForm):
    # allowed_units = CharField()
    #

    def clean_unit(self):
        if self.cleaned_data['unit'] in self.cleaned_data['ingredient'].allowedUnits.all():
            return self.cleaned_data['unit']
        raise forms.ValidationError(
            "This unit is not allowed with this ingredient!"
        )

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',  # jquery
            'rci_recipe_script.js'
        )


class RecipeIngredientAdminForm(ModelForm):
    # allowed_units = CharField()
    #

    def clean_unit(self):
        if self.cleaned_data['unit'] in self.cleaned_data['ingredient'].allowedUnits.all():
            return self.cleaned_data['unit']
        raise forms.ValidationError(
            "This unit is not allowed with this ingredient!"
        )

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',  # jquery
            'rci_script.js'
        )


class RecipeIngredientsInline(admin.TabularInline):
    readonly_fields = ('allowed_units',)
    model = RecipeIngredient
    form = RecipeIngredientRecipeAdminForm

    @admin.display(description='Allowed units')
    def allowed_units(self, instance):
        div = '<div id="id_allowed_units">'

        if instance.pk is not None:
            for line in instance.allowed_units():
                div += line + ', '
                div = div[:-2]
        else:
            div += instance.allowed_units()
        div += '</div>'
        return format_html(div)


class StepsInline(admin.TabularInline):
    model = Step


class CommentsInline(admin.TabularInline):
    model = Comment


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientsInline, StepsInline, CommentsInline]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    readonly_fields = ('allowed_units',)
    form = RecipeIngredientAdminForm

    @admin.display(description='Allowed units')
    def allowed_units(self, instance):
        div = '<div id="id_allowed_units">'

        if instance.pk is not None:
            for line in instance.allowed_units():
                div += line + ', '
                div = div[:-2]
        else:
            div += instance.allowed_units()
        div += '</div>'
        return format_html(div)


admin.site.register(Rating)
admin.site.register(Favorite)
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(Comment)
admin.site.register(Step)
admin.site.register(Unit)
