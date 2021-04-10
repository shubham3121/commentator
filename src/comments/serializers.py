from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Comment


class UserDetailSerializer(serializers.ModelSerializer):
    author_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("author_id", "first_name", "last_name", "username")

    @staticmethod
    def get_author_id(user):
        return user.id


class CommentSerializer(serializers.ModelSerializer):
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
        return comment.id

    @staticmethod
    def get_author(comment):
        return UserDetailSerializer(comment.author).data

    @staticmethod
    def get_replies(comment):
        replies = []
        for child in comment.children.all():
            replies.append(ThreadedCommentSerializer(child).data)
        return replies
