class CustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code


class ErrorMessagesUtil:

    # Роли

    @staticmethod
    def roles_not_found():
        return f"Roles not found."

    @staticmethod
    def role_not_found():
        return f"Role not found."

    @staticmethod
    def user_doesnt_have_this_role():
        return f"User does not have this role."

    # Пользователи

    @staticmethod
    def user_not_found():
        return f"User not found."

    @staticmethod
    def user_already_exists():
        return f"User already exists."

    @staticmethod
    def wrong_password():
        return f"Wrong password given."

    # Токены

    @staticmethod
    def unable_to_refresh_token():
        return f"Unable to refresh token."

    @staticmethod
    def access_token_is_invalid():
        return f"Access token is invalid."

    @staticmethod
    def refresh_token_is_invalid():
        return f"Refresh token is invalid."

    @staticmethod
    def user_not_authorized():
        return f"User not authorized."
