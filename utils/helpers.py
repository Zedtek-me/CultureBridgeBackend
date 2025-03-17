from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from typing import List, Union, Optional, Type


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
