import streamlit as st
import textwrap
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import io

# --- 1. KONFIGURATION & API ---
st.set_page_config(page_title="KI Meme Generator", page_icon="🤣")

# HIER DEINEN KEY EINTRAGEN:
GROQ_API_KEY = "DEIN_GROQ_API_KEY_HIER" 

# Falls du es auf Streamlit Cloud hostest, nutze diese Zeile stattdessen:
# GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)

# --- 2. KI FUNKTION ---
def get_ai_text(topic):
    """Holt einen lustigen Spruch von der Groq-KI."""
    prompt = f"Gib mir einen extrem kurzen, lustigen Meme-Spruch über {topic}. Antworte NUR im Format: Oben: [Text] | Unten: [Text]"
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        response = completion.choices[0].message.content
        # Text zerlegen
        top, bottom = response.replace("Oben: ", "").replace("Unten: ", "").split("|")
        return top.strip().upper(), bottom.strip().upper()
    except Exception as e:
        print(f"KI Fehler: {e}")
        return "WENN DIE KI", "NICHT FUNKTIONIERT"

# --- 3. BILDVERARBEITUNG (VERBESSERT) ---
def create_meme(img_input, top_text, bottom_text):
    """Erstellt das Meme mit optimierter Schriftgröße."""
    img = Image.open(img_input).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Intelligente Schriftgröße: Passt sich Breite UND Höhe an
    base_font_size = min(width / 10, height / 12)
    font_size = int(max(base_font_size, 30))
    
    try:
        # Versucht Arial zu laden, sonst Standard
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    def draw_styled_text(text, position_y):
        if not text: return
        
        # Zeilenumbruch basierend auf Bildbreite
        chars_per_line = int(width / (font_size * 0.7))
        lines = textwrap.wrap(text, width=max(chars_per_line, 10))
        
        current_y = position_y
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (width - w) / 2
            
            # Fette schwarze Outline (für bessere Lesbarkeit)
            outline_range = max(int(font_size / 15), 2)
            for adj_x in range(-outline_range, outline_range + 1):
                for adj_y in range(-outline_range, outline_range + 1):
                    draw.text((x + adj_x, current_y + adj_y), line, font=font, fill="black")
            
            # Weißer Haupttext
            draw.text((x, current_y), line, font=font, fill="white")
            current_y += h + int(font_size / 5)

    # Text oben zeichnen
    draw_styled_text(top_text, int(height / 25))
    
    # Text unten berechnen (damit er nicht unten rausfällt)
    chars_per_line = int(width / (font_size * 0.7))
    num_lines = len(textwrap.wrap(bottom_text, width=max(chars_per_line, 10)))
    bottom_y_start = height - (num_lines * font_size * 1.3) - int(height / 20)
    
    draw_styled_text(bottom_text, bottom_y_start)
    
    return img

# --- 4. WEBSITE LAYOUT (STREAMLIT) ---
st.title("🤣 Dein KI Meme Business")
st.write("Wähle ein Thema und erstelle Content auf Knopfdruck.")

# Sidebar für Einstellungen
with st.sidebar:
    st.header("Einstellungen")
    uploaded_file = st.file_uploader("Bild hochladen", type=["jpg", "png", "jpeg"])
    st.info("Kein Bild hochgeladen? Es wird 'template.jpg' genutzt.")

# Hauptbereich
thema = st.text_input("Meme-Thema eingeben:", "Programmieren")

if st.button("Meme JETZT generieren! ✨"):
    with st.spinner('KI generiert Spruch und Bild...'):
        # 1. Text holen
        top, bottom = get_ai_text(thema)
        
        # 2. Bildquelle festlegen
        if uploaded_file:
            source = uploaded_file
        else:
            source = "template.jpg" # Stelle sicher, dass die Datei existiert!
            
        try:
            # 3. Meme erstellen
            meme_img = create_meme(source, top, bottom)
            
            # 4. Anzeigen
            st.image(meme_img, caption=f"Thema: {thema}", use_container_width=True)
            
            # 5. Download
            buf = io.BytesIO()
            meme_img.save(buf, format="JPEG")
            st.download_button("Bild speichern", buf.getvalue(), "mein_meme.jpg", "image/jpeg")
            
        except FileNotFoundError:
            st.error("Fehler: 'template.jpg' wurde nicht gefunden! Bitte lade ein Bild hoch oder lege eine Datei namens 'template.jpg' in den Ordner.")