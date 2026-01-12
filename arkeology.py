import streamlit as st
import cv2
import numpy as np
from PIL import Image

# Başlık ve Açıklama 📝
st.set_page_config(layout="wide")
st.title("🏛️ Arkeolojik Teknik Çizim & Ölçülendirme")
st.write("Nesne hatlarını çıkarır ve teknik çizim standartlarında boyut bilgilerini ekler.")

# 1. Kullanıcıdan Dosya Alımı 📥
uploaded_file = st.file_uploader("Bir resim seçin...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Orijinal Görüntü")
        st.image(image, use_container_width=True)

    if st.button('Teknik Çizimi ve Ölçüleri Oluştur'):
        with st.spinner('Hesaplanıyor...'):
            # --- ADIM 1: Görüntü İşleme ---
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (7, 7), 0)
            edged = cv2.Canny(blurred, 50, 150)
            
            # Konturları genişlet (çizgileri birleştirmek için)
            edged = cv2.dilate(edged, None, iterations=1)
            edged = cv2.erode(edged, None, iterations=1)

            # --- ADIM 2: Nesne Tespiti ve Boyutlandırma ---
            contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Beyaz arka planlı bir tuval oluştur (Teknik çizim kağıdı)
            h, w = gray.shape
            drawing_canvas = np.ones((h, w), dtype="uint8") * 255
            
            # Tüm kenarları siyah kalemle çiz
            cv2.drawContours(drawing_canvas, contours, -1, (0, 0, 0), 1)

            if contours:
                # En büyük konturu veya tüm nesneleri kapsayan alanı bulalım
                all_cnts = np.concatenate(contours)
                x, y, w_box, h_box = cv2.boundingRect(all_cnts)

                # --- ADIM 3: Teknik Çizim Standartlarında Ölçülendirme ---
                color = (100, 100, 100) # Gri tonlu ölçü çizgileri
                thickness = 1
                offset = 20 # Çizgilerin nesneden uzaklığı

                # Genişlik Çizgisi (Üstte)
                cv2.line(drawing_canvas, (x, y - offset), (x + w_box, y - offset), color, thickness)
                cv2.line(drawing_canvas, (x, y - offset - 5), (x, y - offset + 5), color, thickness)
                cv2.line(drawing_canvas, (x + w_box, y - offset - 5), (x + w_box, y - offset + 5), color, thickness)
                
                # Yükseklik Çizgisi (Solda)
                cv2.line(drawing_canvas, (x - offset, y), (x - offset, y + h_box), color, thickness)
                cv2.line(drawing_canvas, (x - offset - 5, y), (x - offset + 5, y), color, thickness)
                cv2.line(drawing_canvas, (x - offset - 5, y + h_box), (x - offset + 5, y + h_box), color, thickness)

                # Metin Yazdırma (Boyutlar)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(drawing_canvas, f"{w_box}px", (x + w_box//2 - 20, y - offset - 10), font, 0.5, (0,0,0), 1)
                cv2.putText(drawing_canvas, f"{h_box}px", (x - offset - 50, y + h_box//2), font, 0.5, (0,0,0), 1)

            with col2:
                st.subheader("Teknik Çizim Çıktısı")
                st.image(drawing_canvas, use_container_width=True)
                
                # İndirme Seçeneği
                result_img = Image.fromarray(drawing_canvas)
                st.success("Ölçülendirme tamamlandı!")
