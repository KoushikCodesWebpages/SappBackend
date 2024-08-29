from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404

class BaseDBView(APIView):
    model = None

    def post(self, request, index=None):
        if index is not None:
            # Update existing record
            try:
                obj = self.model.objects.get(id=index)
            except self.model.DoesNotExist:
                raise Http404("Data not found")

            # Update fields with the data from the request
            obj.title = request.data.get('title', obj.title)
            obj.description = request.data.get('description', obj.description)
            obj.status = request.data.get('status', obj.status)
            obj.save()

            return Response({'message': 'Data updated successfully'})
        else:
            # Create new record
            title = request.data['title']
            description = request.data['description']
            status = request.data['status']
            self.model.objects.create(title=title, description=description, status=status)
            return Response({'message': 'Data posted successfully'})
    
    def get(self, request, index=None):
        if index is not None:
            try:
                obj = self.model.objects.get(id=index)
                data = {
                    'id': obj.id,
                    'title': obj.title,
                    'description': obj.description,
                    'status': obj.status
                }
                return Response(data)
            except self.model.DoesNotExist:
                raise Http404("Data not found")
        else:
            # Handle listing or count
            count = self.model.objects.count()
            return Response({'count': count})

    def delete(self, request, index):
        try:
            obj = self.model.objects.get(id=index)
        except self.model.DoesNotExist:
            raise Http404("Data not found")
        
        obj.delete()
        return Response({'message': 'Data deleted successfully'})
