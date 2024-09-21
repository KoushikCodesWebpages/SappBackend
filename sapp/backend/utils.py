from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db.models import Q

class BaseDBView(APIView):
    model_class = None
    serializer_class = None
    pagination_class = None  # Set this in your child classes if needed

    def post(self, request, index=None):
        if index is not None:
            try:
                obj = self.model_class.objects.get(id=index)
            except self.model_class.DoesNotExist:
                raise NotFound("Data not found")

            serializer = self.serializer_class(obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, index=None):
        if index is not None:
            try:
                obj = self.model_class.objects.get(id=index)
                serializer = self.serializer_class(obj)
                return Response(serializer.data)
            except self.model_class.DoesNotExist:
                raise NotFound("Data not found")
        else:
            # Handle filtering, sorting, and searching
            queryset = self.model_class.objects.all()

            # Filtering
            filter_params = {key: value for key, value in request.GET.items() if key not in ['sort', 'search', 'page']}
            if filter_params:
                queryset = queryset.filter(**filter_params)

            # Searching
            search = request.GET.get('search', '')
            if search:
                query = Q(title__icontains=search)
                for field in self.model_class._meta.get_fields():
                    if field.name != 'title' and hasattr(field, 'related_model'):
                        query |= Q(**{f"{field.name}__icontains": search})
                queryset = queryset.filter(query)

            # Sorting
            sort = request.GET.get('sort', '')
            if sort:
                queryset = queryset.order_by(sort)

            # Use the pagination class set in the child view
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(paginated_queryset, many=True)

            return paginator.get_paginated_response(serializer.data)

    def delete(self, request, index):
        try:
            obj = self.model_class.objects.get(id=index)
        except self.model_class.DoesNotExist:
            raise NotFound("Data not found")
        
        obj.delete()
        return Response({'message': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
