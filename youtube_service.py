import os
import logging
import requests
from urllib.parse import quote

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

def search_nde_videos(query, max_results=10):
    """
    Search for NDE-related educational videos on YouTube.
    Filters results to focus on educational and professional content.
    """
    try:
        if not YOUTUBE_API_KEY:
            return {
                'status': 'error',
                'message': 'YouTube API key not configured'
            }
        
        # Enhanced query with NDE-specific terms
        nde_enhanced_query = f"{query} NDT NDE non-destructive testing inspection tutorial education"
        
        # YouTube Data API search endpoint
        search_url = "https://www.googleapis.com/youtube/v3/search"
        
        params = {
            'part': 'snippet',
            'q': nde_enhanced_query,
            'type': 'video',
            'maxResults': max_results,
            'order': 'relevance',
            'key': YOUTUBE_API_KEY,
            'videoDefinition': 'any',
            'videoDuration': 'any',
            'videoEmbeddable': 'true',
            'safeSearch': 'strict'
        }
        
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        videos = []
        for item in data.get('items', []):
            snippet = item['snippet']
            
            # Filter for educational/professional content
            title = snippet['title'].lower()
            description = snippet['description'].lower()
            
            # Check for educational indicators
            educational_keywords = [
                'tutorial', 'training', 'education', 'course', 'learn', 'how to',
                'guide', 'demonstration', 'explained', 'basics', 'fundamentals',
                'procedure', 'standard', 'certification', 'inspection', 'testing'
            ]
            
            # Check for NDE relevance
            nde_keywords = [
                'ndt', 'nde', 'ultrasonic', 'radiographic', 'magnetic particle',
                'penetrant', 'eddy current', 'visual inspection', 'testing',
                'non-destructive', 'nondestructive', 'inspection'
            ]
            
            has_educational = any(keyword in title or keyword in description for keyword in educational_keywords)
            has_nde_content = any(keyword in title or keyword in description for keyword in nde_keywords)
            
            if has_educational and has_nde_content:
                video_info = {
                    'video_id': item['id']['videoId'],
                    'title': snippet['title'],
                    'description': snippet['description'][:200] + '...' if len(snippet['description']) > 200 else snippet['description'],
                    'channel_title': snippet['channelTitle'],
                    'published_at': snippet['publishedAt'],
                    'thumbnail': snippet['thumbnails']['default']['url'],
                    'embed_url': f"https://www.youtube.com/embed/{item['id']['videoId']}"
                }
                videos.append(video_info)
        
        return videos
        
    except requests.exceptions.RequestException as e:
        logging.error(f"YouTube API request error: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"YouTube search error: {str(e)}")
        return []

def get_video_details(video_id):
    """
    Get detailed information about a specific YouTube video.
    """
    try:
        if not YOUTUBE_API_KEY:
            return None
        
        details_url = "https://www.googleapis.com/youtube/v3/videos"
        
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': video_id,
            'key': YOUTUBE_API_KEY
        }
        
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('items'):
            return None
        
        item = data['items'][0]
        snippet = item['snippet']
        content_details = item['contentDetails']
        statistics = item['statistics']
        
        return {
            'video_id': video_id,
            'title': snippet['title'],
            'description': snippet['description'],
            'channel_title': snippet['channelTitle'],
            'published_at': snippet['publishedAt'],
            'duration': content_details['duration'],
            'view_count': statistics.get('viewCount', 'N/A'),
            'like_count': statistics.get('likeCount', 'N/A'),
            'thumbnail': snippet['thumbnails']['default']['url'],
            'embed_url': f"https://www.youtube.com/embed/{video_id}"
        }
        
    except Exception as e:
        logging.error(f"Video details error: {str(e)}")
        return None

def validate_nde_video_content(video_info):
    """
    Validate that a video contains legitimate NDE educational content.
    """
    try:
        title = video_info.get('title', '').lower()
        description = video_info.get('description', '').lower()
        channel = video_info.get('channel_title', '').lower()
        
        # Professional/educational channel indicators
        professional_indicators = [
            'university', 'college', 'institute', 'training', 'education',
            'certification', 'asnt', 'asme', 'astm', 'aws', 'api',
            'technical', 'engineering', 'industrial', 'professional'
        ]
        
        # NDE technical content indicators
        technical_indicators = [
            'ultrasonic testing', 'radiographic testing', 'magnetic particle',
            'liquid penetrant', 'eddy current', 'visual inspection',
            'ndt level', 'certification', 'procedure', 'standard',
            'defect detection', 'flaw detection', 'inspection technique'
        ]
        
        has_professional = any(indicator in channel or indicator in title for indicator in professional_indicators)
        has_technical = any(indicator in title or indicator in description for indicator in technical_indicators)
        
        # Calculate relevance score
        relevance_score = 0
        if has_professional:
            relevance_score += 0.5
        if has_technical:
            relevance_score += 0.5
        
        return {
            'is_relevant': relevance_score >= 0.5,
            'relevance_score': relevance_score,
            'has_professional': has_professional,
            'has_technical': has_technical
        }
        
    except Exception as e:
        logging.error(f"Video validation error: {str(e)}")
        return {
            'is_relevant': False,
            'relevance_score': 0,
            'has_professional': False,
            'has_technical': False
        }
