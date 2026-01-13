import streamlit as st
import cv2
import numpy as np
from PIL import Image

def draw_technical_dimension(img, p1, p2, text, is_vertical=False):
    """Ölçü çizgilerini siyah ve ince çizer."""
    color = (0, 0, 0)
    thickness = 1
    offset = 30
    x1, y1 = p1
    x2, y2 = p2

    if not is_vertical:
        line_y = y1 - offset
        cv2.line(img, (x1, y1), (x1, line_y), color, 1)
        cv2.line(img, (x2, y2), (x2, line_y), color, 1)
        cv2.line(img, (x1, line_y), (x2, line_y), color, 1)
        cv2.putText(img, text, (x1 + (x2-x1)//2 - 20, line_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    else:
        line_x = x1 - offset
        cv2.line(img, (x1, y1), (line_x, y1), color, 1)
        cv2.line(img, (x1, y2), (line_x, y2), color, 1)
        cv2.line(img, (line_x, y1), (line_x, y2), color, 1)
        cv2.putText(img, text, (line_x - 40, y1 + (y2-y1)//2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

st.set_page_config(layout="wide", page_title="Teknik Çizim")
st.title("📏 Arkeolojik Teknik Çizim Paneli")

uploaded_file = st.file_uploader("Fotoğraf yükleyin...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Resmi oku
    img_pil = Image.open(uploaded_file)
    img_array = np.array(img_pil)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # Boş Beyaz Tuval Oluştur
    pad = 60
    h, w = img_bgr.shape[:2]
    canvas = np.ones((h + 2*pad, w + 2*pad, 3), dtype="uint8") * 255

    if st.button("Teknik Çizimi Üret"):
        with st.spinner("Çiziliyor..."):
            # Görüntü İşleme (Tüm resmi yakalamak için)
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            # Keskinliği artırıp gürültüyü azaltalım
            blurred = cv2.bilateralFilter(gray, 9, 75, 75) 
            edged = cv2.Canny(blurred, 30, 100) # Daha hassas kenar tespiti

            # TÜM konturları bul
            contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:
                # 1. TÜM hatları ince siyah kalemle (thickness=1) çiz
                cv2.drawContours(canvas[pad:-pad, pad:-pad], contours, -1, (0, 0, 0), 1)

                # 2. Genel sınırları bul (Ölçülendirme için)
                all_pts = np.vstack(contours)
                rx, ry, rw, rh = cv2.boundingRect(all_pts)
                
                # Tuval üzerindeki yerleri
                nx, ny = rx + pad, ry + pad

                # 3. Ölçülendirme
                draw_technical_dimension(canvas, (nx, ny), (nx + rw, ny), f"{rw}px")
                draw_technical_dimension(canvas, (nx, ny), (nx, ny + rh), f"{rh}px", True)

                # Görselleştirme
                col1, col2 = st.columns(2)
                col1.image(img_pil, caption="Orijinal", use_container_width=True)
                
                # Kırpma: Sadece çizilen objeyi göster
                final_view = canvas[max(0, ny-50):min(canvas.shape[0], ny+rh+50), 
                                    max(0, nx-50):min(canvas.shape[1], nx+rw+50)]
                col2.image(final_view, caption="Teknik Çizim", use_container_width=True)
            else:
                st.warning("Belirgin bir hat bulunamadı. Lütfen daha net bir fotoğraf deneyin.")
