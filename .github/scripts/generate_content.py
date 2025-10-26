import os
import requests
from datetime import datetime
import json

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
    
    prompt = "Generate a very short, interesting, and recent update or fact about Generative AI. Keep it to 1-3 sentences, maximum 25 words, no conversational filler."
    
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
    
    # Pre-process all strings that need escaping or special formatting
    location_encoded = RICARDO_LOCATION.replace(' ', '%20').replace(',', '%2C')
    quote_for_js = ai_quote.replace('"', r'\"').replace("'", r"\'").replace('\n', ' ')
    
    # Build HTML using string concatenation to avoid f-string issues
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
    html_parts.append('<!-- AI-Generated Insight Card with Streaming Animation -->')
    html_parts.append('<br/>')
    html_parts.append('')
    html_parts.append('<div align="center">')
    html_parts.append('  <table>')
    html_parts.append('    <tr>')
    html_parts.append('      <td>')
    html_parts.append('        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); max-width: 650px; margin: 15px auto;">')
    html_parts.append('          <div style="color: #fff; font-family: \'Courier New\', monospace; font-size: 14px; margin-bottom: 15px; opacity: 0.9;">')
    html_parts.append('            💡 AI INSIGHT OF THE DAY')
    html_parts.append('          </div>')
    html_parts.append('          <div id="ai-quote" style="color: #fff; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 1.6; min-height: 50px; text-align: left;">')
    html_parts.append('            <span id="quote-text"></span><span id="cursor" style="animation: blink 1s infinite;">|</span>')
    html_parts.append('          </div>')
    html_parts.append(f'          <div style="color: rgba(255,255,255,0.7); font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif; font-size: 12px; margin-top: 15px; text-align: right;">')
    html_parts.append(f'            🤖 Powered by Google Gemini 2.5 • Updated: {current_time}')
    html_parts.append('          </div>')
    html_parts.append('        </div>')
    html_parts.append('      </td>')
    html_parts.append('    </tr>')
    html_parts.append('  </table>')
    html_parts.append('</div>')
    html_parts.append('')
    html_parts.append('<script>')
    html_parts.append('  (function() {')
    html_parts.append(f'    const quote = "{quote_for_js}";')
    html_parts.append('    const quoteEl = document.getElementById(\'quote-text\');')
    html_parts.append('    const cursor = document.getElementById(\'cursor\');')
    html_parts.append('    let i = 0;')
    html_parts.append('    ')
    html_parts.append('    function typeWriter() {')
    html_parts.append('      if (i < quote.length) {')
    html_parts.append('        quoteEl.textContent += quote.charAt(i);')
    html_parts.append('        i++;')
    html_parts.append('        setTimeout(typeWriter, 50);')
    html_parts.append('      } else {')
    html_parts.append('        cursor.style.display = \'none\';')
    html_parts.append('      }')
    html_parts.append('    }')
    html_parts.append('    ')
    html_parts.append('    setTimeout(typeWriter, 500);')
    html_parts.append('  })();')
    html_parts.append('</script>')
    html_parts.append('')
    html_parts.append('<style>')
    html_parts.append('  @keyframes blink {')
    html_parts.append('    0%, 50% { opacity: 1; }')
    html_parts.append('    51%, 100% { opacity: 0; }')
    html_parts.append('  }')
    html_parts.append('</style>')
    html_parts.append('')
    html_parts.append('<!-- Animated Skill Bars -->')
    html_parts.append('<br/>')
    html_parts.append('')
    html_parts.append('### 🚀 Core Technologies')
    html_parts.append('')
    html_parts.append('<p align="center">')
    html_parts.append('  <img src="https://skillicons.dev/icons?i=python,tensorflow,pytorch,aws,gcp,react,typescript,docker&theme=dark" />')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('<!-- GitHub Stats with Custom Theme -->')
    html_parts.append('<br/>')
    html_parts.append('')
    html_parts.append('<table align="center">')
    html_parts.append('  <tr>')
    html_parts.append('    <td>')
    html_parts.append('      <img height="180em" src="https://github-readme-stats.vercel.app/api?username=rickkk856&show_icons=true&theme=tokyonight&hide_border=true&bg_color=0d1117&title_color=a78bfa&icon_color=667eea&text_color=c9d1d9" />')
    html_parts.append('    </td>')
    html_parts.append('    <td>')
    html_parts.append('      <img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username=rickkk856&layout=compact&theme=tokyonight&hide_border=true&bg_color=0d1117&title_color=a78bfa&text_color=c9d1d9" />')
    html_parts.append('    </td>')
    html_parts.append('  </tr>')
    html_parts.append('</table>')
    html_parts.append('')
    html_parts.append('<!-- Activity Graph -->')
    html_parts.append('<br/>')
    html_parts.append('')
    html_parts.append('<img src="https://github-readme-activity-graph.vercel.app/graph?username=rickkk856&custom_title=Contribution%20Graph&bg_color=0d1117&color=a78bfa&line=667eea&point=c9d1d9&area_color=667eea&title_color=fff&area=true&hide_border=true" width="100%"/>')
    html_parts.append('')
    html_parts.append('<!-- Tech Stack Grid -->')
    html_parts.append('<br/>')
    html_parts.append('')
    html_parts.append('### 🛠️ Tech Stack')
    html_parts.append('')
    html_parts.append('<table align="center">')
    html_parts.append('  <tr>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/AI%20%26%20ML-FF6B6B?style=for-the-badge&logo=tensorflow&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>TensorFlow • PyTorch<br/>Scikit-learn • OpenCV</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/GenAI%20%26%20LLM-4ECDC4?style=for-the-badge&logo=openai&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>LangChain • Vertex AI<br/>Amazon Bedrock • n8n</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/Cloud%20%26%20DevOps-95E1D3?style=for-the-badge&logo=amazonaws&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>AWS • GCP • Lambda<br/>GitHub Actions • Docker</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/Data%20Science-F38181?style=for-the-badge&logo=pandas&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>Pandas • NumPy<br/>Power BI • SQL</b></sub>')
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