# myapp/utils.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

class BaseDBView(APIView):
    model_class = None
    serializer_class = None
  # Default pagination class

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
            query = request.GET.get('search', '')
            queryset = self.model_class.objects.filter(title__icontains=query)

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
