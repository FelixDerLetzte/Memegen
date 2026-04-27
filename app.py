import streamlit as st
import textwrap
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import io

# --- KONFIGURATION ---
st.set_page_config(page_title="KI Meme Generator", page_icon="🤣")

# Dein Groq API Key (am besten in den Secrets speichern, für lokal hier eintragen)
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# --- FUNKTIONEN ---
def get_ai_text(topic):
    prompt = f"Gib mir einen extrem kurzen, lustigen Meme-Spruch über {topic}. Antworte NUR im Format: Oben: [Text] | Unten: [Text]"
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        response = completion.choices[0].message.content
        top, bottom = response.replace("Oben: ", "").replace("Unten: ", "").split("|")
        return top.strip().upper(), bottom.strip().upper()
    except:
        return "FEHLER BEIM LADEN", "KI HAT KEINE LUST"

def create_meme(img_input, top_text, bottom_text):
    img = Image.open(img_input).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    font_size = int(width / 12)
    
    try:
        # Versucht eine Schriftart zu laden
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    def draw_styled_text(text, y_pos):
        lines = textwrap.wrap(text, width=15)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (width - w) / 2
            # Outline
            for adj in range(-3, 4):
                draw.text((x+adj, y_pos), line, font=font, fill="black")
                draw.text((x, y_pos+adj), line, font=font, fill="black")
            # Text
            draw.text((x, y_pos), line, font=font, fill="white")
            y_pos += h + 10

    draw_styled_text(top_text, 20)
    draw_styled_text(bottom_text, height - (font_size * 2.5))
    return img

# --- WEBSITE LAYOUT ---
st.title("🤣 KI Meme Generator")
st.write("Gib ein Thema ein und lass die KI den Rest erledigen!")

col1, col2 = st.columns([1, 1])

with col1:
    thema = st.text_input("Über was soll das Meme sein?", "Programmieren")
    uploaded_file = st.file_uploader("Eigenes Bild hochladen (optional)", type=["jpg", "png", "jpeg"])
    
    generate_btn = st.button("Meme generieren! ✨")

with col2:
    if generate_btn:
        with st.spinner('KI denkt nach...'):
            # 1. Text von KI holen
            top, bottom = get_ai_text(thema)
            
            # 2. Bildquelle wählen
            source_img = uploaded_file if uploaded_file else "temp.jpg"
            
            # 3. Meme erstellen
            result_img = create_meme(source_img, top, bottom)
            
            # 4. Anzeigen
            st.image(result_img, caption="Dein fertiges Meme", use_container_width=True)
            
            # 5. Download Button
            buf = io.BytesIO()
            result_img.save(buf, format="JPEG")
            byte_im = buf.getvalue()
            st.download_button(label="Bild herunterladen", data=byte_im, file_name="meme.jpg", mime="image/jpeg")
    else:
        st.info("Warte auf deine Eingabe...")