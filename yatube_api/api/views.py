from django.http.request import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
    GenericViewSet
)

from posts.models import Post, Group, Follow, Comment
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    PostSerializer,
    GroupSerializer,
    FollowSerializer,
    CommentSerializer
)


class PostViewSet(ModelViewSet):
    """Viewset for Posts."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(ReadOnlyModelViewSet):
    """Viewset for Groups."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FollowViewSet(CreateModelMixin,
                    ListModelMixin,
                    GenericViewSet):
    """Custom ViewSet for Follows."""
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data['user'] = request.user.username

        return super().create(request, *args, **kwargs)


class CommentViewSet(ModelViewSet):
    """Viewset for Comments."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def _get_post(self, id_str):
        """Get object of Post model from kwargs."""
        post_id = self.kwargs.get(id_str)
        return get_object_or_404(Post, pk=post_id)

    def get_queryset(self):
        post = self._get_post('post_id')
        return post.comments.all()

    def perform_create(self, serializer):
        post = self._get_post('post_id')
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        post = self._get_post('post_id')
        serializer.save(author=self.request.user, post=post)
