from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db.models import Q

class BaseDBView(APIView):
    model_class = None
    serializer_class = None 
    pagination_class = None  # Set this in your child classes if needed

    def post(self, request):
        # Create a new instance of the model
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, index=None):
        if index is not None:
            # Retrieve a specific instance by index
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
                query = Q()
                for field in self.model_class._meta.get_fields():
                    if hasattr(field, 'related_model'):
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

    def patch(self, request, index=None):
        if index is not None:
            # Update a specific instance by index
            try:
                obj = self.model_class.objects.get(id=index)
            except self.model_class.DoesNotExist:
                raise NotFound("Data not found")
        else:
            # Update the currently logged-in user's instance if index is not provided
            try:
                obj = self.model_class.objects.get(user=request.user)  # Adjust according to your model structure
            except self.model_class.DoesNotExist:
                raise NotFound("Data not found for the logged-in user.")

        serializer = self.serializer_class(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, index=None):
        if index is not None:
            # Replace a specific instance by index
            try:
                obj = self.model_class.objects.get(id=index)
            except self.model_class.DoesNotExist:
                raise NotFound("Data not found")
        else:
            # Replace the currently logged-in user's instance if index is not provided
            try:
                obj = self.model_class.objects.get(user=request.user)  # Adjust according to your model structure
            except self.model_class.DoesNotExist:
                raise NotFound("Data not found for the logged-in user.")

        serializer = self.serializer_class(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, index):
        try:
            obj = self.model_class.objects.get(id=index)
        except self.model_class.DoesNotExist:
            raise NotFound("Data not found")
        
        obj.delete()
        return Response({'message': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
