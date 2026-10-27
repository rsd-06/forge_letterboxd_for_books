from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.book_search, name='book_search'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/ol/<str:ol_key>/', views.book_detail, name='book_detail_ol'),
    path('book/<int:book_id>/rate/', views.log_or_rate_book, name='log_or_rate_book'),
    path('book/<int:book_id>/shelf/', views.toggle_readlist_item, name='toggle_readlist_item'),
    path('review/<int:review_id>/comment/', views.add_review_comment, name='add_review_comment'),

    # Shelves and lists
    path('lists/', views.readlists_view, name='my_readlists'),
    path('lists/new/', views.create_readlist, name='create_readlist'),
    path('user/<str:username>/lists/', views.readlists_view, name='user_readlists'),
    path('user/<str:username>/list/<slug:slug>/', views.readlist_detail, name='readlist_detail'),

    # Profile & Social
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('user/<str:username>/follow/', views.toggle_friend, name='toggle_friend'),
    path('community/', views.community, name='community'),

    # AI Assistant & Recommendations & Feedback
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('api/chat-feedback/', views.submit_chat_feedback, name='chat_feedback'),

    # FAQs, Health Check & Support Tickets
    path('faq/', views.faq_view, name='faq'),
    path('health/', views.health_check, name='health_check'),
    path('support/tickets/', views.support_ticket_view, name='support_tickets'),

    # Error code explorer & simulators (8 error codes)
    path('errors/', views.error_code_explorer, name='error_explorer'),
    path('errors/<int:code>/', views.error_code_explorer, name='error_simulate'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    re_path(r'^(?!media/|static/).*$', views.custom_404_view, name='catch_all_404'),
]
