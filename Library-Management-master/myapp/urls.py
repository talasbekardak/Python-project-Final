from django.urls import path
from myapp import views

app_name = 'myapp'

urlpatterns = [
    # Define URL patterns for different views in the app

    # Index view to display the main page
    path(r'', views.IndexView.as_view(), name='index'),

    # Detail view for displaying book details using the book_id
    path(r'<int:book_id>/', views.DetailView.as_view(), name='detail'),

    # Findbooks view to search for books
    path(r'findbooks/', views.findbooks, name='findbooks'),

    # Place_order view for placing an order
    path(r'place_order/', views.place_order, name='place_order'),

    # Review view for book reviews
    path(r'review/', views.review, name='review'),

    # User login view
    path(r'login/', views.user_login, name='login'),

    # User logout view
    path(r'logout/', views.user_logout, name='logout'),

    # Check reviews for a specific book
    path(r'check/<int:book_id>/', views.chk_reviews, name='check_reviews'),

    # Register view for user registration
    path(r'register/', views.register, name='register'),

    # My orders view for displaying user orders
    path(r'orders/', views.my_orders, name='orders'),
]

# Comments:
# - Each path maps a URL pattern to a specific view function or class-based view.
# - The 'name' attribute in each path is used to identify the URL and reference it in templates or code.
# - The '<int:book_id>/' captures an integer value for the book_id in the URL for the detail and check reviews views.
# - 'app_name' defines the application namespace to avoid URL naming conflicts between different apps.
# - Consider adding further comments specific to the purpose or functionality of each view if needed.
