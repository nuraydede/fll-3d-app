import streamlit as st
import cv2
import numpy as np
from PIL import Image

# Başlık ve Açıklama 📝
st.title("🏛️ Arkeolojik Teknik Çizim Oluşturucu")
st.write("Görüntüdeki nesnelerin hatlarını çıkararak teknik çizim üretir.")

# 1. Kullanıcıdan Dosya Alımı 📥
uploaded_file = st.file_uploader("Bir resim seçin...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Resmi PIL ile açıp OpenCV formatına (numpy) çevirelim
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    
    # OpenCV RGB değil BGR bekler, ama biz çizim için gri ton kullanacağız
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # Yan yana iki sütun oluşturalım ↔️
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Orijinal Görüntü")
        st.image(image, use_container_width=True)

    # 2. Teknik Çizim İşlemi 🎨
    # 'Çizimi Üret' butonuna basılınca çalışır
    if st.button('Teknik Çizimi Oluştur'):
        with st.spinner('Çizgi hatları çıkarılıyor...'):
            # Gri tonlama
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # Gürültü engelleme (Gaussian Blur)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Kenar tespiti (Canny)
            edges = cv2.Canny(blurred, 50, 150)
            
            # Teknik çizim tuvali (siyah arka plan üzerine beyaz çizgiler)
            # İsterseniz bunu tam tersi yapabiliriz (beyaz kağıda siyah kalem)
            drawing = cv2.bitwise_not(edges) 

            with col2:
                st.subheader("Üretilen Teknik Çizim")
                st.image(drawing, use_container_width=True)
                st.success("Çizim başarıyla oluşturuldu!")
