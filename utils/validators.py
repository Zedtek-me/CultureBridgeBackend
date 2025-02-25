import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from typing import List, Dict, Optional

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
        logger.debug(f"length of personality type: {len(value)}\n type of personality_type: {type(description_values)}")
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
