from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Comment


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for fetching details of a User."""

    author_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("author_id", "first_name", "last_name", "username")

    @staticmethod
    def get_author_id(user):
        """
        Args:
             user (User): user instance.
        Returns:
            int: user id.
        """
        return user.id


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for fetching, editing and updating details of a comment."""

    class Meta:
        model = Comment
        fields = (
            "post_id",
            "author_id",
            "message",
            "created_on",
            "updated_on",
            "parent_id",
            "last_child_id",
            "id",
        )
        read_only_fields = (
            "created_on",
            "updated_on",
            "last_child_id",
        )


class ThreadedCommentSerializer(serializers.ModelSerializer):
    """Serializer for rendering a comment and its replies as a threaded structure."""

    author = serializers.SerializerMethodField(read_only=True, required=False)
    message_id = serializers.SerializerMethodField(read_only=True, required=False)
    replies = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = Comment
        fields = (
            "message_id",
            "author",
            "replies",
            "post_id",
            "message",
            "created_on",
            "updated_on",
            "parent_id",
        )
        read_only_fields = ("updated_on", "created_on")

    @staticmethod
    def get_message_id(comment):
        """
        Args:
             comment (Comment): comment instance.
        Returns:
            int: comment id.
        """
        return comment.id

    @staticmethod
    def get_author(comment):
        """
        Args:
             comment (Comment): comment instance.
        Returns:
            dict: details of the author of the comment.
        """
        return UserDetailSerializer(comment.author).data

    @staticmethod
    def get_replies(comment):
        """
        Args:
             comment (Comment): comment instance.
        Returns:
            list: replies to the comment instance.
        """
        replies = []
        for child in comment.children.all():
            replies.append(ThreadedCommentSerializer(child).data)
        return replies
