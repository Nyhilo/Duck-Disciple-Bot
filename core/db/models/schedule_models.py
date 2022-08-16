class Schedule():
    def __init__(self, schedule_id=None, schedule_name=None, schedule_channel=None, start_timestamp=None,
                 day_of_the_year=None, day_of_the_month=None, day_of_the_week=None, hour_of_the_day=None,
                 next_activation=None, active=1):

        self.schedule_id = schedule_id
        self.schedule_name = schedule_name
        self.schedule_channel = schedule_channel
        self.start_timestamp = start_timestamp
        self.day_of_the_year = day_of_the_year
        self.day_of_the_month = day_of_the_month
        self.day_of_the_week = day_of_the_week
        self.hour_of_the_day = hour_of_the_day
        self.next_activation = next_activation
        self.active = active
