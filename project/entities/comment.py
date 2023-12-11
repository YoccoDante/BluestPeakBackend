from datetime import date as dt

class Comment():
    def __init__(self,enterprise_id:str, _id:str, content:str, root_id:str, commenter_id:str, date:str = str(dt.today()), commenter_full_name:str=None) -> None:
        """Root id stands for the background of the commnet,
        like the comment belongs to a specific product or profile"""
        self._id = _id
        self.commenter_id = commenter_id
        self.date = date
        self.content = content
        self.root_id = root_id
        self.enterprise_id = enterprise_id
        self.commenter_full_name = commenter_full_name