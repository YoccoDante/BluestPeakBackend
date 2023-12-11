from project.functional.crypto import Crypto
from project.frameworks_and_drivers.database import db
from project.entities.comment import Comment
from datetime import date as dt
from project.interface_adapters.dao.userDao import UserDao

class CommentDao():
    @staticmethod
    def add_comment(new_comment:Comment) -> None:
        comments = db["comments"]
        new_comment_data = new_comment.__dict__
        # Validate comment content
        if not new_comment_data.get('content'):
            raise ValueError('Comment content is required')
        try:
            comments.insert_one(new_comment_data)
        except Exception as e:
            raise ValueError(f"Failed to add comment: {e}")

    @staticmethod
    def delete_comment(commenter_id:str, comment_id:str, enterprise_id:str) -> None:
        comments = db["comments"]
        try:
            comments.delete_one({"_id":comment_id, 'commenter_id':commenter_id, 'enterprise_id':enterprise_id})
        except Exception as e:
            raise ValueError(f"Failed to delete comment: {e}")

    @staticmethod
    def edit_comment(enterprise_id:str, commenter_id:str, comment_id:str, new_content:str) -> None:
        comments = db["comments"]
        # Validate new content
        if not new_content:
            raise ValueError('New content is required')
        try:
            comments.update_one({"_id":comment_id, 'commenter_id':commenter_id, 'enterprise_id':enterprise_id},
                {"$set": {
                    "content":new_content,
                    "date": str(dt.today())
                }})
        except Exception as e:
            raise ValueError(f"Failed to update comment: {e}")

    @staticmethod
    def get_root_comments(root_id:str, enterprise_id:str) -> list[Comment]:
        """Returns a list of Comment objects"""
        comments = db["comments"]
        try:
            root_comments = comments.find({"root_id":root_id, 'enterprise_id':enterprise_id})
            comment_list = [
                Comment(
                    _id=Crypto.encrypt(comment["_id"]),
                    commenter_id=Crypto.encrypt(comment["commenter_id"]),
                    content=comment["content"],
                    root_id=Crypto.encrypt(comment["root_id"]),
                    date=comment["date"],
                    enterprise_id=comment['enterprise_id'],
                    commenter_full_name=UserDao.get_user_by_id(
                        user_id=comment["commenter_id"],
                        enterprise_id=enterprise_id
                    ).full_name
                ).__dict__
            for comment in root_comments]
            return comment_list
        except Exception as e:
            raise ValueError(f"Failed to get root comments: {e}")
    
    @staticmethod
    def delete_root_commentaries(root_id:str, enterprise_id:str) -> None:
        """Deletes all the comments made in a root by a given _id."""
        comments = db["comments"]
        try:
            comments.delete_many({"root_id":root_id, 'enterprise_id':enterprise_id})
        except Exception as e:
            raise ValueError(f"Failed to delete root comments: {e}")

    @staticmethod
    def delete_comment(commenter_id:str, comment_id:str, enterprise_id) -> None:
        """Deletes a commentary by it's _id."""
        comments = db["comments"]
        try:
            comments.delete_one({"_id":comment_id, 'commenter_id':commenter_id, 'enterprise_id':enterprise_id})
        except Exception as e:
            raise ValueError(f"Failed to delete comment: {e}")
    
    @staticmethod
    def delete_commentaries(commenter_id:str, enterprise_id:str) -> None:
        """Deletes all the commentaries made for a user or customer."""
        comments = db["comments"]
        try:
            comments.delete_many({"commenter_id":commenter_id, 'enterprise_id':enterprise_id})
        except Exception as e:
            raise ValueError(f"Failed to delete commentaries: {e}")