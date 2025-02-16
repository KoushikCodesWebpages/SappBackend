import json
import time
import queue
from django.http import StreamingHttpResponse

# Queue to store notifications
notification_queue = queue.Queue()

def event_stream():
    """Generator function for SSE, listening to the queue."""
    while True:
        try:
            # Wait for a notification
            notification = notification_queue.get(timeout=30)  # Blocks for 30 seconds
            data = json.dumps(notification)
            yield f"data: {data}\n\n"  # SSE format
        except queue.Empty:
            yield ": keep-alive\n\n"  # Prevents connection timeout

def sse_notifications(request):
    """SSE endpoint to stream real-time notifications."""
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response

def send_notification(message):
    """Function to add a notification to the queue."""
    notification_queue.put({"message": message, "timestamp": time.time()})
