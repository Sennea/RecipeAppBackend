from rest_framework import serializers

from api.models import Comment, Favorite, Rating, Category, Step


class StepSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Step
        fields = ['id', 'recipe', 'description', 'order', 'imageUrl']


class StepCreateSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField

    class Meta:
        model = Step
        fields = ['id', 'recipe', 'description', 'order', 'imageUrl']


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']


class RatingSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    stars = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Rating
        fields = ['id', 'recipe', 'user', 'stars']


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ['id', 'recipe', 'user']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('recipe', 'user'),
                message="You have already added this recipe to favourites!"
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'dateAdded', 'dateModified', 'user', 'recipe', 'content']
