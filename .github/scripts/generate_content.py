import os
import requests
from datetime import datetime
import json
import textwrap

# --- Configuration ---
GOOGLE_AI_STUDIO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
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
    # This is an approximation. For a fixed-width font, char_width = font_size * 0.6 (approx).
    # For variable width fonts, it's more complex, but this gives a reasonable estimate.
    chars_per_line = int(max_width / (font_size * 0.6)) 
    wrapped_lines = textwrap.wrap(text, width=chars_per_line)
    return wrapped_lines

def generate_chat_html(ai_quote):
    """Generates GitHub-compatible HTML chat interface."""
    
    current_day = datetime.now().strftime("%A")

    messages = [
        f"👋 Hi, I'm {RICARDO_NAME}!",
        f"📍 I'm located at {RICARDO_LOCATION}",
        f"💡 {ai_quote}",
        f"🙏 Thanks for stopping by and have a nice {current_day}!",
    ]

    html_content = '''
<div align="center">
  <table>
    <tr>
      <td>
'''
    
    for message in messages:
        html_content += f'''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 20px; margin: 8px 0; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); max-width: 400px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 1.4;">
          {message}
        </div>
'''
    
    html_content += '''
      </td>
    </tr>
  </table>
</div>
'''
    return html_content

def update_readme(html_content): # Changed to accept html_content directly
    """Updates the README.md file with the new embedded HTML."""
    readme_path = "README.md"
    
    # Ensure a readme.md exists, create if not
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write("# rickkk856's Profile\n\n")
            f.write("<!-- GENERATED_CONTENT_START -->\n")
            f.write("<!-- GENERATED_CONTENT_END -->\n\n")
            f.write("A dynamic space showcasing my work and current thoughts!\n")

    with open(readme_path, 'r') as f:
        readme_content = f.read()

    # Define markers for the content block
    start_marker = "<!-- GENERATED_CONTENT_START -->"
    end_marker = "<!-- GENERATED_CONTENT_END -->"

    # Create the new embedded HTML markdown
    new_content_block = f"{start_marker}\n\n{html_content}\n\n{end_marker}"

    # Find and replace the old content block
    if start_marker in readme_content and end_marker in readme_content:
        pre_content = readme_content.split(start_marker)[0]
        post_content = readme_content.split(end_marker)[1]
        updated_readme_content = f"{pre_content}{new_content_block}{post_content}"
    else:
        # If markers are not found, append/insert at a sensible place
        print("Warning: Content markers not found in readme.md. Appending content to the end.")
        updated_readme_content = f"{readme_content}\n\n{new_content_block}"

    with open(readme_path, 'w') as f:
        f.write(updated_readme_content)
    print("README.md updated successfully with embedded HTML.")

if __name__ == "__main__":
    print("Starting content generation...")
    ai_quote = get_ai_quote()
    print(f"Fetched AI Quote: {ai_quote}")

    html_content = generate_chat_html(ai_quote)
    # We no longer need to save it as a separate file, just update readme
    # svg_filename = "rickkk856.svg"
    # with open(svg_filename, 'w') as f:
    #     f.write(svg_content)
    # print(f"{svg_filename} generated successfully.")

    update_readme(html_content) # Pass the HTML content directly
    print("Content generation complete.")