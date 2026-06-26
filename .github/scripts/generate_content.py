# .github\scripts\generate_content.py
import os
import requests
from datetime import datetime
from urllib.parse import quote as url_quote
import textwrap
import time

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds

# --- Static Profile Info ---
RICARDO_NAME = "Ricardo"
RICARDO_LOCATION = "São Paulo, SP, Brazil"

def get_api_url(model_id):
    """Generates the API URL for a given model ID, respecting custom proxy settings if present."""
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    custom_url = os.getenv("GOOGLE_AI_STUDIO_API_URL")
    
    if custom_url:
        # Se você configurou uma URL customizada (ex: Cloudflare ou proxy próprio),
        # substituímos dinamicamente o modelo para manter a estrutura do proxy.
        for model in ["gemini-3.5-flash", "gemini-2.5-flash"]:
            if model in custom_url:
                return custom_url.replace(model, model_id)
    return f"{base_url}/models/{model_id}:generateContent"

def get_ai_quote():
    """Fetches a short quote about Generative AI with fallback models to handle quota issues."""
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return "AI is constantly evolving, bringing new possibilities.", "Default Fallback"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GOOGLE_API_KEY
    }

    now = datetime.now()
    formatted_date = now.strftime("%d of %B %Y")  
    prompt = (
        f"Hi, Today is {formatted_date}. Please generate a very short, interesting, and recent "
        f"update or fact about Generative AI and Real Estate and/or Architecture Industry. "
        f"Keep it to 4-6 sentences and mention today's date/month or year, no conversational filler."
    )

    # Lista de modelos prioritários ativos e não obsoletos
    models_fallback = [
        {"id": "gemini-3.5-flash", "name": "Google Gemini 3.5 Flash"},
        {"id": "gemini-3.1-flash-lite", "name": "Google Gemini 3.1 Flash-Lite"},
        {"id": "gemini-3.1-pro-preview", "name": "Google Gemini 3.1 Pro Preview"}
    ]

    for model_info in models_fallback:
        model_id = model_info["id"]
        model_name = model_info["name"]
        api_url = get_api_url(model_id)

        data = {
            "tools": [{"googleSearch": {}}],
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 2048,
                "thinkingConfig": {
                    "thinkingLevel": "minimal"
                }
            }
        }

        print(f"Attempting to generate quote using {model_name} ({model_id})...")
        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=120)
            
            # Se recebermos 429, forçamos a subida de exceção para pular para o próximo modelo
            if response.status_code == 429:
                print(f"⚠️ Model {model_id} is rate-limited / out of quota (429).")
                raise requests.exceptions.RequestException("Quota exceeded (429)")
                
            response.raise_for_status()
            response_data = response.json()
            
            # Validação do retorno
            if 'candidates' not in response_data or not response_data['candidates']:
                raise ValueError("No candidates returned")
                
            first_candidate = response_data['candidates'][0]
            finish_reason = first_candidate.get('finishReason', 'UNKNOWN')
            
            if finish_reason != 'STOP' and finish_reason in ['SAFETY', 'RECITATION', 'OTHER']:
                raise ValueError(f"Response blocked due to: {finish_reason}")
            
            if 'content' not in first_candidate or 'parts' not in first_candidate['content']:
                raise ValueError("Malformed response structure")
                
            for part in first_candidate['content']['parts']:
                if 'text' in part and part['text'].strip():
                    extracted_text = part['text'].strip()
                    print(f"✅ Successfully generated quote using {model_name}!")
                    return extracted_text, model_name
                    
            raise ValueError("No valid text found in parts")

        except Exception as e:
            print(f"❌ Failed with model {model_id}: {e}")
            print(f"Waiting {RETRY_DELAY} seconds before trying next fallback model...")
            time.sleep(RETRY_DELAY)

    # Se todos os modelos falharem
    print("All fallback models exhausted. Using default fallback quote.")
    return (
        "Generative AI continues to transform industries with breakthrough innovations.",
        "System Fallback (No Active Model)"
    )

def generate_profile_html(ai_quote, model_name):
    """Generates beautiful, animated HTML for GitHub profile with a blue theme."""
    
    current_day = datetime.now().strftime("%A")
    current_time = datetime.now().strftime("%H:%M UTC")
    last_updated = datetime.now().strftime("%B %d, %Y at %H:%M UTC")
    
    location_encoded = RICARDO_LOCATION.replace(' ', '%20').replace(',', '%2C')
    wrapped_lines = textwrap.wrap(ai_quote, width=60)
    quote_multiline = ';'.join(wrapped_lines)
    quote_encoded = url_quote(quote_multiline)
    quote_height = max(100, len(wrapped_lines) * 25 + 10)
    
    html_parts = []
    
    html_parts.append('<div align="center">')

    # Profile Header
    html_parts.append('<!-- Profile Header with Blue Gradient Animation -->')
    html_parts.append('<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=2,10,18,24&height=180&section=header&text=Ricardo%20Rodrigues&fontSize=42&fontColor=ffffff&animation=twinkling&fontAlignY=32"/>')

    # Animated Typing Effect
    html_parts.append('<!-- Animated Typing Effect -->')
    html_parts.append('<p align="center">')
    html_parts.append('  <picture>')
    html_parts.append('    <!-- Dark Mode -->')
    html_parts.append('    <source srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=00BFFF&center=true&vCenter=true&multiline=false&repeat=true&width=600&lines=AI+Engineering+%7C+Data+Science;MSc+Architectural+Design+with+AI;5%2B+Years+Working+With+AI+Models" media="(prefers-color-scheme: dark)"/>')
    html_parts.append('    <!-- Light Mode -->')
    html_parts.append('    <source srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=000000&center=true&vCenter=true&multiline=false&repeat=true&width=600&lines=AI+Engineering+%7C+Data+Science;MSc+Architectural+Design+with+AI;5%2B+Years+Working+With+AI+Models" media="(prefers-color-scheme: light)"/>')
    html_parts.append('    <!-- Fallback -->')
    html_parts.append('    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=00BFFF&center=true&vCenter=true&multiline=false&repeat=true&width=600&lines=AI+Engineering+%7C+Data+Science;MSc+Architectural+Design+with+AI;5%2B+Years+Working+With+AI+Models" alt="Typing SVG"/>')
    html_parts.append('  </picture>')
    html_parts.append('</p>')

    # Dynamic Status Cards
    html_parts.append('<!-- Dynamic Status Cards -->')
    html_parts.append('<table align="center">')
    html_parts.append('  <tr>')
    html_parts.append(f'    <td align="center" style="padding: 0;">')
    html_parts.append(f'      <img src="https://img.shields.io/badge/🌍_Location-{location_encoded}-2196F3?style=for-the-badge&labelColor=auto" alt="Location"/>')
    html_parts.append('    </td>')
    html_parts.append(f'    <td align="center" style="padding: 0;">')
    html_parts.append(f'      <img src="https://img.shields.io/badge/📅_Today-{current_day}-00BFFF?style=for-the-badge&labelColor=auto" alt="Day"/>')
    html_parts.append('    </td>')
    html_parts.append('  </tr>')
    html_parts.append('</table>')

    # AI Insight Section
    html_parts.append('<br/>')
    html_parts.append('<div align="center">')
    html_parts.append('  <img src="https://capsule-render.vercel.app/api?type=speech&color=gradient&customColorList=10,14,20&height=80&section=header&text=💡%20AI%20INSIGHT%20OF%20THE%20DAY&fontSize=20&fontColor=ffffff&fontAlignY=45" width="650px"/>')
    html_parts.append('</div>')

    # AI Quote
    html_parts.append('<p align="center">')
    html_parts.append('  <picture>')
    html_parts.append('    <!-- Dark Mode -->')
    html_parts.append(f'    <source srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&size=16&duration=1250&pause=0&color=9BE2FE&center=false&vCenter=true&multiline=true&repeat=false&width=650&height={quote_height}&lines={quote_encoded}" media="(prefers-color-scheme: dark)"/>')
    html_parts.append('    <!-- Light Mode -->')
    html_parts.append(f'    <source srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&size=16&duration=1250&pause=0&color=000000&center=false&vCenter=true&multiline=true&repeat=false&width=650&height={quote_height}&lines={quote_encoded}" media="(prefers-color-scheme: light)"/>')
    html_parts.append('    <!-- Fallback -->')
    html_parts.append(f'    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=16&duration=1250&pause=0&color=9BE2FE&center=false&vCenter=true&multiline=true&repeat=false&width=650&height={quote_height}&lines={quote_encoded}" alt="AI Quote"/>')
    html_parts.append('  </picture>')
    html_parts.append('</p>')

    html_parts.append('<p align="center">')
    # O rodapé agora reflete dinamicamente o modelo que gerou o texto
    html_parts.append(f'  <sub>🤖 Powered by {model_name} • Updated: {current_time}</sub>')
    html_parts.append('</p>')
    html_parts.append('<br/>')

    # Core Technologies
    html_parts.append('')
    html_parts.append('')
    html_parts.append('### 🚀 Core Technologies')
    html_parts.append('')
    html_parts.append('<p align="center">')
    html_parts.append('  <img src="https://skills.syvixor.com/api/icons?perline=6&i=python,anaconda,docker,jupyter,pypi,uvicorn,amazonwebservices,googlecloud,azure,github,githubactions,git,tensorflow,pytorch,opencv,fastapi,swagger,openapi,postgresql,grafana,prometheus,tempo,javascript,typescript,reactjs,vite,vuejs,html,css,figma,adobephotoshop,autocad,wordpress,microsoftpowerautomate,microsoftvisio,powerbi,claudeai,googlegemini,chatgpt,deepseek,ollama,pydantic" />')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('### 🛠️ Tech Stack')
    html_parts.append('<table align="center">')
    html_parts.append('  <tr>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/AI%20%26%20ML-1E88E5?style=for-the-badge&logo=tensorflow&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>TensorFlow • PyTorch</b><br/><b>Scikit-learn • OpenCV</b><br/><b>SciPy</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/GenAI%20%26%20LLM-0288D1?style=for-the-badge&logo=openai&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>LangChain • Google ADK</b><br/><b>Amazon Bedrock • n8n</b><br/><b>Strands-Agents • Agno</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/Cloud%20%26%20DevOps-00ACC1?style=for-the-badge&logo=amazonaws&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>AWS • Lambda</b><br/><b>GCP • GitHub Actions</b><br/><b>Docker • CI/CD</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('    <td align="center" width="25%">')
    html_parts.append('      <img src="https://img.shields.io/badge/Data%20Viz-29B6F6?style=for-the-badge&logo=powerbi&logoColor=white"/>')
    html_parts.append('      <br/><sub><b>PowerBi • Plotly</b><br/><b>Matplotlib • Seaborn</b><br/><b>Numpy • Pandas</b></sub>')
    html_parts.append('    </td>')
    html_parts.append('  </tr>')
    html_parts.append('</table>')
    html_parts.append('')
    html_parts.append('<br/>')

    # Let's Connect Section
    html_parts.append('')
    html_parts.append('### 🤝 Let\'s Connect')
    html_parts.append('')
    html_parts.append('<p align="center">')
    html_parts.append('  <a href="https://linkedin.com/in/rcrarq"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/></a>')
    html_parts.append('  <a href="https://www.behance.net/ricardorodrigu17"><img src="https://img.shields.io/badge/Behance-1769FF?style=for-the-badge&logo=behance&logoColor=white"/></a>')
    html_parts.append('  <a href="https://www.youtube.com/@ricardocesarrodrigues837"><img src="https://img.shields.io/badge/YouTube-1E3A8A?style=for-the-badge&logo=youtube&logoColor=white"/></a>')
    html_parts.append('  <a href="https://www.researchgate.net/profile/Ricardo-Rodrigues-26"><img src="https://img.shields.io/badge/ResearchGate-00B8D4?style=for-the-badge&logo=researchgate&logoColor=white"/></a>')
    html_parts.append('  <a href="https://scholar.google.com.br/citations?user=mVCXbNIAAAAJ"><img src="https://img.shields.io/badge/Google_Scholar-1976D2?style=for-the-badge&logo=google-scholar&logoColor=white"/></a>')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('<br/>')
    html_parts.append('<p align="center">')
    html_parts.append('  <img src="https://komarev.com/ghpvc/?username=rickkk856&color=00BFFF&style=for-the-badge&label=Profile+Views" />')
    html_parts.append('</p>')
    html_parts.append('')
    html_parts.append('<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=2,10,18,24&height=120&section=footer"/>')
    html_parts.append('')
    html_parts.append('---')
    html_parts.append('<p align="center">')
    html_parts.append('  <i>✨ This profile is dynamically updated using GitHub Actions & Google AI Studio ✨</i><br/>')
    html_parts.append('</p>')
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def update_readme(html_content):
    """Updates the README.md file with the new content."""
    readme_path = "README.md"
    
    if not os.path.exists(readme_path):
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("# Ricardo's Profile\n\n")
            f.write("<!-- GENERATED_CONTENT_START -->\n")
            f.write("<!-- GENERATED_CONTENT_END -->\n")

    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    start_marker = "<!-- GENERATED_CONTENT_START -->"
    end_marker = "<!-- GENERATED_CONTENT_END -->"

    new_content_block = f"{start_marker}\n\n{html_content}\n\n{end_marker}"

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
    ai_quote, used_model = get_ai_quote()
    print(f"✅ AI Quote: {ai_quote}")
    print(f"🤖 Used Model: {used_model}")

    html_content = generate_profile_html(ai_quote, used_model)
    update_readme(html_content)
    print("✨ Profile generation complete!")