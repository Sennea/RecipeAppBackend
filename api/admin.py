from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, forms
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html

from api.models import Category, Comment, Favorite, Ingredient, Rating, Recipe, RecipeIngredient, Step, Unit, User
from api.serializers.ingredient import IngredientDisplaySerializer
from recipes.settings import APP_URL


class CustomAdminSite(AdminSite):

    def each_context(self, request):
        context = super(CustomAdminSite, self).each_context(request)
        context['APP_URL'] = APP_URL
        return context

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('ingredients/<int:id>/', self.get_ingredient)
        ]

        urls = my_urls + urls
        return urls

    def get_ingredient(self, request, *args, **kwargs):
        if not request.user.is_anonymous and request.user.is_superuser:
            rci_id = kwargs.get('id')
            try:
                ingredient = Ingredient.objects.get(id=rci_id)
                serializer = IngredientDisplaySerializer(ingredient)
                return JsonResponse({'ingredient': serializer.data}, status=200)
            except ObjectDoesNotExist:
                data = {'error': 'Ingredient with id={} dose not exists!'.format(rci_id)}
                return JsonResponse(data, status=404)
        else:
            response = redirect('/admin/login/')
            return response


class RecipeIngredientAdminForm(ModelForm):

    def clean_unit(self):
        ingredient = self.cleaned_data.get('ingredient', None)
        if ingredient is not None and self.cleaned_data['unit'] in ingredient.allowedUnits.all():
            return self.cleaned_data['unit']
        raise forms.ValidationError(
            "This unit is not allowed with this ingredient!"
        )


class RecipeIngredientsInline(admin.TabularInline):
    readonly_fields = ('allowed_units',)
    model = RecipeIngredient
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


class StepsInline(admin.TabularInline):
    model = Step


class CommentsInline(admin.TabularInline):
    model = Comment


custom_admin = CustomAdminSite()

custom_admin.register(Rating)
custom_admin.register(Favorite)
custom_admin.register(Category)
custom_admin.register(Ingredient)
custom_admin.register(Comment)
custom_admin.register(Step)
custom_admin.register(Unit)

# register the default model

custom_admin.register(Group, GroupAdmin)
custom_admin.register(User, UserAdmin)


@admin.register(Recipe, site=custom_admin)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientsInline, StepsInline, CommentsInline]


@admin.register(RecipeIngredient, site=custom_admin)
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

# admin.site.register(Rating)
# admin.site.register(Favorite)
# admin.site.register(Category)
# admin.site.register(Ingredient)
# admin.site.register(Comment)
# admin.site.register(Step)
# admin.site.register(Unit)
