"""
Custom pagination classes
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination with additional metadata
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'page_size': self.get_page_size(self.request),
                'page': self.page.number,
                'num_pages': self.page.paginator.num_pages,
            },
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for large datasets (like search results)
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'page_size': self.get_page_size(self.request),
                'page': self.page.number,
                'num_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            },
            'results': data
        })


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for API endpoints
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100