from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone

PATH_SEPARATOR = ","


class Comment(models.Model):
    """Database model to store details of a comment.

    1. Each Comment has parent and a child. Although, their values can be null.
    2. If the parent of a comment is null, it implies that this comment is the root comment.
    3. The child of a comment implies the reply to the root comment.
    4. If a comment (with no child) is deleted, then the child value corresponding
       to its parent is set to null.
    5. A comment cannot delete its parent, until its parent exists.

    """

    # id of the post to which the comment is attached.
    post_id = models.PositiveIntegerField(db_index=True, null=False, blank=False)

    # author of the comment
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # text of the comment
    message = models.TextField(null=True, blank=True)

    # when the comment was created
    created_on = models.DateTimeField(auto_now_add=True, blank=True)

    # when the comment was updated
    updated_on = models.DateTimeField(auto_now_add=True, blank=True)

    # reference to the parent node of the comment
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )

    # reference to the last child node of the comment
    last_child = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )

    # path for traversing the comments as a flat list
    tree_path = models.CharField(max_length=500, editable=False)

    def __repr__(self):
        return f"<Comment<{self.pk}>: {self.message[:15]}>"

    @property
    def root_id(self):
        return int(self.tree_path.split(PATH_SEPARATOR)[0])

    @property
    def root_path(self):
        return Comment.objects.filter(pk__in=self.tree_path.split(PATH_SEPARATOR)[:-1])

    @transaction.atomic
    def save(self, *args, **kwargs):

        is_new = not self.pk

        if is_new:
            self.created_on = timezone.now()
        super(Comment, self).save(*args, **kwargs)

        # If a new comment
        if is_new:
            tree_path = str(self.pk).zfill(10)
            if self.parent:
                tree_path = PATH_SEPARATOR.join((self.parent.tree_path, tree_path))
                self.parent.last_child = self
                Comment.objects.filter(pk=self.parent_id).update(
                    last_child=self.id, updated_on=self.created_on
                )

            self.tree_path = tree_path
            self.updated_on = self.created_on
        else:
            self.updated_on = timezone.now()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.parent_id:
            prev_child = (
                Comment.objects.filter(parent=self.parent_id)
                .exclude(pk=self.pk)
                .order_by("-created_on")
                .first()
            )

            if prev_child:
                Comment.objects.filter(pk=self.parent_id).update(
                    last_child=prev_child, updated_on=prev_child.created_on
                )
            else:
                Comment.objects.filter(pk=self.parent_id).update(
                    last_child=None, updated_on=self.parent.created_on
                )

        super(Comment, self).delete(*args, **kwargs)

    class Meta:
        ordering = ("tree_path",)
