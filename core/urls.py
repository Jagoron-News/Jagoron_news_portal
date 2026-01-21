
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap, index
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path as url
from django.views.static import serve
from django.views.generic import TemplateView  # <--- 1. Added this import
from home.sitemaps import NewsSitemap, TopicSitemap, CategorySitemap, SectionSitemap
from home.sitemap_views import custom_sitemap_index, topic_sitemap_view
from home.google_news_sitemap_view import google_news_sitemap
from home.views import robots_txt_view

# Sitemap dictionary
sitemaps = {
    'news': NewsSitemap,
    'section': SectionSitemap,
    'topic': TopicSitemap,
    'category': CategorySitemap,
}

urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,{'document_root':settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root':settings.STATIC_ROOT}),
    
    # <--- 2. Added this path for ads.txt
    path('ads.txt', TemplateView.as_view(template_name='ads.txt', content_type='text/plain')),
    
    # Robots.txt
    path('robots.txt', robots_txt_view, name='robots_txt'),

    # Sitemaps (must be before home.urls to avoid catch-all pattern conflicts)
    path('sitemap.xml', custom_sitemap_index, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.index'),
    path('sitemaps/news-sitemap.xml', google_news_sitemap, name='google-news-sitemap'),  # Google News sitemap
    path('sitemaps/regular-news-sitemap.xml', sitemap, {'sitemaps': {'news': NewsSitemap}}, name='regular-news-sitemap'),  # Regular news sitemap
    path('sitemaps/section-sitemap.xml', sitemap, {'sitemaps': {'section': SectionSitemap}}, name='section-sitemap'),
    path('sitemaps/topic-sitemap.xml', topic_sitemap_view, name='topic-sitemap'),
    # Handle trailing slash for sitemaps
    path('sitemaps/topic-sitemap.xml/', topic_sitemap_view, name='topic-sitemap-slash'),
    path('sitemaps/section-sitemap.xml/', sitemap, {'sitemaps': {'section': SectionSitemap}}, name='section-sitemap-slash'),
    path('sitemaps/news-sitemap.xml/', google_news_sitemap, name='google-news-sitemap-slash'),
    path('sitemaps/regular-news-sitemap.xml/', sitemap, {'sitemaps': {'news': NewsSitemap}}, name='regular-news-sitemap-slash'),
    
    # Debug endpoint (remove in production)
    path('debug/news-sitemap-debug/', google_news_sitemap, name='news-sitemap-debug'),

    path('jag-admin/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
    path('', include('home.urls')),
    path('', include('account.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'home.views.custom_404_view'
