"""
Template tags for breadcrumbs
"""
from django import template

register = template.Library()


@register.inclusion_tag('breadcrumbs/breadcrumb.html', takes_context=True)
def breadcrumb(context):
    """
    Generate breadcrumb navigation
    Format:
    - Home > Section (for section pages)
    - Home > Section > Subsection (for subsection pages)
    - Home > Section > News Title (for news detail pages)
    - Home > Section > Subsection > News Title (for news with subsection)
    """
    request = context.get('request')
    news = context.get('news')
    selected_section = context.get('selected_section')
    selected_subsection = context.get('selected_subsection')
    page = context.get('page')
    
    breadcrumb_items = []
    
    # Don't show breadcrumb on homepage
    if request and request.path == '/':
        return {'breadcrumb_items': []}
    
    # Always start with Home
    breadcrumb_items.append({
        'title': 'মূলপাতা',
        'url': '/',
        'is_active': False
    })
    
    # For news detail pages
    if news:
        # Add section if exists
        if news.section:
            breadcrumb_items.append({
                'title': news.section.title,
                'url': news.section.get_absolute_url(),
                'is_active': False
            })
        
        # Add subsection if exists
        if news.sub_section:
            breadcrumb_items.append({
                'title': news.sub_section.title,
                'url': news.sub_section.get_absolute_url(),
                'is_active': False
            })
        
        # Add current news title (active) - truncate if too long
        news_title = news.title or 'খবর'
        if len(news_title) > 60:
            news_title = news_title[:57] + '...'
        
        breadcrumb_items.append({
            'title': news_title,
            'url': request.build_absolute_uri() if request else '',
            'is_active': True
        })
    
    # For section/subsection pages
    elif selected_section:
        # Only show breadcrumb if we have a section
        breadcrumb_items.append({
            'title': selected_section.title,
            'url': selected_section.get_absolute_url(),
            'is_active': not selected_subsection  # Active only if no subsection
        })
        
        # Add subsection if exists
        if selected_subsection:
            breadcrumb_items.append({
                'title': selected_subsection.title,
                'url': selected_subsection.get_absolute_url(),
                'is_active': True
            })
    
    # For default pages
    elif page:
        breadcrumb_items.append({
            'title': page.title or 'পেজ',
            'url': request.build_absolute_uri() if request else '',
            'is_active': True
        })
    
    # If no breadcrumb items (except home), don't show breadcrumb
    if len(breadcrumb_items) <= 1:
        return {'breadcrumb_items': []}
    
    return {
        'breadcrumb_items': breadcrumb_items
    }
