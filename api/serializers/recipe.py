from django.db import transaction, IntegrityError
from rest_framework import serializers

from api.models import Step, RecipeIngredient, Unit, User, Category, Recipe
from api.serializers.serializers import CategorySerializer, CommentSerializer
from api.serializers.unit import UnitPrintSerializer


class StepRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['description', 'order', 'imageUrl']


# Only for validation in Recipe
class RecipeIngredientRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'unit', 'quantity']


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data or key == data:
                return key

        self.fail('invalid_choice', input=data)


class RecipeDisplaySerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    steps = StepRecipeSerializer(many=True)
    ingredients = RecipeIngredientRecipeSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField
    level = ChoiceField(choices=Recipe.LEVEL_CHOICES)
    preparationTimeUnit = ChoiceField(choices=Recipe.PREPARATION_TIME_UNIT_CHOICES)
    comments = CommentSerializer(many=True)
    user_favourite = serializers.BooleanField(read_only=True)
    user_rating = serializers.IntegerField(min_value=0, max_value=5, read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'user', 'title', 'description', 'no_of_rating', 'avg_rating',
                  'user_favourite', 'user_rating',
                  'imageUrl', 'preparationTime', 'preparationTimeUnit',
                  'level', 'dateAdded',
                  'categories', 'steps', 'ingredients', 'comments']


class RecipeSerializer(serializers.ModelSerializer):
    # categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    steps = StepRecipeSerializer(many=True)
    ingredients = RecipeIngredientRecipeSerializer(many=True)
    level = ChoiceField(choices=Recipe.LEVEL_CHOICES)
    preparationTimeUnit = ChoiceField(choices=Recipe.PREPARATION_TIME_UNIT_CHOICES)

    class Meta:
        model = Recipe
        fields = ['id', 'user_id', 'title', 'description', 'no_of_rating', 'avg_rating',
                  'imageUrl', 'preparationTime', 'preparationTimeUnit',
                  'level', 'dateAdded',
                  'categories', 'steps', 'ingredients']

    def validate_steps(self, value):
        if len(value) == 0:
            return serializers.ValidationError("This field cannot be empty!")
        return value

    def validate_ingredients(self, value):
        if len(value) == 0:
            return serializers.ValidationError("This field cannot be empty!")
        return value

    def validate_categories(self, value):
        if len(value) == 0:
            return serializers.ValidationError("This field cannot be empty!")
        return value

    def create(self, validated_data):
        steps_data = validated_data.pop('steps')
        recipe_ingredients_data = validated_data.pop('ingredients')
        categories = validated_data.pop('categories')
        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            recipe.categories.set(categories)
            for recipe_ingredient_data in recipe_ingredients_data:
                allowed_ingredient_units = recipe_ingredient_data['ingredient'].allowedUnits.all()
                recipe_ingredient_unit = recipe_ingredient_data.pop('unit')
                if recipe_ingredient_unit not in allowed_ingredient_units:
                    serializer = UnitPrintSerializer(allowed_ingredient_units, many=True)
                    response = {"message": "Recipe ingredient unit = " + recipe_ingredient_unit.short +
                                           " is not allowed for ingredient with id = " +
                                           str(recipe_ingredient_data['ingredient'].id) + "!",
                                "allowed units": serializer.data}
                    raise serializers.ValidationError(response)
                RecipeIngredient.objects.create(recipe=recipe, unit=recipe_ingredient_unit,
                                                **recipe_ingredient_data)
            for step_data in steps_data:
                try:
                    Step.objects.create(recipe=recipe, **step_data)
                except IntegrityError as e:
                    response = {"steps": ["Each recipe step must have a different order field number!"]}
                    raise serializers.ValidationError(response)

            return recipe

    def update(self, instance, validated_data):
        steps_data = validated_data.get('steps')
        recipe_ingredients_data = validated_data.get('ingredients')
        categories = validated_data.get('categories')
        with transaction.atomic():

            if categories is not None:
                validated_data.pop('categories')
                instance.categories.add(*categories)

            if steps_data is not None:
                validated_data.pop('steps')
                for step_data in steps_data:
                    Step.objects.create(recipe=instance, **step_data)

            if recipe_ingredients_data is not None:
                validated_data.pop('ingredients')
                for recipe_ingredient_data in recipe_ingredients_data:
                    allowed_ingredient_units = recipe_ingredient_data['ingredient'].allowedUnits.all()
                    recipe_ingredient_unit = recipe_ingredient_data.pop('unit')
                    if recipe_ingredient_unit not in allowed_ingredient_units:
                        serializer = UnitPrintSerializer(allowed_ingredient_units, many=True)
                        response = {"message": "Recipe ingredient unit = " + recipe_ingredient_unit.short +
                                               " is not allowed for ingredient with id = " +
                                               str(recipe_ingredient_data['ingredient'].id) + "!",
                                    "allowed units": serializer.data}
                        raise serializers.ValidationError(response)
                    RecipeIngredient.objects.create(recipe=instance, unit=recipe_ingredient_unit,
                                                    **recipe_ingredient_data)
            return super(RecipeSerializer, self).update(instance, validated_data)
