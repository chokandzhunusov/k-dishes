from django.urls import path, re_path

from .views import HomeListView, OrderDetailView, DishDetailView, StatisticsListView

urlpatterns = [
    path("", view=HomeListView.as_view(), name="home"),
    path('order/<slug:slug>/', OrderDetailView.as_view(), name='order_detail'),
    path('dish/<int:pk>/', DishDetailView.as_view(), name='dish_detail'),
    path('statistics/', StatisticsListView.as_view(), name='statistics_list')

]