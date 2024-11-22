from typing import Dict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    page = 1
    page_size = 20
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_data(self, data: Dict) -> Dict:
        return {
            "results": data,
            "total": self.page.paginator.count,  # type: ignore[attr-defined]
            "pages": self.page.paginator.num_pages,  # type: ignore[attr-defined]
            "is_last": not self.page.has_next(),  # type: ignore[attr-defined]
        }

    def get_paginated_response(self, data: Dict) -> Dict:
        return Response(self.get_paginated_data(data))

    def get_paginated_response_schema(self, schema: Dict) -> Dict:
        return {
            "type": "object",
            "properties": {
                "total": {
                    "type": "integer",
                    "example": 123,
                },
                "pages": {
                    "type": "integer",
                    "example": 1,
                },
                "is_last": {"type": "boolean", "example": False},
                "results": schema,
            },
        }
