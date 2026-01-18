"""
Custom view for Google News sitemap with proper XML format
"""
from django.template.response import TemplateResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from datetime import timedelta
from .sitemaps import GoogleNewsSitemap
from .models import News
import logging

logger = logging.getLogger(__name__)


def google_news_sitemap(request):
    """
    Custom view for Google News sitemap that includes:
    - Google News namespace
    - Image namespace
    - Proper news:news tags
    """
    try:
        sitemap = GoogleNewsSitemap()
        
        # Debug: Check what we're querying
        now = timezone.now()
        cutoff_time = now - timedelta(hours=48)
        
        # Get total published news count for debugging
        total_published = News.published.count()
        recent_news = News.published.filter(created_at__gte=cutoff_time).count()
        
        logger.info(f"Google News sitemap debug: Total published={total_published}, Recent (48h)={recent_news}, Cutoff={cutoff_time}, Now={now}")
        
        items = list(sitemap.items())
        
        # Debug: Log how many items we found
        logger.info(f"Google News sitemap: Found {len(items)} items from last 48 hours")
        
        # Get site info
        current_site = get_current_site(request)
        protocol = 'https' if request.is_secure() else 'http'
        site_url = f"{protocol}://{current_site.domain}"
        
        # Prepare items with all necessary data
        sitemap_items = []
        for item in items:
            try:
                image_url = sitemap.get_image_url(item, request)
                sitemap_items.append({
                    'item': item,
                    'location': f"{site_url}{sitemap.location(item)}",
                    'publication_date': sitemap.get_news_publication_date(item),
                    'title': sitemap.get_news_title(item),
                    'keywords': sitemap.get_news_keywords(item),
                    'image_url': image_url,
                    'image_caption': sitemap.get_image_caption(item),
                })
            except Exception as e:
                logger.error(f"Error processing news item {item.id}: {e}")
                continue
        
        context = {
            'items': sitemap_items,
            'publication_name': sitemap.get_publication_name(),
            'publication_language': sitemap.get_publication_language(),
            'site_url': site_url,
        }
        
        return TemplateResponse(
            request,
            'google_news_sitemap.xml',
            context,
            content_type='application/xml'
        )
    except Exception as e:
        logger.error(f"Error generating Google News sitemap: {e}", exc_info=True)
        # Return empty sitemap on error
        current_site = get_current_site(request)
        protocol = 'https' if request.is_secure() else 'http'
        site_url = f"{protocol}://{current_site.domain}"
        return TemplateResponse(
            request,
            'google_news_sitemap.xml',
            {
                'items': [],
                'publication_name': 'জাগরণ নিউজ',
                'publication_language': 'bn',
                'site_url': site_url,
            },
            content_type='application/xml'
        )

