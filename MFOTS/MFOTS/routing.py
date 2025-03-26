from channels.routing import URLRouter
from main.routing import websocket_urlpatterns as main_websocket_urlpatterns

websocket_urlpatterns = URLRouter([
  *main_websocket_urlpatterns,
])