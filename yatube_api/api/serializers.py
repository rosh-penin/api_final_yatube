from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from posts.models import Comment, Post, Group, Follow, User


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group."""

    class Meta:
        fields = ('id', 'title', 'slug', 'description')
        model = Group


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post."""
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    image = serializers.ImageField(required=False)
    group = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Group.objects.all()
    )

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date', 'image', 'group')
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Comment


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow."""
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('user', 'following')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following']
            )
        ]

    def validate(self, attrs):
        if attrs['user'] == attrs['following']:
            raise serializers.ValidationError('You cant follow yourself')

        return attrs
