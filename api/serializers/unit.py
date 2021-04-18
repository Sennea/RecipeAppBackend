from rest_framework import serializers

from api.models import Unit


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'full', 'short']


class UnitPrintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['short', 'full']
