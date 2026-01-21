import logging
from datetime import datetime, date, timedelta
from typing import List, Union, Optional, Type

from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.utils import timezone


def get_logger():
    """returns a configured logger"""
    _logger = logging.getLogger("root")
    _logger.setLevel(logging.DEBUG)
    return _logger


logger = get_logger()

def paginate_data(
    data: Union[List, QuerySet],
    page_count: int = 10, page_no: int = 1
) -> Optional[dict]:
    """quick pagination"""
    paginator = Paginator(data, page_count)
    paginated = paginator.get_page(page_no)
    return {
            "data": paginated.object_list,
            "counts": len(data),
            "page": page_no
        }


def format_date_time(
    date_str: Union[str, None], time_str: Optional[str] = None
) -> Optional[datetime]:
    """formats and return a datetime obj if provided"""
    if not date_str:
        return
    try:
        tz = timezone.get_current_timezone()
        if date_str and time_str:
            datetime_str = f"{date_str} {time_str}"
            return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=tz)
        return datetime.strptime(date_str, "%Y:%m:%d").replace(tzinfo=tz)
    except (Exception, ValueError) as e:
        logger.exception(f"error occured when formatting date string: {e}")
        return None
