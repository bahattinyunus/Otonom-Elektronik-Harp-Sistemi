# 📡 Otonom Elektronik Harp Sistemi (Cognitive-EW-Suite) v2.0

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![TEKNOFEST](https://img.shields.io/badge/TEKNOFEST-2026-red.svg)
![Status](https://img.shields.io/badge/deep--tech_sim-active-success.svg)
![AI Level](https://img.shields.io/badge/AI_Level-Cognitive_RL-orange.svg)

**Otonom Elektronik Harp Sistemi**, modern muharebe sahasındaki spektral karmaşayı yönetmek üzere tasarlanmış, yapay zeka (Reinforcement Learning) destekli, çok disiplinli bir Bilişsel Elektronik Harp (Cognitive EW) simülasyon ve komuta-kontrol mimarisidir. TEKNOFEST 2026 şartnameleri ve modern savaş doktrinleri (OODA Loop) temel alınarak geliştirilmiştir.

---

## 🏛️ Executive Summary (Teknik Özet)

Gelişen radar ve haberleşme teknolojileri, salt güç tabanlı "Brute-Force Jamming" (Kaba Kuvvet Karıştırma) yöntemlerini işlevsiz kılmaktadır. Bu proje; klasik EH sistemlerinin ötesine geçerek, spektrumu bir "canlı" gibi dinleyen, hedeflerin kaçış paternlerini öğrenen ve otonom tepki veren **Bilişsel (Cognitive)** bir yaklaşım sunar.

Sistem, insan müdahalesi olmadan şu döngüyü (OODA Loop) otonom olarak işletir:
1.  **Gözlem (Observe):** SDR (Yazılım Tanımlı Radyo) simülasyonu üzerinden IQ/PSD verisinin gerçek zamanlı toplanması ve şelale (waterfall) analizi.
2.  **Yönelim (Orient):** Spektrumdaki anomalilerin tespiti, sezgisel algoritmalarla modülasyon sınıflandırması ve **TDOA** (Time Difference of Arrival) tabanlı yön (AoA) kestirimi.
3.  **Karar (Decide):** **Q-Learning** (Pekiştirmeli Öğrenme) ajanı aracılığıyla, hedefin davranışlarına (Frekans Atlama vb.) göre en etkili Elektronik Taarruz (ET) zamanlamasının seçilmesi.
4.  **Eylem (Act):** Hedef üzerinde **Look-Through (Ara Bakış)** protokolü ile karıştırma uygulanması ve sonucun ödül/ceza (Reward) mekanizması ile değerlendirilmesi.

---

## 🏗️ Derinlemesine Teknik Mimari (v2.0 Güncellemeleri)

### 1. 🌊 Dinamik RF Ortam Simülasyonu (`sim/rf_environment.py`)
Sistem sadece statik spektrum verisi üretmekle kalmaz, modern LPI (Düşük Yakalanma Olasılığı) taktiklerini de simüle eder:
- **Frequency Hopping (Frekans Atlama):** Düşman hedeflerin izlenmesini zorlaştırmak için hedefler spektrum üzerinde anlık rastgele frekans değişimleri (hop) yaparlar.
- **Atmospheric Fading (Genlik Titreşimi):** Sinyal genliklerine zaman ve faz tabanlı sinüsoidal (Jitter) bozulumlar uygulanarak multipath (çoklu yol) etkileri simüle edilir.

### 2. 🧠 Q-Learning Tabanlı Look-Through Optimizasyonu (`modules/optimizer/`)
Sistem karıştırma (Jamming) yaparken "Körleşme" (kendi sinyalimizden dolayı hedefin görülmemesi) sorununu çözmek için Look-Through (Ara Bakış) uygular. 
- **RL Ajanı (Q-Learning):** Sistem, uyguladığı taarruzun hedefin spektrumdaki sayısını veya gücünü azaltıp azaltmadığını ölçer. Hedef kaybedilirse veya bastırılırsa yapay zekaya **Pozitif Ödül (+10)**, boş spektruma taarruz edilirse **Negatif Ceza (-5)** verilir. 
- **Otonom Adaptasyon:** Bu sayede sistem, $T_{jam}$ (Karıştırma) ve $T_{look}$ (Dinleme) sürelerini dinamik olarak öğrenme eğilimindedir.

### 3. 🎯 Sezgisel Analiz ve TDOA Yön Kestirimi (`modules/`)
- **Heuristic Classifier:** Klasik ezberlerin yerine sinyalin **Bant Genişliği (BW)** ve **Sinyal-Gürültü Oranına (SNR)** bakılarak sahte bir karar ağacı (Decision Tree mock) oluşturulur. Geniş bantlı güçlü sinyaller `16QAM`, dar bantlılar `AM/BPSK` olarak etiketlenir.
- **TDOA (AoA) Radar Algoritması:** Sinyalin merkez frekans vektörleri üzerinden, mikrofon dizilimi (Antenna Array) faz farkı/varış zamanı farkı benzetimi yapılarak sinyalin geliş açısı (0-360 derece) kesinliğe yakın, ancak termal gürültülü (Gaussian Noise) şekilde hesaplanır.

### 4. 📊 Siber-Komuta (Deep-Tech) Arayüzü (`ui/`)
Operatöre nihai taktiksel farkındalık sağlayan, Chart.js ve HTML5 Canvas destekli WebSocket arayüzü:
- **Real-Time Waterfall:** Saniyede 10 kare (100ms) hızında güncellenen piksel bazlı RF güç yoğunluğu haritası.
- **TDOA Polar Radar:** Geliş açılarını (AoA) 8 yönlü (N, NE, E vb.) bir gül diyagramında güce (SNR) orantılı olarak çizen interaktif savaş radarı.
- **Q-Learning Reward Grafiği:** Karıştırma ajanının anlık taarruz başarısını çizen veri grafiği.
- **Tasarım Dili:** TRL-8 (Teknoloji Hazırlık Seviyesi) standartlarına uygun siber-punk, neon tarama çizgili (scan-line) karanlık komuta merkezi estetiği.

---

## 🛠️ Kurulum, Gereksinimler ve Çalıştırma

### Bağımlılıklar
Proje, yoğun veri işleme (DSP) ve canlı veri akışı için aşağıdaki kütüphaneleri kullanır:
- `numpy`, `scipy`, `matplotlib` (Matematik ve Sinyal İşleme)
- `flask`, `flask-socketio`, `eventlet` (Asenkron Web Sunucusu)
- `opencv-python`, `torch` (Gelecek Vizyonu / Görüntü İşleme ve ML)

### Hızlı Kurulum
Tüm gereksinimleri kurmak ve sistemi başlatmak için terminalinizde aşağıdaki adımları sırasıyla uygulayın:

```bash
# 1. Gerekli kütüphaneleri indirin
pip install -r requirements.txt eventlet

# 2. Ana sistemi (Backend + UI) başlatın
python main.py
```

Sistem terminalde `Starting Otonom-EH Dashboard at http://localhost:5000` mesajı verdiğinde tarayıcınızdan komuta arayüzüne giriş yapabilirsiniz.

---

## 🚀 Gelecek Vizyonu (TRL-9 ve Üzeri)
Mevcut v2.0 sürümü bir "Dijital İkiz" (Digital Twin) ve karar-destek simülasyonudur. Projenin nihai hedefi, **GNU Radio** veya **UHD (USRP Hardware Driver)** arayüzleri üzerinden gerçek HackRF/USRP analog radyolarına bağlanıp gerçek zamanlı spektrumda "Otonom Yapay Zeka EH Subayı" olarak sahada bizzat görev almasıdır.