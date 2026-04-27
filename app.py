import streamlit as st
import textwrap
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import io

# --- 1. KONFIGURATION & API ---
st.set_page_config(page_title="KI Meme Imperium", page_icon="🤣", layout="centered")

# HIER DEINEN GEMINI API KEY EINTRAGEN:
GEMINI_API_KEY = "AIzaSyDTbt6gJy-kZp4lv93nrUDD8ny2NM9nxYk" 

# Verbindung zu Google Gemini herstellen
genai.configure(api_key=GEMINI_API_KEY)

# Wir nutzen 'gemini-1.5-flash-latest' für die beste Erreichbarkeit
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    model = genai.GenerativeModel('gemini-3-flash') # Backup-Modell

# --- 2. KI FUNKTION (Humor-Zentrale) ---
def get_ai_text(topic):
    """Holt kreative Meme-Sprüche von Google Gemini."""
    prompt = (
        f"Du bist ein Experte für Internet-Memes. Erstelle ein kurzes, lustiges Meme über: {topic}. "
        "Antworte STRENG im Format: [Text] | [Text]. "
        "Halte dich kurz (max. 5 Wörter pro Zeile)."
    )
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if "|" in text:
            parts = text.split("|")
            top = parts[0].replace("Oben:", "").strip()
            bottom = parts[1].replace("Unten:", "").strip()
            return top.upper(), bottom.upper()
        else:
            # Falls Gemini das Format ignoriert, versuchen wir Zeilen zu trennen
            lines = text.splitlines()
            if len(lines) >= 2:
                return lines[0].upper(), lines[1].upper()
            return "WENN DIE KI", "EIGENWILLIG ANTWORTET"
    except Exception as e:
        return "KI-FEHLER", "PRÜFE API-KEY ODER LIMITS"

# --- 3. BILDVERARBEITUNG (Das visuelle Herzstück) ---
def create_meme(img_input, top_text, bottom_text):
    img = Image.open(img_input).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Schriftgröße berechnen (dynamisch angepasst)
    base_size = min(width / 10, height / 12)
    font_size = int(max(base_size, 35))
    
    try:
        # Sucht Arial (Standard auf Windows), sonst Fallback
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    def draw_styled_text(text, position_y):
        if not text: return
        # Zeilenumbruch-Logik
        chars_per_line = int(width / (font_size * 0.6))
        lines = textwrap.wrap(text, width=max(chars_per_line, 12))
        
        y_offset = position_y
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (width - w) / 2
            
            # Massive schwarze Outline für Lesbarkeit
            outline = max(int(font_size / 15), 2)
            for ax in range(-outline, outline + 1):
                for ay in range(-outline, outline + 1):
                    draw.text((x + ax, y_offset + ay), line, font=font, fill="black")
            
            # Weißer Haupttext
            draw.text((x, y_offset), line, font=font, fill="white")
            y_offset += h + int(font_size / 5)

    # Oben zeichnen
    draw_styled_text(top_text, int(height / 20))
    
    # Unten zeichnen (berechnet Position von unten nach oben)
    chars_per_line = int(width / (font_size * 0.6))
    num_lines = len(textwrap.wrap(bottom_text, width=max(chars_per_line, 12)))
    bottom_y = height - (num_lines * font_size * 1.4) - int(height / 15)
    draw_styled_text(bottom_text, bottom_y)
    
    return img

# --- 4. STREAMLIT WEB-OBERFLÄCHE ---
st.title("🤣 Mein KI Meme Business")
st.write("Erstelle virale Memes mit Google Gemini KI!")

# Layout Spalten
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Konfiguration")
    thema = st.text_input("Thema eingeben:", "Homeoffice")
    uploaded_file = st.file_uploader("Eigenes Bild (optional)", type=["jpg", "png", "jpeg"])
    st.info("Kein Bild? Ich nutze 'template.jpg' aus deinem Ordner.")
    
    generate_btn = st.button("Meme generieren! ✨")

with col2:
    st.header("Ergebnis")
    if generate_btn:
        with st.spinner("Gemini schreibt den Text..."):
            # 1. Text von KI
            top, bottom = get_ai_text(thema)
            
            # 2. Bildquelle
            source = uploaded_file if uploaded_file else "template.jpg"
            
            try:
                # 3. Meme bauen
                final_img = create_meme(source, top, bottom)
                
                # 4. Anzeigen
                st.image(final_img, use_container_width=True)
                
                # 5. Download-Vorbereitung
                buf = io.BytesIO()
                final_img.save(buf, format="JPEG")
                st.download_button("Meme speichern ⬇️", buf.getvalue(), "mein_ki_meme.jpg", "image/jpeg")
                
            except FileNotFoundError:
                st.error("Datei 'template.jpg' nicht gefunden. Bitte lade ein Bild hoch!")
            except Exception as e:
                st.error(f"Fehler: {e}")
    else:
        st.write("Hier erscheint gleich dein Meme.")