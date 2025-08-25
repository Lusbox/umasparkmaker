import requests
from bs4 import BeautifulSoup
import json
import re
import os
from urllib.parse import urlparse
import time
from PIL import Image
import io

def extract_support_cards_from_html(html_content, filter_ssr_only=True):
    """Extract support card data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    cards = []
    
    # Find all span elements with typeof="mw:File"
    card_spans = soup.find_all('span', {'typeof': 'mw:File'})
    
    for span in card_spans:
        link = span.find('a')
        img = span.find('img')
        
        if link and img:
            # Extract card name from link title
            card_name = link.get('title', '')
            if card_name.startswith('Game:'):
                card_name = card_name[5:]  # Remove "Game:" prefix
            
            # Filter for SSR cards only if enabled
            if filter_ssr_only and 'SSR' not in card_name:
                continue
            
            # Extract image URL
            image_url = img.get('src', '')
            
            # Convert relative URL to absolute
            if image_url.startswith('/w/thumb.php'):
                image_url = 'https://umamusu.wiki' + image_url
            
            # Try to get higher resolution image from srcset
            srcset = img.get('srcset', '')
            if srcset:
                # Look for 2x version
                for entry in srcset.split(','):
                    entry = entry.strip()
                    if entry.endswith('2x'):
                        higher_res_url = entry.split(' ')[0]
                        if higher_res_url.startswith('/w/thumb.php'):
                            image_url = 'https://umamusu.wiki' + higher_res_url
                        break
            
            # Extract link URL
            link_url = link.get('href', '')
            if link_url.startswith('/'):
                link_url = 'https://umamusu.wiki' + link_url
            
            if card_name and image_url:
                card_data = {
                    'name': card_name.strip(),
                    'image': image_url,
                    'link': link_url
                }
                cards.append(card_data)
    
    return cards

def load_existing_data(json_file='support_cards.json'):
    """Load existing card data from JSON file"""
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading existing data: {e}")
            return []
    return []

def find_new_cards(current_cards, existing_cards):
    """Compare current cards with existing cards and return new ones"""
    # Create a set of existing card names for quick lookup
    existing_names = {card['name'] for card in existing_cards}
    
    # Find cards that don't exist in the existing data
    new_cards = []
    for card in current_cards:
        if card['name'] not in existing_names:
            new_cards.append(card)
    
    return new_cards

def merge_card_data(current_cards, existing_cards):
    """Merge current cards with existing cards, preserving local_image paths"""
    # Create a dictionary of existing cards for quick lookup
    existing_dict = {card['name']: card for card in existing_cards}
    
    merged_cards = []
    
    for card in current_cards:
        card_name = card['name']
        
        if card_name in existing_dict:
            # Card exists, preserve local_image if it exists
            merged_card = card.copy()
            if 'local_image' in existing_dict[card_name]:
                merged_card['local_image'] = existing_dict[card_name]['local_image']
            merged_cards.append(merged_card)
        else:
            # New card
            merged_cards.append(card)
    
    return merged_cards

def extract_from_url(url, filter_ssr_only=True):
    """Fetch and extract support cards from URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return extract_support_cards_from_html(response.text, filter_ssr_only)
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []

def extract_from_file(file_path, filter_ssr_only=True):
    """Extract support cards from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return extract_support_cards_from_html(html_content, filter_ssr_only)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def optimize_image(image_data, max_width=800, max_height=600, quality=85, format='WEBP'):
    """Optimize image for smaller file size while maintaining quality"""
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if saving as JPEG (JPEG doesn't support transparency)
        if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if image is larger than max dimensions (maintains aspect ratio)
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save optimized image to bytes
        output = io.BytesIO()
        
        if format == 'WEBP':
            img.save(output, format='WEBP', quality=quality, optimize=True)
        elif format == 'JPEG':
            img.save(output, format='JPEG', quality=quality, optimize=True)
        else:  # PNG
            img.save(output, format='PNG', optimize=True)
        
        return output.getvalue()
    
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return image_data  # Return original if optimization fails

def download_image(url, filename, download_dir='images', optimize=True, max_width=800, max_height=600, quality=85, output_format='WEBP'):
    """Download and optionally optimize an image from URL"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get original image data
        image_data = response.content
        
        if optimize:
            # Optimize the image
            optimized_data = optimize_image(image_data, max_width, max_height, quality, output_format)
            
            # Update filename extension based on output format
            base_name = os.path.splitext(filename)[0]
            if output_format == 'WEBP':
                filename = f"{base_name}.webp"
            elif output_format == 'JPEG':
                filename = f"{base_name}.jpg"
            else:  # PNG
                filename = f"{base_name}.png"
            
            final_data = optimized_data
            
            # Calculate size reduction
            original_size = len(image_data)
            optimized_size = len(optimized_data)
            reduction = ((original_size - optimized_size) / original_size) * 100
            
            print(f"Downloaded & optimized: {filename} ({original_size/1024:.1f}KB → {optimized_size/1024:.1f}KB, {reduction:.1f}% reduction)")
        else:
            final_data = image_data
            print(f"Downloaded: {filename}")
        
        # Save to file
        filepath = os.path.join(download_dir, filename)
        with open(filepath, 'wb') as file:
            file.write(final_data)
        
        return filepath
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove extra spaces and limit length
    filename = re.sub(r'\s+', ' ', filename).strip()
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename

def download_all_images(cards, download_dir='images', delay=0.5, start_index=1, optimize=True, max_width=800, max_height=600, quality=85, output_format='WEBP'):
    """Download all card images with optional optimization"""
    if not cards:
        print("No new images to download.")
        return
    
    optimization_text = f" with optimization ({output_format}, max:{max_width}x{max_height}, quality:{quality})" if optimize else ""
    print(f"Downloading {len(cards)} new images to '{download_dir}' directory{optimization_text}...")
    
    for i, card in enumerate(cards, start_index):
        try:
            # Create filename from card name
            safe_name = sanitize_filename(card['name'])
            
            # For optimized images, we'll set the extension in download_image function
            if optimize:
                filename = f"{i:03d}_{safe_name}"  # Extension will be added by download_image
            else:
                # Extract file extension from URL for non-optimized images
                parsed_url = urlparse(card['image'])
                ext = '.png'  # Default
                if 'f=' in parsed_url.query:
                    f_param = [param for param in parsed_url.query.split('&') if param.startswith('f=')]
                    if f_param:
                        original_filename = f_param[0].split('=')[1]
                        if '.' in original_filename:
                            ext = '.' + original_filename.split('.')[-1]
                filename = f"{i:03d}_{safe_name}{ext}"
            
            # Download the image
            local_path = download_image(
                card['image'], 
                filename, 
                download_dir, 
                optimize=optimize,
                max_width=max_width,
                max_height=max_height,
                quality=quality,
                output_format=output_format
            )
            
            # Update card data with local path
            if local_path:
                card['local_image'] = local_path
            
            # Be respectful to the server
            time.sleep(delay)
            
        except Exception as e:
            print(f"Error processing {card['name']}: {e}")
    
    print("Download complete!")

def save_to_json(cards, output_file='support_cards.json'):
    """Save extracted cards to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(cards, file, indent=2, ensure_ascii=False)
    print(f"Saved {len(cards)} cards to {output_file}")

def main():
    json_file = 'support_cards.json'
    
    # Ask user about filtering
    filter_choice = input("Filter for SSR cards only? (y/n) [y]: ").lower().strip()
    filter_ssr_only = filter_choice != 'n'  # Default to True unless explicitly 'n'
    
    filter_text = "SSR cards only" if filter_ssr_only else "all cards"
    print(f"Mode: {filter_text}")
    
    # Load existing data
    print("Loading existing data...")
    existing_cards = load_existing_data(json_file)
    print(f"Found {len(existing_cards)} existing cards")
    
    # Fetch current data from website
    print("Fetching current data from website...")
    url = "https://umamusu.wiki/Game:List_of_Support_Cards"
    current_cards = extract_from_url(url, filter_ssr_only)
    
    if not current_cards:
        print("Failed to fetch current data. Exiting.")
        return []
    
    print(f"Found {len(current_cards)} current {filter_text} on website")
    
    # Find new cards
    new_cards = find_new_cards(current_cards, existing_cards)
    print(f"Found {len(new_cards)} new cards to download")
    
    if new_cards:
        print(f"\nNew {filter_text} found:")
        for i, card in enumerate(new_cards, 1):
            print(f"{i}. {card['name']}")
        
        # Ask user if they want to download new images
        download_choice = input(f"\nDo you want to download {len(new_cards)} new images? (y/n): ").lower().strip()
        
        if download_choice in ['y', 'yes']:
            # Optional: customize download directory
            custom_dir = input("Enter download directory (press Enter for 'images'): ").strip()
            download_dir = custom_dir if custom_dir else 'images'
            
            # Image optimization options
            optimize_choice = input("Optimize images for smaller file size? (y/n): ").lower().strip()
            optimize = optimize_choice in ['y', 'yes']
            
            optimization_settings = {}
            if optimize:
                print("\nOptimization settings (press Enter for defaults):")
                
                # Output format
                format_choice = input("Output format (webp/jpeg/png) [webp]: ").lower().strip()
                output_format = format_choice.upper() if format_choice in ['webp', 'jpeg', 'png'] else 'WEBP'
                
                # Max dimensions
                max_width = input("Maximum width in pixels [800]: ").strip()
                max_width = int(max_width) if max_width.isdigit() else 800
                
                max_height = input("Maximum height in pixels [600]: ").strip()
                max_height = int(max_height) if max_height.isdigit() else 600
                
                # Quality (for WEBP and JPEG)
                if output_format in ['WEBP', 'JPEG']:
                    quality = input("Quality (1-100) [85]: ").strip()
                    quality = int(quality) if quality.isdigit() and 1 <= int(quality) <= 100 else 85
                else:
                    quality = 85  # Not used for PNG
                
                optimization_settings = {
                    'optimize': optimize,
                    'max_width': max_width,
                    'max_height': max_height,
                    'quality': quality,
                    'output_format': output_format
                }
                
                print(f"\nOptimization: {output_format}, max {max_width}x{max_height}, quality {quality}")
            
            # Calculate starting index for new files
            start_index = len(existing_cards) + 1
            
            # Download only new images
            download_all_images(new_cards, download_dir, start_index=start_index, **optimization_settings)
    else:
        print(f"No new {filter_text} to download. All images are up to date!")
    
    # Merge current data with existing data (preserving local_image paths)
    merged_cards = merge_card_data(current_cards, existing_cards)
    
    # Save updated data to JSON file
    save_to_json(merged_cards, json_file)
    
    print(f"\nSummary:")
    print(f"Total cards: {len(merged_cards)}")
    print(f"New cards added: {len(new_cards)}")
    print(f"Cards with local images: {len([c for c in merged_cards if 'local_image' in c])}")
    print(f"Filter mode: {filter_text}")
    
    return merged_cards

if __name__ == "__main__":
    main()