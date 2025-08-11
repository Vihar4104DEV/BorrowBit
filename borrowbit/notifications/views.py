from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # TODO: Implement notification list logic
        return Response({"message": "Notification list endpoint (to be implemented)"})
