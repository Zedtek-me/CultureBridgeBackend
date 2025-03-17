import logging
from datetime import datetime, date, timedelta

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from typing import List, Dict, Optional, Type

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BaseValidator:
    
    @classmethod
    def validate_self_description(
        cls, value: list
    ):
        """Validate the personality type

        Args:
            personality_type (str): the personality type list
        """
        description_values = [isinstance(p_type, str) for p_type in value]
        if not isinstance(value, list) or not all(description_values):
            raise ValidationError(
                _("Personality type must be an array of strings")
            )
        if (
            len(description_values) > 3
            or
            len(description_values) < 3
        ):
            raise ValidationError(
                _("Personality type must neither be greater nor less than 3")
            )



def format_date(date_str: str) -> Type[datetime]:
    """converts a date string to a `datetime` obj"""
    if not date_str:
        return date_str
    _date = datetime.strptime(date_str, "%Y-%m-%d")
    return _date
