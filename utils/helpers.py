import logging
from datetime import datetime, date, timedelta
from typing import List, Union, Optional, Type

from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.utils import timezone

logger = logging.getLogger(__name__)

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
        if date_str and time_str:
            datetime_str = f"{date_str} {time_str}"
            tz = timezone.get_current_timezone()
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        return datetime.strptime(date_str, "%Y:%m:%d").replace(tzinfo=tz)
    except (Exception, ValueError) as e:
        logger.exception(f"error occured when formatting date string: {e}")
        return None
