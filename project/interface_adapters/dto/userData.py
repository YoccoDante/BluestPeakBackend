from project.entities.user import User

class UserData():
    def __init__(self, user:User):
        if user is not None:
            if user._id != None: 
                self._id = user._id
            if user.profile_pic == None:
                self.profile_pic = ""
            else:
                self.profile_pic = user.profile_pic
            self.name = user.name
            self.last_name = user.last_name
            self.email = user.email
            self.stars = user.stars
            self.dept = user.dept
            self.phone_number = user.phone_number
            self.gender = user.gender
            self.range = user.range
            self.session_start = user.session_start
            self.last_activity = user.last_activity
            self.total_usage_time = user.total_usage_time
            self.enterprise_id = user.enterprise_id