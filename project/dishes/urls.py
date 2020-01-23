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
    path('statistics_by_market/', views.StatisticsByMarketListView.as_view(), name='statistics_by_market'),
    path('upload_file/', views.UploadFileView.as_view(), name='upload_file'),
    path('upload_dish_price/', views.UploadDishPriceView.as_view(), name='upload_dish_price'),
    path('create_markets/', views.CreateMarketsView.as_view(), name='create_markets'),
    path('approve_dish/', views.ApproveDish.as_view(), name='approve_dish'),
    path('cancel_dish/', views.CancelDish.as_view(), name='cancel_dish'),
    path('edit_dish/', views.EditDish.as_view(), name='edit_dish'),
]
