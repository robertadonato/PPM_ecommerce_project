from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('prodotti/', views.ProductListView.as_view(), name='product_list'),
    path('chi-siamo/', views.chi_siamo_view, name='chi_siamo'),
    path('servizi/', views.servizi_view, name='servizi'),
    path('contatti/', views.contatti_view, name='contatti'),
    path('product/<int:pk>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('api/offers/<str:offer_code>/', views.get_offer_details, name='get_offer_details'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    path('manage/products/', views.manage_products, name='manage_products'),
    path('manage/products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('manage/products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('manage/products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('manage/products/<int:pk>/stats/', views.product_stats, name='product_stats'),
    path('manage/categories/', views.manage_categories, name='manage_categories'),
    path('manage/categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('manage/categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('manage/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]