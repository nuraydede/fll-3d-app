import streamlit as st
import cv2
import numpy as np
from PIL import Image

def draw_technical_dimension(img, p1, p2, text, is_vertical=False):
    """Teknik resim standartlarında ölçü çizgisi ve ok çizer."""
    color = (0, 0, 0)  # Siyah çizgiler
    thickness = 1
    offset = 40  # Nesneden uzaklık
    tick_size = 5

    x1, y1 = p1
    x2, y2 = p2

    if not is_vertical:
        # Yatay Ölçülendirme (Genişlik)
        line_y = min(y1, y2) - offset
        # Uzatma çizgileri
        cv2.line(img, (x1, y1 - 5), (x1, line_y - tick_size), color, thickness)
        cv2.line(img, (x2, y2 - 5), (x2, line_y - tick_size), color, thickness)
        # Ana ölçü çizgisi ve oklar
        cv2.arrowedLine(img, (x1 + 20, line_y), (x1, line_y), color, thickness, tipLength=0.2)
        cv2.arrowedLine(img, (x2 - 20, line_y), (x2, line_y), color, thickness, tipLength=0.2)
        cv2.line(img, (x1, line_y), (x2, line_y), color, thickness)
        # Metin
        cv2.putText(img, text, (x1 + (x2-x1)//2 - 25, line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    else:
        # Dikey Ölçülendirme (Yükseklik)
        line_x = x1 - offset
        # Uzatma çizgileri
        cv2.line(img, (x1 - 5, y1), (line_x - tick_size, y1), color, thickness)
        cv2.line(img, (x1 - 5, y2), (line_x - tick_size, y2), color, thickness)
        # Ana ölçü çizgisi ve oklar
        cv2.arrowedLine(img, (line_x, y1 + 20), (line_x, y1), color, thickness, tipLength=0.2)
        cv2.arrowedLine(img, (line_x, y2 - 20), (line_x, y2), color, thickness, tipLength=0.2)
        cv2.line(img, (line_x, y1), (line_x, y2), color, thickness)
        # Metin (Dikey)
        cv2.putText(img, text, (line_x - 45, y1 + (y2-y1)//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

# Streamlit Arayüzü
st.set_page_config(layout="wide")
st.title("📏 Arkeolojik Buluntu Teknik Çizim Programı")

uploaded_file = st.file_uploader("Arkeolojik parça fotoğrafı yükleyin...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Çizim için beyaz sayfa ve padding (boşluk) ekleme
    pad = 80
    canvas_h, canvas_w = img_bgr.shape[0] + 2*pad, img_bgr.shape[1] + 2*pad
    white_canvas = np.ones((canvas_h, canvas_w, 3), dtype="uint8") * 255
    
    if st.button("Teknik Çizimi Üret"):
        # Görüntü İşleme
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        
        # Konturları bul
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # En büyük nesneyi merkeze al (Diğer gürültüleri temizler)
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            
            # Nesnenin hatlarını beyaz tuvale aktar (Siyah kalemle)
            cv2.drawContours(white_canvas[pad:-pad, pad:-pad], [c], -1, (0, 0, 0), 2)
            
            # Ölçülendirme koordinatlarını ayarla
            nx, ny = x + pad, y + pad # Tuvaldeki yeni koordinatlar
            
            # GENİŞLİK ÖLÇÜSÜ (Üstte)
            draw_technical_dimension(white_canvas, (nx, ny), (nx + w, ny), f"{w} px")
            
            # YÜKSEKLİK ÖLÇÜSÜ (Solda)
            draw_technical_dimension(white_canvas, (nx, ny), (nx, ny + h), f"{h} px", is_vertical=True)
            
            # Sonuçları Göster
            # --- Sonuçları Göster ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(img, caption="Orijinal Görüntü", use_container_width=True)
            
            with col2:
                # ÖNEMLİ: Çizimi nesneye göre kırpıyoruz ki ekranda büyük görünsün
                # Nesnenin olduğu alanı ve ölçülendirme paylarını (pad) seçiyoruz
                crop_y1, crop_y2 = max(0, ny - pad), min(canvas_h, ny + h + pad)
                crop_x1, crop_x2 = max(0, nx - pad), min(canvas_w, nx + w + pad)
                
                final_view = white_canvas[crop_y1:crop_y2, crop_x1:crop_x2]
                
                st.image(final_view, caption="Teknik Ölçülendirilmiş Çizim", use_container_width=True)
