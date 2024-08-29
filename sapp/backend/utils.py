from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404

class BaseDBView(APIView):
    model = None

    def post(self, request):
        # Post data into the db
        title = request.data['title']
        description = request.data['description']
        status = request.data['status']
        self.model.objects.create(title=title, description=description, status=status)
        return Response({'message': 'Data posted successfully'})

    def get(self, request):
        # Get count of the data
        count = self.model.objects.count()
        return Response({'count': count})

    def get_by_index(self, request, index):
        # Pass index and get the data from the db
        try:
            data = self.model.objects.get(id=index)
        except self.model.DoesNotExist:
            raise Http404("Data not found")
        return Response({'data': {'id': data.id, 'title': data.title, 'description': data.description, 'status': data.status}})

    def post_by_index(self, request, index):
        # Pass index to update data in the db
        try:
            obj = self.model.objects.get(id=index)
        except self.model.DoesNotExist:
            raise Http404("Data not found")

        obj.title = request.data.get('title', obj.title)
        obj.description = request.data.get('description', obj.description)
        obj.status = request.data.get('status', obj.status)
        obj.save()
        
        return Response({'message': 'Data updated successfully'})

    def delete_by_index(self, request, index):
        # Pass index into db and delete that particular value in db
        try:
            obj = self.model.objects.get(id=index)
        except self.model.DoesNotExist:
            raise Http404("Data not found")
        
        obj.delete()
        return Response({'message': 'Data deleted successfully'})
