# 📡 Otonom Elektronik Harp Sistemi (Cognitive-EW-Suite)

![Version](https://img.shields.io/badge/version-1.5.0-blue.svg)
![TEKNOFEST](https://img.shields.io/badge/TEKNOFEST-2026-red.svg)
![Status](https://img.shields.io/badge/deep--tech_sim-active-success.svg)

**Otonom Elektronik Harp Sistemi**, TEKNOFEST 2026 Elektronik Harp (EH) Yarışması şartnamesine uygun olarak geliştirilmiş, yapay zeka destekli, çok disiplinli bir Bilişsel Elektronik Harp (Cognitive EW) mimarisidir.

---

## 🏛️ Executive Summary (Teknik Özet)

Modern muharebe sahasında RF spektrumu, statik bir ortamdan ziyade dinamik ve sürekli değişen bir mücadele alanıdır. Bu proje; klasik EH sistemlerinin ötesine geçerek, **Bilişsel (Cognitive)** bir yaklaşımla spektrumu bir "canlı" gibi dinler, öğrenir ve tepki verir.

Sistem, insan müdahalesi olmadan şu döngüyü (OODA Loop) otonom olarak işletir:
1.  **Gözlem:** SDR üzerinden IQ verisinin gerçek zamanlı toplanması ve FFT analizi.
2.  **Yönelim:** Sinyal tespiti ve modülasyon sınıflandırması yoluyla tehdit kütüphanesi ile eşleştirme.
3.  **Karar:** Pekiştirmeli Öğrenme (Reinforcement Learning) ajanları ile en etkili ET (Elektronik Taarruz) tekniğinin seçilmesi.
4.  **Eylem:** FPGA/SDR tabanlı Look-Through (Ara Bakış) protokolü ile hedefi etkisiz hale getirme.

---

## 🏗️ Derinlemesine Teknik Mimari

### 1. 🌊 Gelişmiş RF Simülasyonu (`sim/rf_environment.py`)
Klasik simülasyonların aksine, sistemimiz **Frequency Hopping (Frekans Atlamalı)** ve **Atmospheric Fading (Genlik Titreşimi)** etkilerini modeller. 
- **Matematiksel Model:** Sinyaller, Gaussian dağılımı üzerine binmiş rastgele Jitter ve termal gürültü ile spektruma enjekte edilir.
- **Hızlı Frekans Atlama:** LPI (Düşük Yakalanma Olasılığı) radarlarını taklit eden anlık frekans değişimleri simüle edilir.

### 2. 🧠 Bilişsel Karar Mekanizması & Look-Through (`modules/optimizer/`)
Elektronik Taarruz (ET) esnasında spektrumu körleşmeden takip edebilmek için **"Look-Through"** tekniği kullanılır.
- **Döngü Mantığı:** Sistem $T_{jam}$ süresi boyunca hedefe karıştırma uygular, ardından mikro-saniyeler mertebesinde ($T_{look}$) karıştırmayı durdurup hedefteki değişiklikleri (frekans değişimi, kapanma vb.) analiz eder.
- **Optimizasyon:** Bu süreç, `SmartOptimizer` sınıfı tarafından zaman tabanlı bir otonom döngü ile yönetilir.

### 3. 🎯 Sinyal Analiz ve Konum Belirleme (`modules/`)
- **Waterfall Detector:** Bilgisayarlı görü (CV) teknikleri ile spektrogram üzerindeki anomalileri (sinyalleri) tespit eder.
- **AI Classifier:** CNN (Convolutional Neural Networks) mimarisi kullanılarak RF imzalarından sınıflandırma yapar.
- **Direction Finder:** TDOA (Time Difference of Arrival) ve Faz Farkı algoritmaları ile hedefin geliş açısını (AoA) matematiksel olarak kestirir.

### 4. 📊 Komuta Kontrol Arayüzü (`ui/`)
Operatöre taktiksel farkındalık sağlamak amacıyla geliştirilen dashboard:
- **Real-Time Streaming:** Flask-SocketIO üzerinden backend verileri 100ms gecikme ile arayüze basılır.
- **Dynamic Heatmap:** HTML5 Canvas API ile piksel bazlı güç yoğunluğu haritası oluşturulur.
- **Jamming Feedback:** Sistem karıştırma durumuna geçtiğinde, spektrum üzerindeki yapay gürültü girişi görsel olarak simüle edilir.

---

## 🛠️ Kurulum ve Kullanım

### Gereksinimler
- Python 3.10+
- Flask, Flask-SocketIO, Eventlet, NumPy, SciPy

### Çalıştırma
1. Bağımlılıkları kurun: `pip install -r requirements.txt`
2. Ana sunucuyu başlatın: `python main.py`
3. Tarayıcıda açın: `http://localhost:5000`

---

## 🚀 Gelecek Vizyonu
Bu proje, sadece bir simülasyon değil; ilerleyen aşamalarda **GNU Radio** ve **UHD** kütüphaneleri üzerinden gerçek USRP/HackRF donanımlarına entegre edilecek bir iskelettir. Nihai hedef, sahada otonom kararlar verebilen bir "Yapay Zeka EH Subayı" oluşturmaktır.