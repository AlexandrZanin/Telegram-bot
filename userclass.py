class User:
    """ This is User Class
    """
    user_dict={}
    def __init__(self, id):
        """
        :param cmd: command
        :param id: user id
        :param sity: city name
        :param sity_id: city id
        :param date_in: check-in date to the hotel
        :param date_out: check-out date to the hotel
        :param low_price: lower price limits
        :param top_price: upper price limits
        :param count_hotel: how many hotels to show
        :param foto: show photo or not
        :param foto_count: how many foto to show
        :param locale: en_US or ru_RU
        :param max_dist: maximum distance to the city center
        :param city_name_id: temporary storage. dictionary: key=city id, value=city name
        :return: User object.
        """
        self.cmd=None
        self.id=id
        self.sity=None
        self.sity_id=None
        self.date_in=None
        self.date_out=None
        self.low_price=0
        self.top_price=0
        self.count_hotels=None
        self.foto=False
        self.foto_count=0
        self.locale='en_US'
        self.max_dist=0
        self.city_name_id={}
        self.currency=None
        User.add_user(id, self)

    @staticmethod
    def get_user(user_id):
        return User.user_dict.get(user_id)
    @staticmethod
    def reg_user(user_id):
        if User.user_dict.get(user_id):
            del User.user_dict[user_id]
        new_user=User(user_id)
        return new_user

    @classmethod
    def add_user(cls, user_id, user):
        cls.user_dict[user_id]=user
