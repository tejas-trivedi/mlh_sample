from django.urls import path
from .views import UpcomingEventsView, OngoingEventsView, PastEventsView, EventInfo, EventRegister, EventView

urlpatterns = [
    path('upcoming/', UpcomingEventsView.as_view(), name="upcoming"),
    path('ongoing/', OngoingEventsView.as_view()),
    path('past/', PastEventsView.as_view()),
    path('info/<event_name>', EventInfo.as_view()),
    path('eventcheck/', EventView.as_view()),
    path('eventregister/', EventRegister.as_view()),
]
