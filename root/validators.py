from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class UppercaseValidator(object):
    """The password must contain at least 1 uppercase letter, A-Z."""

    def validate(self, password, user=None):
        if not re.findall("[A-Z]", password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter from A to Z."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("The password must contain at least 1 uppercase letter from A to Z.")


class LowercaseValidator(object):
    """The password must contain at least 1 lowercase letter, a-z."""

    def validate(self, password, user=None):
        if not any(char.islower() for char in password):
            raise ValidationError(
                _("The password must contain at least 1 lowercase letter from a to z."),
                code="password_no_lower",
            )

    def get_help_text(self):
        return _("The password must contain at least 1 lowercase letter from a to z.")


class SpecialCharValidator(object):
    """The password must contain at least 1 special character @#$%!^&*"""

    def validate(self, password, user=None):
        if not re.findall("[@#$%!^&*]", password):
            raise ValidationError(
                _(
                    "Your password must contain at least 1 special character: "
                    + "@#$%!^&*"
                ),
                code="password_no_symbol",
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 special character: " + "@#$%!^&*")


class NumericalPasswordValidator(object):
    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("Your password must contain at least one digit."),
                code="password_no_number",
            )

    def get_help_text(self):
        return _("Your password must contain at least one digit.")


class MinimumLengthValidator:
    """
    Validate whether the password is of a minimum length.
    """

    def __init__(self, min_length=9):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("The password must be at least %(min_length)d characters long."),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return _(
            "Your password must be at least %(min_length)d characters long."
            % {"min_length": self.min_length}
        )
