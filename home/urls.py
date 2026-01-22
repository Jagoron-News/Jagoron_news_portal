from django.urls import path
from . import views
from django.views.generic import TemplateView # <-- ADD THIS LINE

urlpatterns = [
    path('', views.home, name='home'),
    # Specific routes first (to avoid conflicts with slug-based URLs)

    path('authors/', views.authors_list, name="authors"),
    path('about-us/', views.about_us, name="about_us"),

    path('authors/<slug:slug>/', views.author_detail, name="author_detail"),
    path('topic/<str:tag_name>/', views.topic_news_page, name='topic_news_page'),

    path('ajax/get-subsections/', views.get_subsections, name='get_subsections'),
    path('news/detail/<int:news_id>/', views.news_detail_redirect, name='news_detail_old'),
    path('news/react/<int:news_id>/', views.react_to_news, name='react_to_news'),
    path('news/', views.news_page, name='news_page'),  # Old format for backward compatibility
    path('default-pages/<str:link>/', views.default_page_detail, name='default_page_detail'),
    path('jagoron-1lakh/', views.generate_photo, name='generate_photo'),
    path('search/', views.search_news, name='search_news'),
    path('s/<str:short_code>/', views.redirect_short_url, name='redirect_short_url'),
    path('api/create-short-url/', views.create_short_url, name='create_short_url'),
    path('editor/', TemplateView.as_view(template_name="pages/editor_profile.html"), name='static_editor_page'),
    path('ckeditor/upload/', views.ckeditor_upload, name='ckeditor_upload'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/dashboard/image-stats/', views.dashboard_image_stats, name='dashboard_image_stats'),
    path('admin/dashboard/reporter-stats/', views.dashboard_reporter_stats, name='dashboard_reporter_stats'),
    path('admin/dashboard/content-stats/', views.dashboard_content_stats, name='dashboard_content_stats'),
    # News detail with subsection (must be before other patterns to match integers)
    path('<str:section_slug>/<str:subsection_slug>/<int:news_id>/', views.news_detail_with_subsection, name='news_detail_subsection'),
    # News detail with section only (must be before subsection pattern to match integers)
    path('<str:section_slug>/<int:news_id>/', views.news_detail, name='news_detail'),
    # New slug-based URLs for sections and subsections (must be last to catch all other routes)
    # Exclude sitemaps and other system paths
    path('<str:section_slug>/<str:subsection_slug>/', views.news_page_by_slug, name='news_page_subsection'),
    path('<str:section_slug>/', views.news_page_by_slug, name='news_page_section'),
    # Catch-all pattern for default pages (MUST be last to avoid conflicts)
    path('<slug:slug>/', views.default_page_detail, name='default_page_detail'),

]
