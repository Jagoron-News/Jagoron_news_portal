"""
Template tags for SEO meta tags and structured data
"""
from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
from home.models import SiteInfo
import json
from datetime import datetime

register = template.Library()


@register.inclusion_tag('seo/meta_tags.html', takes_context=True)
def seo_meta_tags(context):
    """
    Generate all SEO meta tags (title, description, author, OG, Twitter)
    """
    request = context.get('request')
    news = context.get('news')
    page = context.get('page')
    selected_section = context.get('selected_section')
    selected_subsection = context.get('selected_subsection')
    
    # Get site info
    site_info = SiteInfo.objects.first()
    site_name = site_info.name if site_info else "জাগরণ নিউজ"
    
    # Get current URL
    current_url = request.build_absolute_uri() if request else ""
    
    # Initialize SEO data
    seo_data = {
        'meta_title': '',
        'meta_description': '',
        'meta_author': '',
        'canonical_url': current_url,  # Default to current URL
        'og_title': '',
        'og_description': '',
        'og_image': '',
        'og_type': 'article',
        'og_site_name': site_name,
        'og_url': current_url,
        'og_locale': 'bn_BD',
        'twitter_card': 'summary_large_image',
        'twitter_title': '',
        'twitter_description': '',
        'twitter_image': '',
    }
    
    # Get SEO data from News, Page, Section, or SubSection
    seo_obj = None
    
    # Priority: SubSection > Section > News > Page
    if selected_subsection:
        try:
            seo_obj = selected_subsection.seo
        except:
            pass
        
        # Fallback to subsection fields if no SEO object
        if not seo_obj:
            seo_data['meta_title'] = selected_subsection.title or ''
            seo_data['meta_description'] = f'{selected_subsection.title} - {site_name}' if selected_subsection.title else ''
            seo_data['og_title'] = selected_subsection.title or ''
            seo_data['og_description'] = seo_data['meta_description']
            seo_data['og_type'] = 'website'
            seo_data['twitter_title'] = selected_subsection.title or ''
            seo_data['twitter_description'] = seo_data['meta_description']
    
    elif selected_section:
        try:
            seo_obj = selected_section.seo
        except:
            pass
        
        # Fallback to section fields if no SEO object
        if not seo_obj:
            seo_data['meta_title'] = selected_section.title or ''
            seo_data['meta_description'] = f'{selected_section.title} - {site_name}' if selected_section.title else ''
            seo_data['og_title'] = selected_section.title or ''
            seo_data['og_description'] = seo_data['meta_description']
            seo_data['og_type'] = 'website'
            seo_data['twitter_title'] = selected_section.title or ''
            seo_data['twitter_description'] = seo_data['meta_description']
    
    elif news:
        try:
            seo_obj = news.seo
        except:
            pass
        
        # Fallback to news fields if no SEO object
        if not seo_obj:
            seo_data['meta_title'] = news.title or ''
            seo_data['meta_description'] = news.sub_content or ''
            seo_data['meta_author'] = news.reporter or ''
            seo_data['og_title'] = news.title or ''
            seo_data['og_description'] = news.sub_content or ''
            if news.heading_image:
                try:
                    seo_data['og_image'] = request.build_absolute_uri(news.heading_image.url) if request else news.heading_image.url
                except:
                    seo_data['og_image'] = news.heading_image.url
            elif news.main_image:
                try:
                    seo_data['og_image'] = request.build_absolute_uri(news.main_image.url) if request else news.main_image.url
                except:
                    seo_data['og_image'] = news.main_image.url
            else:
                seo_data['og_image'] = ''
            seo_data['twitter_title'] = news.title or ''
            seo_data['twitter_description'] = news.sub_content or ''
            seo_data['twitter_image'] = seo_data.get('og_image', '')
    
    elif page:
        try:
            seo_obj = page.seo
        except:
            pass
        
        # Fallback to page fields if no SEO object
        if not seo_obj:
            seo_data['meta_title'] = page.title or ''
            seo_data['meta_description'] = ''
            seo_data['og_title'] = page.title or ''
            seo_data['og_description'] = ''
    
    # Override with SEO object data if exists
    if seo_obj:
        seo_data['meta_title'] = seo_obj.meta_title or seo_data.get('meta_title', '')
        seo_data['meta_description'] = seo_obj.meta_description or seo_data.get('meta_description', '')
        seo_data['meta_author'] = seo_obj.meta_author or seo_data.get('meta_author', '')
        # Canonical URL - use custom if set, otherwise use current URL
        seo_data['canonical_url'] = seo_obj.canonical_url or current_url
        seo_data['og_title'] = seo_obj.og_title or seo_obj.meta_title or seo_data.get('og_title', '')
        seo_data['og_description'] = seo_obj.og_description or seo_obj.meta_description or seo_data.get('og_description', '')
        seo_data['og_type'] = seo_obj.og_type or 'article'
        seo_data['og_site_name'] = seo_obj.og_site_name or site_name
        seo_data['twitter_card'] = seo_obj.twitter_card or 'summary_large_image'
        seo_data['twitter_title'] = seo_obj.twitter_title or seo_obj.meta_title or seo_data.get('twitter_title', '')
        seo_data['twitter_description'] = seo_obj.twitter_description or seo_obj.meta_description or seo_data.get('twitter_description', '')
        
        # Handle images
        if seo_obj.og_image:
            try:
                seo_data['og_image'] = request.build_absolute_uri(seo_obj.og_image.url) if request else seo_obj.og_image.url
            except:
                seo_data['og_image'] = seo_obj.og_image.url
        elif news and news.heading_image:
            try:
                seo_data['og_image'] = request.build_absolute_uri(news.heading_image.url) if request else news.heading_image.url
            except:
                seo_data['og_image'] = news.heading_image.url
        elif news and news.main_image:
            try:
                seo_data['og_image'] = request.build_absolute_uri(news.main_image.url) if request else news.main_image.url
            except:
                seo_data['og_image'] = news.main_image.url
        elif selected_section or selected_subsection:
            # For sections/subsections, use site logo or default image if available
            if site_info and site_info.logo:
                try:
                    seo_data['og_image'] = request.build_absolute_uri(site_info.logo.url) if request else site_info.logo.url
                except:
                    seo_data['og_image'] = site_info.logo.url
        
        if seo_obj.twitter_image:
            try:
                seo_data['twitter_image'] = request.build_absolute_uri(seo_obj.twitter_image.url) if request else seo_obj.twitter_image.url
            except:
                seo_data['twitter_image'] = seo_obj.twitter_image.url
        else:
            seo_data['twitter_image'] = seo_data.get('og_image', '')
    
    # Get image dimensions if image exists
    og_image_width = ''
    og_image_height = ''
    og_image_type = ''
    og_image_alt = seo_data['og_title'] or site_name
    
    if seo_data['og_image']:
        # Try to get dimensions from SEO object's image
        if seo_obj and seo_obj.og_image:
            try:
                from PIL import Image
                img = Image.open(seo_obj.og_image.path)
                og_image_width = str(img.width)
                og_image_height = str(img.height)
                og_image_type = f"image/{img.format.lower()}" if img.format else 'image/jpeg'
            except:
                pass
        
        # Default dimensions if not found
        if not og_image_width:
            og_image_width = '1200'
            og_image_height = '630'
            og_image_type = 'image/jpeg'
    
    seo_data['og_image_width'] = og_image_width
    seo_data['og_image_height'] = og_image_height
    seo_data['og_image_type'] = og_image_type
    seo_data['og_image_alt'] = og_image_alt
    seo_data['twitter_image_alt'] = og_image_alt
    
    # Update URL
    seo_data['og_url'] = current_url
    
    # Ensure canonical_url is always set (best practice - every page should have a canonical tag)
    if not seo_data.get('canonical_url'):
        seo_data['canonical_url'] = current_url
    
    return seo_data


@register.simple_tag(takes_context=True)
def article_schema(context):
    """
    Generate Article structured data (JSON-LD) for news articles
    """
    request = context.get('request')
    news = context.get('news')
    
    if not news:
        return ''
    
    site_info = SiteInfo.objects.first()
    site_name = site_info.name if site_info else "জাগরণ নিউজ"
    site_url = request.build_absolute_uri('/') if request else ''
    
    # Get author
    author_name = news.reporter or site_name
    
    # Get image
    image_url = ''
    if news.heading_image:
        image_url = request.build_absolute_uri(news.heading_image.url) if request else news.heading_image.url
    elif news.main_image:
        image_url = request.build_absolute_uri(news.main_image.url) if request else news.main_image.url
    
    # Get category
    categories = [cat.name for cat in news.category.all()] if hasattr(news, 'category') else []
    
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": news.title or '',
        "description": news.sub_content or '',
        "image": image_url,
        "datePublished": news.created_at.isoformat() if news.created_at else '',
        "dateModified": news.updated_at.isoformat() if news.updated_at else '',
        "author": {
            "@type": "Person",
            "name": author_name
        },
        "publisher": {
            "@type": "Organization",
            "name": site_name,
            "logo": {
                "@type": "ImageObject",
                "url": request.build_absolute_uri(site_info.logo.url) if site_info and site_info.logo else ''
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": request.build_absolute_uri(news.get_absolute_url()) if request else news.get_absolute_url()
        }
    }
    
    if categories:
        schema["articleSection"] = categories[0] if categories else ''
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, indent=2)}</script>')


@register.simple_tag(takes_context=True)
def organization_schema(context):
    """
    Generate Organization structured data (JSON-LD) - should be on all pages
    """
    request = context.get('request')
    site_info = SiteInfo.objects.first()
    
    if not site_info:
        return ''
    
    site_name = site_info.name or "জাগরণ নিউজ"
    site_url = request.build_absolute_uri('/') if request else ''
    logo_url = request.build_absolute_uri(site_info.logo.url) if site_info.logo else ''
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": site_name,
        "url": site_url,
        "logo": logo_url
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, indent=2)}</script>')


@register.simple_tag(takes_context=True)
def breadcrumb_schema(context):
    """
    Generate Breadcrumb structured data (JSON-LD)
    """
    request = context.get('request')
    news = context.get('news')
    
    if not news or not request:
        return ''
    
    site_url = request.build_absolute_uri('/')
    current_url = request.build_absolute_uri()
    
    breadcrumb_items = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": site_url
        }
    ]
    
    # Add section if exists
    if news.section:
        breadcrumb_items.append({
            "@type": "ListItem",
            "position": 2,
            "name": news.section.title,
            "item": request.build_absolute_uri(news.section.get_absolute_url())
        })
    
    # Add current page
    breadcrumb_items.append({
        "@type": "ListItem",
        "position": len(breadcrumb_items) + 1,
        "name": news.title or 'News',
        "item": current_url
    })
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_items
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, indent=2)}</script>')


@register.simple_tag(takes_context=True)
def website_schema(context):
    """
    Generate Website structured data (JSON-LD) - for homepage
    """
    request = context.get('request')
    site_info = SiteInfo.objects.first()
    
    if not site_info:
        return ''
    
    site_name = site_info.name or "জাগরণ নিউজ"
    site_url = request.build_absolute_uri('/') if request else ''
    
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site_name,
        "url": site_url
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, indent=2)}</script>')


@register.simple_tag(takes_context=True)
def newspaper_schema(context):
    """
    Generate comprehensive Newspaper structured data (JSON-LD) - should be on all pages
    """
    request = context.get('request')
    site_info = SiteInfo.objects.first()
    
    if not site_info:
        return ''
    
    site_name = site_info.name or "জাগরণ নিউজ"
    site_url = request.build_absolute_uri('/') if request else 'https://jagoronnews.com/'
    
    # Handle logo URL
    logo_url = 'https://jagoronnews.com/media/logo/jn_final_InHmW00.png'  # Default fallback
    if site_info and site_info.logo:
        try:
            logo_url = request.build_absolute_uri(site_info.logo.url) if request else site_info.logo.url
        except:
            pass  # Use default if error
    
    # Build hasPart array dynamically from sections and subsections
    has_part = []
    
    # Get all active sections and subsections
    from home.models import NavbarItem, SubSection
    
    # Add sections
    for section in NavbarItem.objects.filter(is_active=True).order_by('position'):
        if section.english_title:  # Only add sections with slugs
            section_url = request.build_absolute_uri(section.get_absolute_url()) if request else section.get_absolute_url()
            has_part.append({
                "@type": "CreativeWork",
                "name": section.title,
                "url": section_url
            })
    
    # Add subsections
    for subsection in SubSection.objects.filter(is_active=True).select_related('section').order_by('position'):
        if subsection.english_title and subsection.section and subsection.section.english_title:
            subsection_url = request.build_absolute_uri(subsection.get_absolute_url()) if request else subsection.get_absolute_url()
            has_part.append({
                "@type": "CreativeWork",
                "name": subsection.title,
                "url": subsection_url
            })
    
    # Build about array with common topics
    about = [
        {"@type": "Thing", "name": "National News"},
        {"@type": "Thing", "name": "Country News"},
        {"@type": "Thing", "name": "Regional News of Bangladesh"},
        {"@type": "Thing", "name": "International News"},
        {"@type": "Thing", "name": "Politics"},
        {"@type": "Thing", "name": "Opinion and Editorials"},
        {"@type": "Thing", "name": "Religion"},
        {"@type": "Thing", "name": "Education"},
        {"@type": "Thing", "name": "Campus News"},
        {"@type": "Thing", "name": "Sports"},
        {"@type": "Thing", "name": "Cricket"},
        {"@type": "Thing", "name": "Football"},
        {"@type": "Thing", "name": "Kabaddi"},
        {"@type": "Thing", "name": "Economy"},
        {"@type": "Thing", "name": "Entertainment"},
        {"@type": "Thing", "name": "Science and Technology"},
        {"@type": "Thing", "name": "Health"},
        {"@type": "Thing", "name": "Weather News"},
        {"@type": "Thing", "name": "Travel and Tourism"},
        {"@type": "Thing", "name": "Journeys and Lifestyle"},
        {"@type": "Thing", "name": "Jobs and Careers"},
        {"@type": "Thing", "name": "Agriculture News"},
        {"@type": "Thing", "name": "India News"},
        {"@type": "Thing", "name": "Global Affairs by Region"}
    ]
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Newspaper",
        "@id": f"{site_url}#newspaper",
        "name": "Jagoron News",
        "alternateName": site_name,
        "url": site_url,
        "description": "Jagoron News is an independent digital newspaper in Bangladesh delivering fact-based, unbiased, and ethical journalism across national, international, political, social, economic, and public interest topics.",
        "abstract": "Truth Matters. Stay Awake. Jagoron News publishes verified, independent, and responsible journalism with a strong commitment to transparency, accountability, and democratic values.",
        "inLanguage": ["bn-BD", "en"],
        "genre": "News, Journalism",
        "countryOfOrigin": {
            "@type": "Country",
            "name": "Bangladesh"
        },
        "locationCreated": {
            "@type": "Place",
            "name": "Dhaka, Bangladesh",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "11/8/C, Panthapath",
                "addressLocality": "Dhaka",
                "postalCode": "1215",
                "addressCountry": "BD"
            }
        },
        "startDate": "2024-10-23",
        "publisher": {
            "@type": "Organization",
            "@id": f"{site_url}#organization",
            "name": "Jagoron News",
            "url": site_url,
            "logo": {
                "@type": "ImageObject",
                "url": logo_url
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+8801301330088",
                "contactType": "Editorial & Public Inquiries",
                "email": "jagoronnewss@gmail.com",
                "areaServed": "BD",
                "availableLanguage": ["bn", "en"]
            },
            "sameAs": [
                "https://www.facebook.com/jagoronnewss",
                "https://www.instagram.com/jagoronnews/",
                "https://www.linkedin.com/company/jagoron-news/",
                "https://www.tiktok.com/@jagoron_news",
                "https://www.youtube.com/@DailyJagoronNews",
                "https://en.wikipedia.org/wiki/Jagoron_News"
            ]
        },
        "editor": {
            "@type": "Person",
            "@id": f"{site_url}editor/#person",
            "name": "MD Saddam Hosen",
            "jobTitle": "Editor-in-Chief",
            "url": f"{site_url}editor/",
            "description": "Editor-in-Chief of Jagoron News, leading the newsroom with a commitment to ethical, factual, and impactful journalism."
        },
        "accountablePerson": {
            "@type": "Person",
            "name": "MD Saddam Hosen",
            "jobTitle": "Editor-in-Chief"
        },
        "publishingPrinciples": {
            "@type": "CreativeWork",
            "name": "Editorial Guidelines & Ethics Policy",
            "url": f"{site_url}default-pages/editorialguidelines/"
        },
        "isAccessibleForFree": True,
        "isFamilyFriendly": True,
        "audience": {
            "@type": "Audience",
            "audienceType": "General Public"
        },
        "keywords": "Bangladesh news, national news, international news, politics, economy, sports, education, health, agriculture, technology, entertainment, jobs",
        "about": about,
        "hasPart": has_part,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"{site_url}about/"
        }
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, indent=2)}</script>')
