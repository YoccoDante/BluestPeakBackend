class User:
    def __init__(self, _id, name, last_name, email, gender, range, phone_number, session_start=None, last_activity=None, total_usage_time=0, enterprise_id=None, password = None, profile_pic=None, stars=0, dept=False):
        self._id:str = _id
        self.name:str = str(name).lower()
        self.last_name:str = str(last_name).lower()
        self.email:str = str(email).lower()
        self.gender:str = str(gender).lower()
        self.password:str = password
        self.profile_pic:str = profile_pic
        self.stars:int = stars
        self.dept:bool = dept
        self.range:str = str(range).lower()
        self.phone_number:str = phone_number
        self.session_start = session_start
        self.last_activity = last_activity
        self.total_usage_time:float = total_usage_time
        self.enterprise_id:str = enterprise_id  # The ID of the enterprise that this user belongs to
        self.full_name = self.name+' '+self.last_name