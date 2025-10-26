import os
import requests
from datetime import datetime
from urllib.parse import quote as url_quote
import textwrap

# --- Configuration ---
GOOGLE_AI_STUDIO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Static Profile Info ---
RICARDO_NAME = "Ricardo"
RICARDO_LOCATION = "São Paulo, SP, Brazil"

def get_ai_quote():
    """Fetches a short quote about Generative AI from Google AI Studio."""
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return "AI is constantly evolving, bringing new possibilities."

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GOOGLE_API_KEY
    }

    current_day = datetime.now().strftime("%A")   

    prompt = f"Hi, Today is {current_day}. Please generate a very short, interesting, and recent update or fact about Generative AI. Keep it to 4-6 sentences, no conversational filler."
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(GOOGLE_AI_STUDIO_API_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        response_data = response.json()
        
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
        print(f"An unexpected error occurred: {e}")
        return "AI is a fascinating field with continuous breakthroughs."

def generate_profile_html(ai_quote):
    """Generates beautiful, animated HTML for GitHub profile."""
    
    current_day = datetime.now().strftime("%A")
    current_time = datetime.now().strftime("%H:%M UTC")
    last_updated = datetime.now().strftime("%B %d, %Y at %H:%M UTC")
    
    # Pre-process strings
    location_encoded = RICARDO_LOCATION.replace(' ', '%20').replace(',', '%2C')
    
    # Wrap quote into multiple lines (max 60 chars per line)
    wrapped_lines = textwrap.wrap(ai_quote, width=60)
    
    # Join lines with semicolon for the typing SVG service and URL encode
    quote_multiline = ';'.join(wrapped_lines)
    quote_encoded = url_quote(quote_multiline)
    
    # Calculate height based on number of lines (30px per line + padding)
    quote_height = max(100, len(wrapped_lines) * 25 + 10)
    
    # Build HTML using string concatenation
    html_parts = []
    
    html_parts.append('<div align="center">')
    html_parts.append('')
    html_parts.append('<!-- Profile Header with Gradient Animation -->')
    html_parts.append('<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=180&section=header&text=Ricardo%20Rodrigues&fontSize=42&fontColor=fff&animation=twinkling&fontAlignY=32"/>')
    html_parts.append('')
    html_parts.append('<!-- Animated Typing Effect -->')
    html_parts.append('<p align="center">')
    html_parts.append('  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=A78BFA&center=true&vCenter=true&multiline=false&repeat=true&width=600&lines=AI+Engineer+%7C+Data+Scientist;MSc+Architectural+Design+%2B+AI;5%2B+Years+Training+AI+Models" alt="Typing SVG" />')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('<!-- Dynamic Status Cards with Modern Design -->')
    html_parts.append('<table align="center">')
    html_parts.append('  <tr>')
    html_parts.append(f'    <td align="center" style="padding: 0;">')
    html_parts.append(f'      <img src="https://img.shields.io/badge/🌍_Location-{location_encoded}-667eea?style=for-the-badge&labelColor=1a1b27" alt="Location"/>')
    html_parts.append('    </td>')
    html_parts.append(f'    <td align="center" style="padding: 0;">')
    html_parts.append(f'      <img src="https://img.shields.io/badge/📅_Today-{current_day}-764ba2?style=for-the-badge&labelColor=1a1b27" alt="Day"/>')
    html_parts.append('    </td>')
    html_parts.append('  </tr>')
    html_parts.append('</table>')
    html_parts.append('')
    html_parts.append('<!-- AI-Generated Insight with Typing Animation -->')
    html_parts.append('<br/>')
    html_parts.append('')
    html_parts.append('<div align="center">')
    html_parts.append('  <img src="https://capsule-render.vercel.app/api?type=speech&color=gradient&customColorList=12,14,18&height=50&section=header&text=💡%20AI%20INSIGHT%20OF%20THE%20DAY&fontSize=20&fontColor=fff&fontAlignY=30" width="650px"/>')
    html_parts.append('</div>')
    html_parts.append('')
    html_parts.append('<p align="center">')
    html_parts.append(f'  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=16&duration=750&pause=0&color=FFFFFF&center=false&vCenter=true&multiline=true&repeat=false&width=650&height={quote_height}&lines={quote_encoded}" alt="AI Quote" />')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('<p align="center">')
    html_parts.append(f'  <sub>🤖 Powered by Google Gemini 2.5 • Updated: {current_time}</sub>')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('<br/>')
    html_parts.append('')
    html_parts.append('<!-- Animated Skill Bars -->')
    html_parts.append('')
    html_parts.append('### 🚀 Core Technologies')
    html_parts.append('')
    html_parts.append('<p align="center">')
    html_parts.append('  <img src="https://skillicons.dev/icons?i=python,anaconda,tensorflow,pytorch,opencv,aws,gcp,react,typescript,nodejs,docker,github,fastapi,html,selenium,figma,sketchup,autocad&theme=dark&perline=6" />')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('### 🛠️ Tech Stack')
    html_parts.append('')
    html_parts.append('<table align="center">')
    html_parts.append('  <tr>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/AI%20%26%20ML-FF6B6B?style=for-the-badge&logo=tensorflow&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>TensorFlow • PyTorch</b><br/><b>Scikit-learn • OpenCV</b><br/><b>SciPy</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/GenAI%20%26%20LLM-4ECDC4?style=for-the-badge&logo=openai&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>LangChain • Google ADK</b><br/><b>Amazon Bedrock • n8n</b><br/><b>Strands-Agents</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/Cloud%20%26%20DevOps-95E1D3?style=for-the-badge&logo=amazonaws&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>AWS • Lambda</b><br/><b>Google Cloud Platform</b><br/><b>GitHub Actions • Docker</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/Data%20Viz-FFB703?style=for-the-badge&logo=powerbi&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>PowerBi • Plotly</b><br/><b>Matplotlib • Seaborn</b><br/><b>Numpy • Pandas</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('  </tr>')
    html_parts.append('</table>')
    html_parts.append('')
    html_parts.append('<!-- Connect Section with Animated Badges -->')
    html_parts.append('<br/>')
    html_parts.append('')
    html_parts.append('### 🤝 Let\'s Connect')
    html_parts.append('')
    html_parts.append('<p align="center">')
    html_parts.append('  <a href="https://linkedin.com/in/rcrarq">')
    html_parts.append('    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&labelColor=0077B5"/>')
    html_parts.append('  </a>')
    html_parts.append('  <a href="https://www.behance.net/ricardorodrigu17">')
    html_parts.append('    <img src="https://img.shields.io/badge/Behance-1769FF?style=for-the-badge&logo=behance&logoColor=white&labelColor=1769FF"/>')
    html_parts.append('  </a>')
    html_parts.append('  <a href="https://www.youtube.com/@ricardocesarrodrigues837">')
    html_parts.append('    <img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white&labelColor=FF0000"/>')
    html_parts.append('  </a>')
    html_parts.append('  <a href="https://www.researchgate.net/profile/Ricardo-Rodrigues-26">')
    html_parts.append('    <img src="https://img.shields.io/badge/ResearchGate-00CCBB?style=for-the-badge&logo=researchgate&logoColor=white&labelColor=00CCBB"/>')
    html_parts.append('  </a>')
    html_parts.append('  <a href="https://scholar.google.com.br/citations?user=mVCXbNIAAAAJ">')
    html_parts.append('    <img src="https://img.shields.io/badge/Google_Scholar-4285F4?style=for-the-badge&logo=google-scholar&logoColor=white&labelColor=4285F4"/>')
    html_parts.append('  </a>')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('<!-- Profile Views Counter -->')
    html_parts.append('<br/>')
    html_parts.append('')
    html_parts.append('<p align="center">')
    html_parts.append('  <img src="https://komarev.com/ghpvc/?username=rickkk856&color=blueviolet&style=for-the-badge&label=Profile+Views" />')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('<!-- Animated Footer Wave -->')
    html_parts.append('<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=footer"/>')
    html_parts.append('')
    html_parts.append('---')
    html_parts.append('')
    html_parts.append('<p align="center">')
    html_parts.append('  <i>✨ This profile is dynamically updated using GitHub Actions & Google AI Studio ✨</i>')
    html_parts.append('  <br/>')
    html_parts.append(f'  <sub>Last updated: {last_updated}</sub>')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def update_readme(html_content):
    """Updates the README.md file with the new content."""
    readme_path = "README.md"
    
    # Create README if it doesn't exist
    if not os.path.exists(readme_path):
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("# Ricardo's Profile\n\n")
            f.write("<!-- GENERATED_CONTENT_START -->\n")
            f.write("<!-- GENERATED_CONTENT_END -->\n")

    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # Define markers
    start_marker = "<!-- GENERATED_CONTENT_START -->"
    end_marker = "<!-- GENERATED_CONTENT_END -->"

    # Create new content block
    new_content_block = f"{start_marker}\n\n{html_content}\n\n{end_marker}"

    # Replace content
    if start_marker in readme_content and end_marker in readme_content:
        pre_content = readme_content.split(start_marker)[0]
        post_content = readme_content.split(end_marker)[1]
        updated_readme_content = f"{pre_content}{new_content_block}{post_content}"
    else:
        print("Warning: Markers not found. Appending content.")
        updated_readme_content = f"{readme_content}\n\n{new_content_block}"

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_readme_content)
    print("README.md updated successfully!")

if __name__ == "__main__":
    print("🚀 Starting profile generation...")
    ai_quote = get_ai_quote()
    print(f"✅ AI Quote: {ai_quote}")

    html_content = generate_profile_html(ai_quote)
    update_readme(html_content)
    print("✨ Profile generation complete!")