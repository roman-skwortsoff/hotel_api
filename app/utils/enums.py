from enum import Enum


class Weekday(str, Enum):
    weekday = "weekday"
    weekend = "weekend"
    anytime = "anyday"


class AccommodationType(str, Enum):
    hotel_room = "hotel_room"
    guest_house = "guest_house"
    gazebo = "gazebo"
