import streamlit as st
import textwrap
from google import genai
from PIL import Image, ImageDraw, ImageFont
import io

# --- 1. KONFIGURATION & SICHERHEIT ---
st.set_page_config(page_title="KI Meme Imperium 2026", page_icon="🤣")

# Diese Logik prüft, ob der Key in den Cloud-Secrets liegt oder lokal eingetragen ist
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # HIER DEINEN KEY FÜR LOKALE TESTS EINTRAGEN
    api_key = "DEIN_LOKALER_API_KEY_HIER"

# Initialisierung der neuen Google GenAI Bibliothek
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("API Key Konfigurationsfehler. Bitte Secrets prüfen.")

# --- 2. KI FUNKTION (Gemini 2.0) ---
def get_ai_text(topic):
    prompt = (
        f"Du bist ein Meme-Profi. Erstelle ein kurzes, lustiges Meme über: {topic}. "
        "Antworte NUR im Format: Oben: [Text] | Unten: [Text]. "
        "Maximal 5 Wörter pro Zeile."
    )
    
    # Wir probieren erst Flash, dann Lite als Backup
    for model_id in ["gemini-2.0-flash", "gemini-2.0-flash-lite"]:
        try:
            response = client.models.generate_content(
                model=model_id, 
                contents=prompt
            )
            text = response.text.strip()
            
            if "|" in text:
                parts = text.split("|")
                top = parts[0].replace("Oben:", "").strip().upper()
                bottom = parts[1].replace("Unten:", "").strip().upper()
                return top, bottom
            else:
                lines = text.splitlines()
                return lines[0].upper(), lines[-1].upper()
        except:
            continue
            
    return "QUOTA ERREICHT", "BITTE KURZ WARTEN"

# --- 3. BILDVERARBEITUNG (Optimiert für alle Formate) ---
def create_meme(img_input, top_text, bottom_text):
    img = Image.open(img_input).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Dynamische Schriftgröße
    base_size = min(width / 10, height / 12)
    font_size = int(max(base_size, 35))
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    def draw_styled_text(text, position_y):
        if not text: return
        chars_per_line = int(width / (font_size * 0.6))
        lines = textwrap.wrap(text, width=max(chars_per_line, 12))
        
        y_offset = position_y
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (width - w) / 2
            
            # Outline für Lesbarkeit
            outline = max(int(font_size / 15), 2)
            for ax in range(-outline, outline + 1):
                for ay in range(-outline, outline + 1):
                    draw.text((x + ax, y_offset + ay), line, font=font, fill="black")
            
            draw.text((x, y_offset), line, font=font, fill="white")
            y_offset += h + int(font_size / 5)

    # Texte zeichnen
    draw_styled_text(top_text, int(height / 20))
    
    chars_per_line = int(width / (font_size * 0.6))
    num_lines = len(textwrap.wrap(bottom_text, width=max(chars_per_line, 12)))
    bottom_y = height - (num_lines * font_size * 1.4) - int(height / 15)
    draw_styled_text(bottom_text, bottom_y)
    
    return img

# --- 4. WEB-OBERFLÄCHE (Streamlit) ---
st.title("🤣 KI Meme Generator Pro")
st.markdown("Erstelle Content für Social Media mit Gemini 2.0")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Einstellungen")
    thema = st.text_input("Thema:", "Programmieren")
    uploaded_file = st.file_uploader("Bild hochladen", type=["jpg", "png", "jpeg"])
    generate_btn = st.button("Meme generieren! ✨")

with col2:
    st.subheader("Vorschau")
    if generate_btn:
        with st.spinner("KI generiert Spruch..."):
            top, bottom = get_ai_text(thema)
            
            if top == "QUOTA ERREICHT":
                st.warning("Gratis-Limit bei Google erreicht. Bitte kurz warten.")
            else:
                source = uploaded_file if uploaded_file else "template.jpg"
                try:
                    final_meme = create_meme(source, top, bottom)
                    st.image(final_meme, use_container_width=True)
                    
                    # Download
                    buf = io.BytesIO()
                    final_meme.save(buf, format="JPEG")
                    st.download_button("Download ⬇️", buf.getvalue(), "meme.jpg", "image/jpeg")
                except Exception as e:
                    st.error(f"Fehler: {e}")
    else:
        st.info("Warte auf Eingabe...")