# commentator
## A Django Based Comment System

#### Requirements
The API should have the following capabilities:
1. Get a list of all comments made on a page with a given URL.
2. Add a new comment on a page with a given URL.
3. Add a new sub-comment on an already existing comment as a reply.
4. Edit an existing comment.
5. Delete a single comment or an entire comment thread using the comment's identifier.

#### Entities
- User
- Comment

#### Database Models

**Note** : In the current design, deleting a parent comment will also delete its child comments.

**Comment**
- id: Auto increment id
- author_id: id of the user making the comment 
- post_id: id of the post on which the comment is made
- message: message posted in the comment
- created_on: date on which the comment was posted
- updated_on: date on which the comment was updated
- parent: reference to parent of the comment (if any)  
- last_child: reference to last reply to the comment
- tree_path: path for traversing the comments as a flat list

### APIs

---
****Get all comments for a given post****

**Type**: GET

**Url**: /<post_id>/comments/

**Sample Response Data**: 

    {
        "post_id": 1,
        "comments": [
            {
                "message_id": 1,
                "author": {
                    "author_id": 2,
                    "first_name": "",
                    "last_name": "",
                    "username": "shubham"
                },
                "replies": [
                    {
                        "message_id": 2,
                        "author": {
                            "author_id": 2,
                            "first_name": "",
                            "last_name": "",
                            "username": "shubham"
                        },
                        "replies": [],
                        "post_id": 1,
                        "message": "Reply",
                        "created_on": "2021-04-10T13:56:32.260205Z",
                        "updated_on": "2021-04-10T13:56:32.260301Z",
                        "parent_id": 1
                    }
                ],
                "post_id": 1,
                "message": "Message",
                "created_on": "2021-04-10T12:52:29.680232Z",
                "updated_on": "2021-04-10T13:56:32.260205Z",
                "parent_id": null
            },
        ]
    }
**Status**: 200

---
***Add a new comment***

**Type**: POST

**Url**: /reply/

**Body**:

    {
    “post_id”: “”,
    “message”: “”,
    “parent_id”: “”,
    }

**Sample Response Data**: 

    {“message”: “Message”, “post_id”: 1}

**Status**: 201/400

---
****Edit an existing comment****

**Type**: PATCH

**Url**: /edit-message/<message_id>

**Body**:

    {
    “message”: “”
    }
 
**Sample Response Data**: 

    {
    "post_id": 1,
    "author_id": 1,
    "message": "Update Message",
    "created_on": "2021-04-10T13:56:32.260205Z",
    "updated_on": "2021-04-10T14:12:18.729563Z",
    "parent_id": 1,
    "last_child_id": null,
    "id": 1
    }

 
**Status**: 204/404

---
****Delete an existing comment****

**Type**: DELETE
    
**Url**: /delete-message/<message_id>
 
**Response Data**:

    None 
**Status**: 204/404
