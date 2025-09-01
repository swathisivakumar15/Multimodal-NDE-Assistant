import trafilatura
import logging
from openai_service import summarize_nde_content, chat_with_nde_assistant

def get_website_text_content(url: str) -> str | None:
    """
    Extract main text content from a website using trafilatura.
    The text content is optimized for NDE technical analysis.
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        
        text = trafilatura.extract(downloaded)
        return text
    except Exception as e:
        logging.error(f"Web scraping error for {url}: {str(e)}")
        return None

def scrape_nde_content(url: str) -> dict:
    """
    Scrape NDE-related content from a website and process it for technical analysis.
    """
    try:
        # Validate URL is likely to contain NDE content
        nde_keywords = [
            'nde', 'ndt', 'non-destructive', 'nondestructive', 'ultrasonic', 
            'radiographic', 'magnetic particle', 'penetrant', 'eddy current',
            'inspection', 'testing', 'asme', 'astm', 'api', 'aws'
        ]
        
        url_lower = url.lower()
        has_nde_keywords = any(keyword in url_lower for keyword in nde_keywords)
        
        # Extract content
        raw_content = get_website_text_content(url)
        
        if not raw_content:
            return {
                'status': 'error',
                'message': 'Unable to extract content from the provided URL. The site may be inaccessible or have content restrictions.'
            }
        
        # Check if content is too short to be meaningful
        if len(raw_content.strip()) < 100:
            return {
                'status': 'error',
                'message': 'The extracted content is too short to provide meaningful analysis.'
            }
        
        # Summarize and analyze the content with NDE focus
        if has_nde_keywords or any(keyword in raw_content.lower() for keyword in nde_keywords):
            # Process as NDE content
            summary = summarize_nde_content(raw_content[:4000])  # Limit content length
            processed_content = f"**NDE Technical Content Summary:**\n\n{summary}\n\n**Source:** {url}"
        else:
            # General content processing with NDE context
            processed_content = chat_with_nde_assistant(
                f"Please analyze this web content from an NDE perspective and extract any relevant technical information:\n\n{raw_content[:3000]}"
            )
        
        return {
            'status': 'success',
            'content': processed_content,
            'source_url': url,
            'content_length': len(raw_content)
        }
        
    except Exception as e:
        logging.error(f"NDE content scraping error: {str(e)}")
        return {
            'status': 'error',
            'message': f'Failed to process content from the URL: {str(e)}'
        }

def scrape_multiple_sources(urls: list) -> dict:
    """
    Scrape content from multiple NDE-related sources and combine the analysis.
    """
    try:
        results = []
        successful_scrapes = 0
        
        for url in urls:
            result = scrape_nde_content(url)
            results.append(result)
            if result['status'] == 'success':
                successful_scrapes += 1
        
        if successful_scrapes == 0:
            return {
                'status': 'error',
                'message': 'Unable to successfully scrape content from any of the provided URLs.'
            }
        
        # Combine successful results
        combined_content = []
        for i, result in enumerate(results):
            if result['status'] == 'success':
                combined_content.append(f"**Source {i+1}:** {result['content']}")
        
        final_content = "\n\n---\n\n".join(combined_content)
        
        return {
            'status': 'success',
            'content': final_content,
            'sources_processed': len(urls),
            'successful_scrapes': successful_scrapes
        }
        
    except Exception as e:
        logging.error(f"Multiple source scraping error: {str(e)}")
        return {
            'status': 'error',
            'message': f'Failed to process multiple sources: {str(e)}'
        }
