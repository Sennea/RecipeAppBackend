from rest_framework import serializers

from api.models import Unit, RecipeIngredient, Ingredient
from api.serializers.unit import UnitPrintSerializer


class RecipeIngredientSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    # def validate_unit(self, value):
    #     unit = Unit.objects.filter(short__exact=value)
    #     if Unit.objects.filter(short__exact=value):
    #         return unit[0]
    #     serializer = UnitPrintSerializer(Unit.objects.all(), many=True)
    #     response = {"message": "There is no such unit!", "available units": serializer.data}
    #     raise serializers.ValidationError(response)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'recipe', 'unit', 'quantity']

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('recipe', 'ingredient'),
                message="There is already such an ingredient in this recipe!"
            )
        ]

    def create(self, validated_data):
        ingredient = validated_data.get('ingredient')

        unit = validated_data.pop('unit')
        allowed_ingredient_units = ingredient.allowedUnits.all()
        if unit not in allowed_ingredient_units:
            serializer = UnitPrintSerializer(allowed_ingredient_units, many=True)
            # data = list(map(lambda v: v['short'], json.loads(json.dumps(serializer.data))))
            response = {"message": "This unit is not allowed for this ingredient!", "allowed units": serializer.data}
            raise serializers.ValidationError(response)
        validated_data['unit'] = unit.short
        return RecipeIngredient.objects.create(**validated_data)


class RecipeIngredientUpdateSerializer(serializers.ModelSerializer):

    # def validate_unit(self, value):
    #     unit = Unit.objects.filter(short__exact=value)
    #     if Unit.objects.filter(short__exact=value):
    #         return unit[0]
    #     serializer = UnitPrintSerializer(Unit.objects.all(), many=True)
    #     response = {"message": "There is no such unit!", "available units": serializer.data}
    #     raise serializers.ValidationError(response)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'unit', 'quantity']

    def update(self, instance, validated_data):
        ingredient = instance.ingredient
        unit = validated_data.get('unit')
        if unit is not None:
            validated_data.pop('unit')
            allowed_ingredient_units = ingredient.allowedUnits.all()

            if unit not in allowed_ingredient_units:
                serializer = UnitPrintSerializer(allowed_ingredient_units, many=True)
                response = {"message": "This unit is not allowed for this ingredient!",
                            "allowed units": serializer.data}
                raise serializers.ValidationError(response)
            validated_data['unit'] = unit.short
        return super(RecipeIngredientUpdateSerializer, self).update(instance, validated_data)
