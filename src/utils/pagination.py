from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    page = 1
    page_size = 20
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_data(self, data):
        return {
            "results": data,
            "total": self.page.paginator.count,
            "pages": self.page.paginator.num_pages,
            "is_last": not self.page.has_next(),
        }

    def get_paginated_response(self, data):
        return Response(self.get_paginated_data(data))

    def get_paginated_response_schema(self, schema):
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
