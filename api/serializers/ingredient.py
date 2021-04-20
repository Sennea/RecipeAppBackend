from rest_framework import serializers

from api.models import Unit, Ingredient
from api.serializers.unit import UnitPrintSerializer


class IngredientDisplaySerializer(serializers.ModelSerializer):
    allowedUnits = UnitPrintSerializer(many=True)

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'imageUrl', 'quantity', 'unit', 'allowedUnits', 'kcal', 'isActive']
        depth = 1


class IngredientSerializer(serializers.ModelSerializer):
    allowedUnits = serializers.PrimaryKeyRelatedField(many=True, queryset=Unit.objects.all())

    # def validate_unit(self, value):
    #     if Unit.objects.filter(short__exact=value):
    #         return value
    #     serializer = UnitPrintSerializer(Unit.objects.all(), many=True)
    #     response = {"message": "There is no such unit!", "available units": serializer.data}
    #     raise serializers.ValidationError(response)

    def validate_allowedUnits(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("This field cannot be empty!")
        return value

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'imageUrl', 'quantity', 'unit', 'allowedUnits', 'kcal', 'isActive']
