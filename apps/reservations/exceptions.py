from rest_framework.exceptions import APIException
from rest_framework import status


class CartAlreadyActiveError(Exception):
    pass


class SeatsLockedError(Exception):
    pass


class SessionAlreadyStarted(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "This session has already started."


class ActiveCartExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "You already have an active reservation for this session."


class SeatsUnavailable(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "One or more seats are already reserved."


class InvalidSeatsSelection(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "One or more seats are invalid or inactive."


class MaxSeatsExceeded(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Maximum seats per reservation exceeded."
