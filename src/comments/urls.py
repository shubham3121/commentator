from django.urls import path
from comments import api

urlpatterns = [
    path(
        "<int:post_id>/comments/",
        api.CommentsAPIView.as_view(),
        name="fetch-comments",
    ),
    path(
        "reply/",
        api.CommentsAPIView.as_view(),
        name="add-comment",
    ),
    path(
        "edit-message/<int:message_id>/",
        api.CommentsAPIView.as_view(),
        name="edit-comment",
    ),
    path(
        "delete-message/<int:message_id>/",
        api.CommentsAPIView.as_view(),
        name="delete-comment",
    ),
]
