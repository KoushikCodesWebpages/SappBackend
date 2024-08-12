class BaseDBView(APIView):
    model = None

    def post(self, request, model_type):
        # Post data into the db
        title = request.data['title']
        description = request.data['description']
        status = request.data['status']
        self.model.objects.create(title=title, description=description, status=status)
        return Response({'message': 'Data posted successfully'})

    def get(self, request, model_type):
        # Get count of the data
        count = self.model.objects.count()
        return Response({'count': count})

    def get_by_index(self, request, index, model_type):
        # Pass index and get the data from the db
        data = self.model.objects.filter(id=index)
        return Response({'data': data})

    def post_by_index(self, request, index, model_type):
        # Pass index to post data into the db
        title = request.data['title']
        description = request.data['description']
        status = request.data['status']
        self.model.objects.filter(id=index).update(title=title, description=description, status=status)
        return Response({'message': 'Data posted successfully'})

    def delete_by_index(self, request, index, model_type):
        # Pass index into db and delete that particular value in db
        self.model.objects.filter(id=index).delete()
        return Response({'message': 'Data deleted successfully'})