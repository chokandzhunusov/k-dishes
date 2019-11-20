from django.urls import path, re_path

import dishes.views as views

urlpatterns = [
    path("", view=views.HomeListView.as_view(), name="home"),
    path('order/<slug:slug>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/<slug:slug>/delete', views.OrderDeleteView.as_view(), name='order_delete'),
    path('dish/<int:pk>/', views.DishDetailView.as_view(), name='dish_detail'),
    path('dish/<int:pk>/edit', views.DishEditView.as_view(), name='dish_edit'),
    path('statistics/', views.StatisticsListView.as_view(), name='statistics_list'),
    path('statistics/<int:pk>/', views.DishStatisticsView.as_view(), name='dish_statistics'),
    path('upload_file/', views.UploadFileView.as_view(), name='upload_file'),
    path('upload_dish_price/', views.UploadDishPriceView.as_view(), name='upload_dish_price'),
    path('create_markets/', views.CreateMarketsView.as_view(), name='create_markets'),
]
