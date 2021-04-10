from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from comments.models import Comment
from comments.serializers import CommentSerializer, ThreadedCommentSerializer


class CommentsAPIView(APIView):
    """API View to perform the following functions:
        - Get all comments for a post.
        - Add a new comment or reply to a post.
        - Edit an existing comment.
        - Delete an existing comment.

    Allowed Methods: GET, POST, PATCH, DELETE.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication, SessionAuthentication]

    def get(self, request, post_id):
        """Fetches all the comments for a post.

        Args:
             request: Request object.
             post_id (int): post id.

        Returns:
            dict: list of comments for the given post.
            Example:
                {
                    "post_id": 1,
                    "comments": [
                        {
                            "message_id": 1,
                            "message": "Message 1",
                            "author": {
                                "author_id": 1,
                                "first_name": "Tony",
                                "last_name": "Stark",
                                "username": "ironman"
                            },
                            "replies": [
                                {
                                    "message_id": 2,
                                    "author": {
                                        "author_id": 2,
                                        "first_name": "Peter",
                                        "last_name": "Parker",
                                        "username": "spiderman"
                                    },
                                    "replies": [],
                                    "post_id": 1,
                                    "message": "Reply 1",
                                    "created_on": "2021-04-10T14:00:40.101022Z",
                                    "updated_on": "2021-04-10T14:00:40.101050Z",
                                    "parent_id": 1
                                }
                            ],
                            "post_id": 1,
                            "created_on": "2021-04-10T12:52:29.680232Z",
                            "updated_on": "2021-04-10T14:00:40.101022Z",
                            "parent_id": null
                        }
                    ]
                }
        """
        comments_data = []
        payload = {"post_id": post_id}

        # Fetch all parent comments for the given post id.
        comments = Comment.objects.filter(post_id=post_id, parent__isnull=True)

        # For each parent comment, fetch its details and replies attached to it.
        for comment in comments:
            comment_data = ThreadedCommentSerializer(comment).data
            comments_data.append(comment_data)

        # Added the comments to the payload.
        payload["comments"] = comments_data
        return Response(data=payload, status=status.HTTP_200_OK)

    def post(self, request):
        """Creates a new comment or reply to an existing comment.

        Args:
             request: Request object.
        Returns:
            dict: status of the response and the message that is added a comment.
        """
        # Get the message body attached to the request object.
        message_body = request.data
        post_id = message_body.get("post_id")
        user = request.user

        # Check if the post id to which the user is commenting is not empty.
        if not post_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # payload for the comment serializer.
        data = {
            "message": message_body.get("message"),
            "author_id": user.id,
            "post_id": post_id,
            "parent_id": message_body.get("parent_id"),
        }

        serializer_instance = CommentSerializer(data=data)

        # If the payload is not valid, return the corresponding errors.
        if not serializer_instance.is_valid():
            return serializer_instance.errors
        # Create the comment with the given payload.
        serializer_instance.create(data)

        return Response(data=serializer_instance.data, status=status.HTTP_201_CREATED)

    def patch(self, request, message_id):
        """Edit the message for an existing comment.

        Args:
            request: Request object.
            message_id (int): id of comment id.
        Returns:
             dict: details of the updated comment.
             Example:
                 {
                    "post_id": 1,
                    "author_id": 1,
                    "message": "Updated Message",
                    "created_on": "2021-04-10T12:54:26.436566Z",
                    "updated_on": "2021-04-10T15:08:19.840550Z",
                    "parent_id": 1,
                    "last_child_id": 3,
                    "id": 2
                }
        """

        # Get the message to be updated and the request user.
        message = request.data.get("message")
        user = request.user

        # Fetch the comment to be updated.
        comment = Comment.objects.filter(id=message_id, author=user).first()

        # If comment there is no matching comment, return status 404.
        if not comment:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Initialize the serializer class.
        serializer_instance = CommentSerializer(
            comment, data={"message": message}, partial=True
        )

        # If the payload to be updated has error, then return the errors.
        if not serializer_instance.is_valid():
            return serializer_instance.errors

        # Update the comment with the updated message.
        serializer_instance.save()

        return Response(data=serializer_instance.data, status=status.HTTP_200_OK)

    def delete(self, request, message_id):
        """Deletes the comment corresponding to the message id.

        Args:
            request: Request object.
            message_id (int): id of the comment to be deleted.
        """

        # get the request user.
        user = request.user

        # fetch the comment to be deleted.
        comment = Comment.objects.filter(id=message_id, author=user).first()

        # If there is no comment for the given message id, return status 404.
        if not comment:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # If comment is found, then delete it.
        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
