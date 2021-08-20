import pytest

from app import exceptions
from app.services import token_service


def test_correct_get_course_id_from_token():
    course_id = 1
    token = token_service.create_course_invite_link(course_id=course_id)
    course_id_ = token_service.get_course_id_from_token(token)
    assert course_id == course_id_


def test_invalid_get_course_id_from_token():
    token = token_service.create_course_invite_link(course_id=1)
    invalid_token = token + "invalid_part"

    with pytest.raises(exceptions.InvalidCourseInvite):
        token_service.get_course_id_from_token(invalid_token)


def test_correct_get_register_token_data():
    data = {
        "email": "email",
        "username": "username",
        "password": "12345678",
        "role": "student",
    }
    token = token_service.create_confirmation_token(data)
    data_ = token_service.get_register_token_data(token)
    assert data == data_


def test_invalid_get_register_token_data():
    data = {
        "email": "email",
        "username": "username",
        "password": "12345678",
        "role": "student",
    }
    token = token_service.create_confirmation_token(data)
    invalid_token = token + "invalid_part"

    with pytest.raises(exceptions.InvalidRegisterToken):
        token_service.get_register_token_data(invalid_token)
