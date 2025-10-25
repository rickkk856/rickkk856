import os
import requests
from datetime import datetime
import json
import textwrap

# --- Configuration ---
GOOGLE_AI_STUDIO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Static Profile Info ---
RICARDO_NAME = "Ricardo"
RICARDO_LOCATION = "São Paulo, SP, Brazil"

# --- SVG Constants ---
SVG_WIDTH = 500
SVG_HEIGHT_PER_LINE = 30 # Approx height per line of text
SVG_MAX_BUBBLE_WIDTH = 450
SVG_PADDING_X = 20
SVG_PADDING_Y = 15
FONT_SIZE = 16
TEXT_COLOR = "#FFFFFF"
BUBBLE_COLOR = "#333333"
BUBBLE_RADIUS = 10
LINE_HEIGHT_FACTOR = 1.4 # Factor for multi-line text
ANIMATION_DURATION = "0.6s"
ANIMATION_DELAY_INCREMENT = "0.7s" # Delay between bubbles

def get_ai_quote():
    """Fetches a short quote about Generative AI from Google AI Studio."""
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return "AI is constantly evolving, bringing new possibilities."

    headers = {
        "Content-Type": "application/json"
    }
    prompt = "Generate a very short, interesting, and recent update or fact about Generative AI. Keep it to 1-3 sentences, maximum 25 words, no conversational filler like 'Did you know that:'."
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    params = {
        "key": GOOGLE_API_KEY
    }

    try:
        response = requests.post(GOOGLE_AI_STUDIO_API_URL, headers=headers, json=data, params=params, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        response_data = response.json()
        
        # Extracting the text, handling potential variations in response structure
        if 'candidates' in response_data and response_data['candidates']:
            first_candidate = response_data['candidates'][0]
            if 'content' in first_candidate and 'parts' in first_candidate['content']:
                for part in first_candidate['content']['parts']:
                    if 'text' in part:
                        return part['text'].strip()
        
        print(f"Warning: Could not extract AI quote from response: {response_data}")
        return "Generative AI continues to push creative boundaries."

    except requests.exceptions.RequestException as e:
        print(f"Error calling Google AI Studio API: {e}")
        return "AI advancements are accelerating innovation globally."
    except Exception as e:
        print(f"An unexpected error occurred during AI quote retrieval: {e}")
        return "AI is a fascinating field with continuous breakthroughs."

def wrap_text(text, max_width, font_size):
    """Wraps text to fit within a given SVG width, estimating character count."""
    # This is an approximation. A more precise method would involve measuring rendered text.
    # For a fixed-width font, char_width = font_size * 0.6 (approx). For variable, it's harder.
    # We'll use a conservative estimate for typical sans-serif fonts.
    chars_per_line = int(max_width / (font_size * 0.6)) # Rough estimate
    wrapped_lines = textwrap.wrap(text, width=chars_per_line)
    return wrapped_lines

def generate_svg_chat(ai_quote):
    """Generates the animated chat-bubble-like SVG."""
    
    current_day = datetime.now().strftime("%A")

    messages = [
        f"Hi, I'm {RICARDO_NAME}.",
        f"I'm located at {RICARDO_LOCATION}.",
        f"Did you know that: {ai_quote}",
        f"Thanks for stopping by and have a nice {current_day}!",
    ]

    svg_content = f'''
<svg width="{SVG_WIDTH}" viewBox="0 0 {SVG_WIDTH} 1" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bubble-bg {{ fill: {BUBBLE_COLOR}; rx: {BUBBLE_RADIUS}px; ry: {BUBBLE_RADIUS}px; }}
    .bubble-text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji"; font-size: {FONT_SIZE}px; fill: {TEXT_COLOR}; }}
  </style>
'''
    current_y = SVG_PADDING_Y
    total_height = 0
    animation_begin_time = 0.0

    for i, message in enumerate(messages):
        wrapped_lines = wrap_text(message, SVG_MAX_BUBBLE_WIDTH - (SVG_PADDING_X * 2), FONT_SIZE)
        
        # Calculate bubble height based on wrapped lines
        bubble_height = (len(wrapped_lines) * FONT_SIZE * LINE_HEIGHT_FACTOR) + (SVG_PADDING_Y * 2)
        
        # Ensure minimum height for single line messages
        if len(wrapped_lines) == 1:
            bubble_height = max(bubble_height, SVG_HEIGHT_PER_LINE + (SVG_PADDING_Y * 2))

        # We'll make all bubbles the same max width for simplicity and alignment
        bubble_width = SVG_MAX_BUBBLE_WIDTH
        
        svg_content += f'''
  <rect x="{SVG_PADDING_X}" y="{current_y}" width="{bubble_width}" height="{bubble_height}" class="bubble-bg">
    <animate attributeName="opacity" from="0" to="1" dur="{ANIMATION_DURATION}" begin="{animation_begin_time}s" fill="freeze"/>
  </rect>
'''
        text_y = current_y + SVG_PADDING_Y + FONT_SIZE # Start text just below bubble top padding
        for line_idx, line in enumerate(wrapped_lines):
            svg_content += f'''
  <text x="{SVG_PADDING_X * 2}" y="{text_y + (line_idx * FONT_SIZE * LINE_HEIGHT_FACTOR)}" class="bubble-text">
    <tspan> {line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')} </tspan>
    <animate attributeName="opacity" from="0" to="1" dur="{ANIMATION_DURATION}" begin="{animation_begin_time}s" fill="freeze"/>
  </text>
'''
        current_y += bubble_height + SVG_PADDING_Y # Space between bubbles
        total_height = current_y
        animation_begin_time += float(ANIMATION_DELAY_INCREMENT.replace('s','')) # Increment delay for next bubble

    # Adjust overall SVG height based on total content
    final_height = total_height + SVG_PADDING_Y # Add final padding
    svg_content = svg_content.replace('viewBox="0 0 500 1"', f'viewBox="0 0 {SVG_WIDTH} {final_height}" height="{final_height}"')

    svg_content += '''
</svg>
'''
    return svg_content

def update_readme(svg_filename):
    """Updates the readme.md file with the new SVG."""
    readme_path = "readme.md"
    
    # Ensure a readme.md exists, create if not
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write("# rickkk856's Profile\n\n")
            f.write("<!-- GENERATED_SVG_START -->\n")
            f.write("<!-- GENERATED_SVG_END -->\n\n")
            f.write("A dynamic space showcasing my work and current thoughts!\n")

    with open(readme_path, 'r') as f:
        readme_content = f.read()

    # Define markers for the SVG block
    start_marker = "<!-- GENERATED_SVG_START -->"
    end_marker = "<!-- GENERATED_SVG_END -->"

    # Create the new SVG embed markdown
    new_svg_markdown = f"{start_marker}\n![Dynamic Profile Card]({svg_filename})\n{end_marker}"

    # Find and replace the old SVG block
    if start_marker in readme_content and end_marker in readme_content:
        pre_svg = readme_content.split(start_marker)[0]
        post_svg = readme_content.split(end_marker)[1]
        updated_readme_content = f"{pre_svg}{new_svg_markdown}{post_svg}"
    else:
        # If markers are not found, append/insert at a sensible place
        print("Warning: SVG markers not found in readme.md. Appending SVG to the end.")
        updated_readme_content = f"{readme_content}\n\n{new_svg_markdown}"

    with open(readme_path, 'w') as f:
        f.write(updated_readme_content)
    print("readme.md updated successfully.")

if __name__ == "__main__":
    print("Starting content generation...")
    ai_quote = get_ai_quote()
    print(f"Fetched AI Quote: {ai_quote}")

    svg_content = generate_svg_chat(ai_quote)
    svg_filename = "rickkk856.svg" # Name of your SVG file
    with open(svg_filename, 'w') as f:
        f.write(svg_content)
    print(f"{svg_filename} generated successfully.")

    update_readme(svg_filename)
    print("Content generation complete.")