class Enterprise:
    def __init__(self, _id, name, email, phone_number, total_usage_time=0, paid=True, total_users:int=0):
        self._id = _id
        self.name = name
        self.total_usage_time = total_usage_time
        self.paid = paid
        self.total_users = total_users
        self.email = email
        self.phone_number = phone_number