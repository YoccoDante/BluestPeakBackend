class Rate():
    def __init__(self, enterprise_id:str, rater_id:str, target_id:str, rate:int) -> None:
        self.rater_id = rater_id
        self.target_id = target_id
        self.rate = rate
        self.enterprise_id = enterprise_id
        