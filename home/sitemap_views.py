"""
Custom sitemap index view to generate the correct sitemap URLs
"""
from django.contrib.sitemaps import Sitemap
from django.template.response import TemplateResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.urls import reverse
from .sitemaps import GoogleNewsSitemap


def custom_sitemap_index(request, sitemaps):
    """
    Custom sitemap index view that generates URLs in the format:
    /sitemaps/news-sitemap.xml (Google News sitemap)
    /sitemaps/section-sitemap.xml
    /sitemaps/topic-sitemap.xml
    """
    # Map sitemap names to custom URL names
    sitemap_url_map = {
        'news': 'google-news-sitemap',  # Google News sitemap
        'topic': 'topic-sitemap',
        'category': 'category-sitemap',
    }
    
    # Build sitemap entries with custom URLs
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    
    sitemaps_list = []
    for section, site in sitemaps.items():
        # Special handling for Google News sitemap
        if section == 'news':
            # Use GoogleNewsSitemap to get lastmod
            google_news_sitemap = GoogleNewsSitemap()
            items = list(google_news_sitemap.items())
            lastmod = None
            if items:
                try:
                    lastmods = []
                    for item in items[:100]:  # Limit to first 100 items for performance
                        try:
                            item_lastmod = google_news_sitemap.lastmod(item)
                            if item_lastmod:
                                lastmods.append(item_lastmod)
                        except Exception:
                            continue
                    if lastmods:
                        lastmod = max(lastmods)
                except Exception:
                    try:
                        if items[0]:
                            lastmod = google_news_sitemap.lastmod(items[0])
                    except Exception:
                        pass
            
            # Build URL for Google News sitemap
            try:
                url_path = reverse('google-news-sitemap')
                loc = f"{protocol}://{current_site.domain}{url_path}"
            except Exception:
                loc = f"{protocol}://{current_site.domain}/sitemaps/news-sitemap.xml"
            
            sitemaps_list.append({
                'location': loc,
                'lastmod': lastmod,
            })
        else:
            # Regular sitemap handling
            if isinstance(site, type) and issubclass(site, Sitemap):
                site_instance = site()
            else:
                site_instance = site
            
            # Get the last modification date (most recent update)
            items = list(site_instance.items())
            lastmod = None
            if items:
                # Try to get lastmod from all items and find the most recent
                try:
                    lastmods = []
                    for item in items[:100]:  # Limit to first 100 items for performance
                        try:
                            item_lastmod = site_instance.lastmod(item)
                            if item_lastmod:
                                lastmods.append(item_lastmod)
                        except Exception:
                            continue
                    if lastmods:
                        lastmod = max(lastmods)
                except Exception:
                    # Fallback: try first item only
                    try:
                        if items[0]:
                            lastmod = site_instance.lastmod(items[0])
                    except Exception:
                        pass
            
            # Use custom URL name if available
            url_name = sitemap_url_map.get(section, f'sitemap-{section}')
            
            # Build the URL
            try:
                url_path = reverse(url_name)
                loc = f"{protocol}://{current_site.domain}{url_path}"
            except Exception:
                # Fallback to default format
                loc = f"{protocol}://{current_site.domain}/sitemaps/{section}-sitemap.xml"
            
            sitemaps_list.append({
                'location': loc,
                'lastmod': lastmod,
            })
    
    # Render the sitemap index template
    return TemplateResponse(request, 'sitemap_index.xml', {
        'sitemaps': sitemaps_list,
    }, content_type='application/xml')

