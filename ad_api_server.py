"""
BriteCo Ad Generator API Server
Provides AI-powered endpoints for ad generation
Uses same proven architecture as venue-newsletter-tool
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add venue-newsletter-tool backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'venue-newsletter-tool', 'backend'))

from integrations.openai_client import OpenAIClient
from integrations.gemini_client import GeminiClient
from integrations.claude_client import ClaudeClient

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize AI clients
openai_client = OpenAIClient()
gemini_client = GeminiClient()
claude_client = ClaudeClient()

print("[OK] OpenAI initialized")
print("[OK] Gemini initialized")
print("[OK] Claude initialized")

# BriteCo brand guidelines
BRAND_GUIDELINES = """
BriteCo Brand Guidelines:
- Colors: Turquoise (#31D7CA), Navy (#272D3F), Orange (#FC883A)
- Style: Modern, clean, optimistic, trustworthy
- Target: Millennials and Gen Z engaged couples
- Photography: Warm lighting, diverse couples, genuine moments
- No gradients - solid colors only
- Gilroy font family

Requirements for ads:
- Show happy couple with engagement ring or jewelry
- Warm, natural lighting
- Modern, clean aesthetic
- Include turquoise color accent somewhere
- Professional photography quality
- Authentic, candid moment (not too posed)
- Diverse representation
"""

# Platform specifications
PLATFORM_SIZES = {
    'meta': [
        {'name': 'Square Feed', 'width': 1080, 'height': 1080},
        {'name': 'Portrait Story', 'width': 1080, 'height': 1920},
        {'name': 'Landscape', 'width': 1200, 'height': 1200}
    ],
    'reddit': [
        {'name': 'Feed', 'width': 1200, 'height': 628},
        {'name': 'Square', 'width': 960, 'height': 960}
    ],
    'pinterest': [
        {'name': 'Standard Pin', 'width': 1000, 'height': 1500},
        {'name': 'Square', 'width': 1000, 'height': 1000}
    ]
}

@app.route('/')
def serve_index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/logo file for claude.jpg')
def serve_logo():
    """Serve the logo file"""
    return send_from_directory('.', 'logo file for claude.jpg')

@app.route('/logos/<filename>')
def serve_logo_file(filename):
    """Serve logo files dynamically"""
    return send_from_directory('.', filename)

@app.route('/api/generate-prompt', methods=['POST'])
def generate_prompt():
    """Generate image prompt using Claude or OpenAI"""
    try:
        data = request.json
        campaign_text = data.get('campaignText', '')
        platforms = data.get('platforms', [])
        provider = data.get('provider', 'claude')

        print(f"\n[API] Generate Prompt Request")
        print(f"  Provider: {provider}")
        print(f"  Platforms: {platforms}")

        prompt_context = f"""You are an expert at creating image generation prompts for AI models.

Create an image generation prompt for BriteCo jewelry insurance ads for {', '.join(platforms)}.

Campaign context: {campaign_text}

{BRAND_GUIDELINES}

Generate ONE detailed, creative prompt (200 words max) for Nano Banana (Google Gemini) image generator. Make it specific, visual, and actionable."""

        # Use selected provider
        if provider == 'claude':
            print("[API] Using Claude...")
            result = claude_client.generate_content(
                prompt=prompt_context,
                max_tokens=500,
                temperature=0.7
            )
            prompt = result.get('content', '')
        else:
            print("[API] Using OpenAI...")
            result = openai_client.generate_content(
                prompt=prompt_context,
                max_tokens=500,
                temperature=0.7
            )
            prompt = result.get('content', '')

        print(f"[API] Prompt generated successfully ({len(prompt)} chars)")

        return jsonify({
            'success': True,
            'prompt': prompt,
            'provider': provider
        })

    except Exception as e:
        print(f"[API ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-images', methods=['POST'])
def generate_images():
    """Generate images using Gemini (Nano Banana) - 2 variations per size"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        platforms = data.get('platforms', [])

        print(f"\n[API] Generate Images Request")
        print(f"  Platforms: {platforms}")
        print(f"  Prompt: {prompt[:100]}...")
        print(f"  Generating 2 variations per size")

        images = []

        for platform in platforms:
            platform_lower = platform.lower()
            sizes = PLATFORM_SIZES.get(platform_lower, PLATFORM_SIZES['meta'])

            for size in sizes:
                # Generate 2 variations for each size
                for variation_num in range(1, 3):  # 1, 2
                    try:
                        print(f"[API] Generating {platform} - {size['name']} - Variation {variation_num}...")

                        # Calculate aspect ratio for this size
                        width = size['width']
                        height = size['height']
                        aspect_ratio = width / height

                        # Determine aspect ratio string for Gemini prompt enhancement
                        if aspect_ratio > 1.5:
                            aspect_hint = "wide landscape format (16:9 or wider)"
                            composition_hint = "horizontal composition with subjects positioned to fill the wide frame"
                        elif aspect_ratio > 1.2:
                            aspect_hint = "landscape format"
                            composition_hint = "horizontal composition"
                        elif aspect_ratio > 0.85:
                            aspect_hint = "square format (1:1)"
                            composition_hint = "centered composition with subjects filling the square frame"
                        elif aspect_ratio > 0.6:
                            aspect_hint = "portrait format (4:5)"
                            composition_hint = "vertical composition with more headroom"
                        else:
                            aspect_hint = "tall portrait format (9:16 story)"
                            composition_hint = "full vertical composition from head to below waist, story-style framing"

                        # Enhance prompt with aspect ratio guidance
                        enhanced_prompt = f"{prompt}\n\nIMPORTANT: Compose this image specifically for {aspect_hint}. Use {composition_hint}. Frame: {width}x{height}px.\n\nDo NOT include any company logos, brand marks, watermarks, or text overlays in the image. Generate photography only without any branding elements."

                        # Generate with Gemini (Nano Banana) with aspect-specific prompt
                        result = gemini_client.generate_image(
                            prompt=enhanced_prompt,
                            model="gemini-2.5-flash-image"
                        )

                        image_data = result.get('image_data', '')

                        if image_data:
                            # Resize and compress image to reduce size
                            try:
                                import base64
                                from PIL import Image, ImageOps
                                from io import BytesIO

                                # Decode base64 to PIL Image
                                image_bytes = base64.b64decode(image_data)
                                pil_image = Image.open(BytesIO(image_bytes))

                                print(f"[API] Original image: {pil_image.size}")

                                # Use ImageOps.fit to crop/resize maintaining aspect ratio with centering
                                target_width = size['width']
                                target_height = size['height']
                                pil_image = ImageOps.fit(pil_image, (target_width, target_height), Image.Resampling.LANCZOS, centering=(0.5, 0.5))

                                # Convert to JPEG with compression to reduce size
                                buffer = BytesIO()
                                pil_image.convert('RGB').save(buffer, format='JPEG', quality=85, optimize=True)
                                compressed_bytes = buffer.getvalue()
                                image_data = base64.b64encode(compressed_bytes).decode('utf-8')

                                print(f"[API] Final: {pil_image.size}, compressed from {len(image_bytes)} to {len(compressed_bytes)} bytes")
                            except Exception as resize_error:
                                print(f"[API] WARNING - Resize failed, using original: {resize_error}")

                            images.append({
                                'platform': platform,
                                'size': f"{size['name']} - Variation {variation_num}",
                                'width': size['width'],
                                'height': size['height'],
                                'url': f"data:image/jpeg;base64,{image_data}"
                            })
                            print(f"[API] SUCCESS - {platform} {size['name']} - Variation {variation_num}")
                        else:
                            print(f"[API] WARNING - No image data for {platform} {size['name']} - Variation {variation_num}")

                    except Exception as img_error:
                        print(f"[API ERROR] Failed to generate {platform} {size['name']} - Variation {variation_num}: {img_error}")

        print(f"[API] Generated {len(images)} images total")

        return jsonify({
            'success': True,
            'images': images,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"[API ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-ad-copy', methods=['POST'])
def generate_ad_copy():
    """Generate platform-specific ad copy using Claude or OpenAI"""
    try:
        data = request.json
        platform = data.get('platform', '').lower()
        size_name = data.get('sizeName', '')
        campaign_text = data.get('campaignText', '')
        text_overlay = data.get('textOverlay', '')
        provider = data.get('provider', 'claude')

        print(f"\n[API] Generate Ad Copy Request")
        print(f"  Platform: {platform}, Size: {size_name}")
        print(f"  Provider: {provider}")

        # Platform-specific specs
        platform_specs = {
            'meta': {
                'headline_limit': 27,
                'primary_text_visible': 125,
                'description_limit': 27,
                'best_practices': 'Front-load value proposition in first 30 characters. Use emojis sparingly.'
            },
            'reddit': {
                'headline_limit': 300,
                'body_limit': 500,
                'best_practices': 'Be authentic and conversational. Redditors value transparency and community.'
            },
            'pinterest': {
                'title_limit': 100,
                'title_visible': 40,
                'description_limit': 500,
                'best_practices': 'Focus on aspirational, visual language. Pinterest is about inspiration and discovery.'
            }
        }

        specs = platform_specs.get(platform, platform_specs['meta'])

        # Build prompt based on platform
        if platform == 'meta':
            prompt_context = f"""You are an expert social media copywriter for BriteCo jewelry insurance.

Generate ad copy for a {platform.upper()} ad campaign.

Campaign context: {campaign_text}
Text overlay on image: "{text_overlay}"
Ad size: {size_name}

Platform specifications for {platform.upper()}:
{', '.join([f'{k}: {v}' for k, v in specs.items()])}

BriteCo Brand Voice:
- Modern, trustworthy, optimistic
- Target: Millennials and Gen Z engaged couples
- Focus on peace of mind and protecting what matters
- Turquoise (#31D7CA), Navy (#272D3F), Orange (#FC883A) brand colors

Generate:
1. Headline (stay within 27 characters)
2. Primary text (engaging, benefit-focused, first 125 chars are most visible)
3. Description (stay within 27 characters, appears below primary text)
4. Call-to-action suggestion

Return as JSON:
{{
  "headline": "...",
  "body": "...",
  "description": "...",
  "cta": "..."
}}

Return ONLY the JSON, no other text."""
        else:
            prompt_context = f"""You are an expert social media copywriter for BriteCo jewelry insurance.

Generate ad copy for a {platform.upper()} ad campaign.

Campaign context: {campaign_text}
Text overlay on image: "{text_overlay}"
Ad size: {size_name}

Platform specifications for {platform.upper()}:
{', '.join([f'{k}: {v}' for k, v in specs.items()])}

BriteCo Brand Voice:
- Modern, trustworthy, optimistic
- Target: Millennials and Gen Z engaged couples
- Focus on peace of mind and protecting what matters
- Turquoise (#31D7CA), Navy (#272D3F), Orange (#FC883A) brand colors

Generate:
1. Headline (stay within character limits)
2. Primary text/body copy (engaging, benefit-focused)
3. Call-to-action suggestion

Return as JSON:
{{
  "headline": "...",
  "body": "...",
  "cta": "..."
}}

Return ONLY the JSON, no other text."""

        # Use selected provider
        if provider == 'claude':
            print("[API] Using Claude...")
            result = claude_client.generate_content(
                prompt=prompt_context,
                max_tokens=500,
                temperature=0.7
            )
            copy_text = result.get('content', '')
        else:
            print("[API] Using OpenAI...")
            result = openai_client.generate_content(
                prompt=prompt_context,
                max_tokens=500,
                temperature=0.7
            )
            copy_text = result.get('content', '')

        # Parse JSON from response
        import json
        import re

        # Remove markdown code blocks if present
        copy_text = re.sub(r'```json\s*', '', copy_text)
        copy_text = re.sub(r'```\s*', '', copy_text)
        copy_text = copy_text.strip()

        try:
            ad_copy = json.loads(copy_text)
        except:
            # If JSON parsing fails, create default structure
            ad_copy = {
                'headline': copy_text[:100],
                'body': 'Protect what matters most with BriteCo jewelry insurance.',
                'cta': 'Get Protected'
            }

        print(f"[API] Ad copy generated successfully")

        return jsonify({
            'success': True,
            'adCopy': ad_copy,
            'provider': provider
        })

    except Exception as e:
        print(f"[API ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-animation', methods=['POST'])
def generate_animation():
    """Generate animated GIF from multiple image variations"""
    try:
        data = request.json
        base_prompt = data.get('prompt', '')
        width = data.get('width', 1080)
        height = data.get('height', 1080)
        duration_seconds = data.get('duration', 5)
        platform = data.get('platform', 'Meta')
        size_name = data.get('sizeName', 'Square')

        print(f"\n[API] Generate Animation Request")
        print(f"  Platform: {platform}, Size: {size_name}")
        print(f"  Duration: {duration_seconds} seconds")
        print(f"  Dimensions: {width}x{height}")

        # Generate 5 frames with slight variations
        frame_count = min(duration_seconds, 5)  # Max 5 frames
        frames = []

        # Define prompt variations for animation effect
        variations = [
            "",  # Original
            "Zoom in slightly to show more detail on the jewelry",
            "Pan slightly to the right to show the couple's connection",
            "Zoom out slightly for a wider view",
            "Return to original composition"
        ]

        for i in range(frame_count):
            try:
                variation_prompt = variations[i] if i < len(variations) else ""
                enhanced_prompt = f"{base_prompt}\n\n{variation_prompt}".strip()

                print(f"[API] Generating frame {i+1}/{frame_count}...")

                # Calculate aspect ratio hints
                aspect_ratio = width / height
                if aspect_ratio > 1.5:
                    aspect_hint = "wide landscape format (16:9 or wider)"
                    composition_hint = "horizontal composition with subjects positioned to fill the wide frame"
                elif aspect_ratio > 1.2:
                    aspect_hint = "landscape format"
                    composition_hint = "horizontal composition"
                elif aspect_ratio > 0.85:
                    aspect_hint = "square format (1:1)"
                    composition_hint = "centered composition with subjects filling the square frame"
                elif aspect_ratio > 0.6:
                    aspect_hint = "portrait format (4:5)"
                    composition_hint = "vertical composition with more headroom"
                else:
                    aspect_hint = "tall portrait format (9:16 story)"
                    composition_hint = "full vertical composition from head to below waist, story-style framing"

                enhanced_prompt += f"\n\nIMPORTANT: Compose this image specifically for {aspect_hint}. Use {composition_hint}. Frame: {width}x{height}px.\n\nDo NOT include any company logos, brand marks, watermarks, or text overlays in the image. Generate photography only without any branding elements."

                # Generate frame with Gemini
                result = gemini_client.generate_image(
                    prompt=enhanced_prompt,
                    model="gemini-2.5-flash-image"
                )

                image_data = result.get('image_data', '')

                if image_data:
                    import base64
                    from PIL import Image, ImageOps
                    from io import BytesIO

                    # Decode and resize frame
                    image_bytes = base64.b64decode(image_data)
                    pil_image = Image.open(BytesIO(image_bytes))

                    # Resize to exact dimensions
                    pil_image = ImageOps.fit(pil_image, (width, height), Image.Resampling.LANCZOS, centering=(0.5, 0.5))

                    frames.append(pil_image.convert('RGB'))
                    print(f"[API] Frame {i+1} generated successfully")

            except Exception as frame_error:
                print(f"[API ERROR] Failed to generate frame {i+1}: {frame_error}")

        if len(frames) == 0:
            return jsonify({'success': False, 'error': 'No frames generated'}), 500

        print(f"[API] Creating GIF from {len(frames)} frames...")

        # Create animated GIF
        from io import BytesIO
        import base64

        # Convert frames to base64 for individual editing
        frame_images = []
        for i, frame in enumerate(frames):
            frame_buffer = BytesIO()
            frame.save(frame_buffer, format='PNG')
            frame_base64 = base64.b64encode(frame_buffer.getvalue()).decode('utf-8')
            frame_images.append(f"data:image/png;base64,{frame_base64}")

        gif_buffer = BytesIO()

        # Calculate duration per frame in milliseconds
        duration_ms = int((duration_seconds * 1000) / len(frames))

        # Save as animated GIF
        frames[0].save(
            gif_buffer,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,  # Infinite loop
            optimize=True
        )

        gif_data = base64.b64encode(gif_buffer.getvalue()).decode('utf-8')

        print(f"[API] Animation created successfully ({len(gif_buffer.getvalue())} bytes)")

        return jsonify({
            'success': True,
            'animation': f"data:image/gif;base64,{gif_data}",
            'frames': frame_images,  # Individual frames for editing
            'frame_count': len(frames),
            'duration': duration_seconds
        })

    except Exception as e:
        print(f"[API ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 80)
    print("BriteCo Ad Generator - Python API Server")
    print("=" * 80)
    print(f"\nStarting server...")
    print(f"URL: http://localhost:3000")
    print(f"\nAPIs:")
    print(f"  [OK] Claude (claude-sonnet-4-5-20250929)")
    print(f"  [OK] OpenAI (gpt-4o)")
    print(f"  [OK] Google Gemini (gemini-2.5-flash-image / Nano Banana)")
    print(f"\nPress Ctrl+C to stop")
    print("=" * 80)
    print()

    app.run(debug=True, port=3000, host='0.0.0.0')
