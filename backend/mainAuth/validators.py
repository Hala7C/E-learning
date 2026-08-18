import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from datetime import datetime

class NumberValidator(object):
    def __init__(self, min_digits=0):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        if not len(re.findall('\d', password)) >= self.min_digits:
            raise ValidationError(
                _("The password must contain at least %(min_digits)d digit(s), 0-9."),
                code='password_no_number',
                params={'min_digits': self.min_digits},
            )
    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_digits)d digit(s), 0-9." % {'min_digits': self.min_digits}
        )

   

    
class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase letter, A-Z."
        )


class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("The password must contain at least 1 lowercase letter, a-z."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 lowercase letter, a-z."
        )


class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                _("The password must contain at least 1 symbol: " +
                  "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 symbol: " +
            "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
        )


def validate_month(month_str):
    """
    Validate if the input string represents a valid month.

    Args:
        month_str (str): The input string to be validated.

    Returns:
        datetime.date: The validated month as a datetime.date object.

    Raises:
        ValidationError: If the input string is not a valid month.
    """
    try:
        # Try to parse the input string as a month (e.g., "January", "Feb", "03")        
        if month_str:
            month_date = datetime.strptime(month_str, '%B').date()
            return month_date.replace(day=1)
    except ValueError:
        try:
            # Try to parse the input string as a month number (e.g., "1", "03")
            month_date = datetime.strptime(month_str, '%m').date()
            return month_date.replace(day=1)
        except ValueError:
            # Raise a ValidationError if the input is not a valid month
            raise ValidationError({'month': f'"{month_str}" is not a valid month.'})


def validate_year(year_str):
    """
    Validate if the input string represents a valid year.

    Args:
        year_str (str): The input string to be validated.

    Returns:
        int: The validated year as an integer.

    Raises:
        ValidationError: If the input string is not a valid year.
    """
    try:
        # Try to parse the input string as a year (e.g., "2023", "1990")
        if year_str:
            year = int(year_str)
            if year < 1900 or year > 2100:
                raise ValueError
            return year
    except ValueError:
        # Raise a ValidationError if the input is not a valid year
        raise ValidationError({'year': f'"{year_str}" is not a valid year.'})