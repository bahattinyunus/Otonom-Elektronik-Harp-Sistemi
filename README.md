# 📡 Otonom Elektronik Harp Sistemi (Cognitive-EW-Suite) v3.0

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![TEKNOFEST](https://img.shields.io/badge/TEKNOFEST-2026-red.svg)
![Status](https://img.shields.io/badge/deep--tech_sim-active-success.svg)
![AI Level](https://img.shields.io/badge/AI_Level-Cognitive_RL_%2B_MLP-orange.svg)

**Otonom Elektronik Harp Sistemi**, modern muharebe sahasındaki spektral karmaşayı yönetmek üzere tasarlanmış, yapay zeka (Reinforcement Learning & PyTorch MLP) ve bilgisayarlı görü (OpenCV) destekli, çok disiplinli bir Bilişsel Elektronik Harp (Cognitive EW) simülasyon ve komuta-kontrol mimarisidir. TEKNOFEST 2026 şartnameleri ve modern Savaş Doktrinleri temel alınarak geliştirilmiştir.

---

## 🏛️ Executive Summary (Teknik Özet)

Gelişen radar ve haberleşme teknolojileri, salt güç tabanlı "Brute-Force Jamming" (Kaba Kuvvet Karıştırma) yöntemlerini işlevsiz kılmaktadır. LPI (Düşük Yakalanma Olasılığı) taktikleri kullanan, frekans atlayan ve genlik titreşimi (Fading) gösteren hedeflere karşı sistemimiz; klasik EH sistemlerinin ötesine geçerek spektrumu bir "canlı" gibi dinler, hedeflerin kaçış paternlerini öğrenir ve otonom tepki veren **Bilişsel (Cognitive)** bir yaklaşım sunar.

Sistem OODA (Observe, Orient, Decide, Act) döngüsünü milisaniyeler içerisinde işletir:
1.  **Gözlem (Observe):** SDR (Yazılım Tanımlı Radyo) tabanlı IQ/PSD (Güç Spektral Yoğunluk) verisinin 1024-bin FFT analizi.
2.  **Yönelim (Orient):** Spektrumdaki hedeflerin **OpenCV 2D Contour** tespiti, **PyTorch MLP** ile modülasyon sınıflandırması ve **TDOA** (Time Difference of Arrival) ile matematiksel yön (AoA) kestirimi.
3.  **Karar (Decide):** **Q-Learning** ajanı ile hedefin adaptif davranışına (Frekans Atlama) göre karıştırma (Jamming) ve dinleme (Look-Through) periyotlarının otonom planlanması.
4.  **Eylem (Act) & Öğrenme:** Hedefe taarruz uygulanıp, sonucun başarılı olup olmadığına (hedefin düşürülüp düşürülmediğine) bakılarak veri tabanına (**SQLite Blackbox**) ödül (reward) veya ceza (penalty) olarak kaydedilmesi.

---

## 🏗️ Derinlemesine Teknik Mimari ve Teorik Altyapı

Sistem v3.0 sürümü itibarıyla, tamamen otonom yapay zeka algoritmaları, sinyal işleme matematiği ve manuel müdahale mekanizmaları etrafında şekillenmiştir. Aşağıda çekirdek modüllerin teknik çalışma prensipleri detaylandırılmıştır.

### 1. 🌊 Dinamik RF Dinamikleri ve Sinyal Yayılım Fiziği (`sim/rf_environment.py`)
RF (Radyo Frekans) dalgalarının atmosferdeki fiziksel doğası simüle edilir. 
- **Frequency Hopping (Frekans Atlama):** Spread-spectrum (yayılı spektrum) veya LPI sinyalleri gibi, hedeflerimiz %30 ihtimalle saniyede birkaç kez Merkez Frekanslarını (Center Frequency $f_c$) $\pm 40\%$ oranında rastgele atlatarak izlenmeyi zorlaştırır.
- **Atmospheric Fading (Genlik Titreşimi):** Multipath (çoklu yol) solmalarını taklit etmek adına, sinyal genliklerine ($A$) zamana ve faza bağlı sönümlenmeler eklenir:
  $$ A(t) = A_{base} \cdot (1 + 0.2 \cdot \sin(10t + \phi_{offset})) $$
  Bu matematiksel model, sinyalin spektrum üzerinde bir yanıp bir sönmesine yol açar.

### 2. 👁️ OpenCV Tabanlı 2B Spektrum Tespiti (`modules/detector/detector.py`)
Sistemin gözü işlevi gören bu modül, yalnızca 1 boyutlu frekans eşik değerlerine (Threshold) bakmaz (Klasik yaklaşım); spektrumun son saniyelerindeki zaman serisini 2 Boyutlu bir matris (Resim dosyası formatı) olarak havuzlar.
- **Grayscale Dönüşüm:** PSD (Gürültü tabanı ve Sinyal Gücü) geçmiş matrisini $0-255$ arası bir `uint8` renk uzayına normalize eder.
- **Canny Edge & Contours:** `cv2.threshold` ve `cv2.findContours` fonksiyonlarıyla ardışık spektrum kareleri tıpkı bir udu/radar ekranı gibi değerlendirilip "sinyal adacıkları" (bloblar) tespit edilir. Bu sayede frekansı kayan, genişleyip daralan sinyaller bile "bağlı bileşen" (Connected Component) toleranslarıyla yakalanır.

### 3. 🧠 PyTorch Kestirim Ağı ve Forward-Pass (`modules/classifier/classifier.py`)
Hedefin ne tür bir yayın (Modülasyon) yaptığını anlama işi **PyTorch** mimarisi kullanılarak inşa edilmiş bir **Çok Katmanlı Algılayıcı (MLP - Multi-Layer Perceptron)** ile gerçekleştirilir.
- **Ağ Yapısı:** `Linear(2, 16) -> ReLU -> Linear(16,8) -> ReLU -> Linear(8, Classes)`. Sinyalin Çıkarılmış SNR (Sinyal/Gürültü Oranı) ve Bant Genişliği (BW) normalleştirilmiş tensör matrislerine (`torch.tensor`) dönüştürülüp yapay sinir ağına (`model(x)`) sokulur. 
- **Bilişsel Çıkarım:** Klasik IF-THEN kod blokları yerine, sinir ağının matematik ağırlıklarına dayalı sınıflandırma yapılarak BPSK, QPSK, 16QAM, AM, FM veya LoRa etiketleri atanır (Örn: Cihaz çok geniş bantlı (Wideband) bir tespit yaparsa onu AM yerine LoRa'ya etiketlemeye zorlayan taktik override'lara da sahiptir).

### 4. 🧭 TDOA Yön Bulucu Fiziği (`modules/direction_finder/df_logic.py`)
Sinyalin geliş açısının (AoA - Angle of Arrival) tespiti, pasif sensörlerin en kritik işlevidir. Modülümüz, donanımsal anten gecikmelerini sembolize eden *Time Difference of Arrival (TDOA)* matematiğini referans alır.
- Sinyalin taşıyıcı frekansına (Center Index) bağımlı faz farkları matematiksel olarak çözümlenir (Altın oran $137.5$ derece dağılım baz alınır).
- Radar benzeri gerçeklik sağlamak için tespit açısının üzerine $\mu=0, \sigma=2.0$ olan Gaussian White Noise (Beyaz Gürültü) eklenir. Böylelikle statik bir hedefin yayın açısı sürekli $142.0^\circ$ değil, $[140.7^\circ, 143.1^\circ]$ bandında doğal bir titreşim aralığına oturur.

### 5. 🤖 Q-Learning (RL) Tabanlı ET Optimizasyonu (`modules/optimizer/et_optimizer.py`)
Elektronik Taarruz (ET) esnasında spektrumu körleşmeden takip edebilmek için "Look-Through" moduna ihtiyaç vardır. Ancak ne kadar süre karıştırma, ne kadar süre sessizlik/dinleme yapılacağı yapay zeka tarafından belirlenir:
- **Reward (Ödül) Modeli:** Karıştırmaya (Jamming) başlandığında, şelale analizinde tespit edilen hedeflerin *sayısı düşerse*, bu durum karıştırmanın başarılı olduğu anlamına gelir ve ajana $(+10)$ puan yazılır. Hedef sayısı değişmez veya karıştırma enerjisi boşa harcanırsa ajan $(-2)$ veya $(-5)$ gibi negatıf puanlarla cezalandırılır.
- **Davranış:** Q-Ödül geçmişi sistemde tutuldukça, Ajan başarısız politikalardan kaçınıp, doğrudan hedefi bastırabilecek optimum "Taarruz / Standby" vuruş oranını (Duty Cycle) bulmaya yaklaşır.

### 6. 🗄️ Taktiksel Kara Kutu - Blackbox (`core/blackbox.py`)
Uçuş Görev Veri Kaydedicisi (FDR) misali, sistemin saniyede onlarca kez aldığı tüm tespit (Signals) ve karar (Actions) çıktıları güvenli bir şekilde `sqlite3` tabanlı `logs/mission_log.db` veritabanına asenkron olarak kaydedilir. 
- Bu veritabanı, operasyon sonrası veri analizi (AAR - After Action Report) için yapılandırılmıştır. "Hangi saniyede sistem hedefi FM sınıflandırdı ve saat kaçta Jamming açıldı?" soruları SQL sorgularıyla %100 izlenebilir hale gelmiştir. 

---

## 💻 Komuta Merkezi Arayüzü (Operator Deck UI)
Arayüz, sadece bir gösterge paneli olmaktan çıkarılarak "Etkileşimli (Interactive) Komuta Merkezi"ne dönüştürülmüştür.
- **WebSocket Veri Yolu:** Flask-SocketIO mimarisi sayesinde backend'den alınan PSD matrisleri, 100ms lik asenkron periyotlarla tarayıcı `Canvas API` sine yazdırılarak gerçek zamanlı bir SDR ekranı oluşturur.
- **Radar & Q-Chart:** `Chart.js` kullanılarak, TDOA açılarını güce (SNR) göre kutupsal çizen Polar Gülgoncası (Rose/Radar) haritası ve RL Ajanının kazanım/kayıplarını çizen Dinamik Çizgi Grafiği eklenmiştir.
- **Manuel Kontrol Müdahalesi (Override):** Operatör dilerse sağ konsoldaki `SİSTEM MODU` üzerinden "Otonom (AI)" kontrolü devre dışı bırakıp "MANUEL"e geçebilir; arayüz üzerinden Karıştırma (Jamming) tuşunu basılı tutabilir ve çevre gürültü seviyesini (Noise Floor) $(-120dB)$ ile $(-40dB)$ arası dinamik olarak manipüle edebilir. 
- Arayüz renkleri, siber-punk scanline (tarama çizgileri) animasyonları ile derin mavi ve kontrast $Cyan/Red$ (Neon) TRL-8 standartlarına bürünmüştür.

---

## 🛠️ Kurulum, Gereksinimler ve Çalıştırma

### Bağımlılıklar
- `numpy`, `scipy`, `matplotlib`
- `flask`, `flask-socketio`, `eventlet`
- `opencv-python` (`cv2`)
- `torch` (PyTorch)

### Hızlı Kurulum

```bash
# 1. Gerekli kütüphaneleri indirin
pip install -r requirements.txt eventlet

# 2. Ana sistemi (Backend + UI) başlatın
python main.py
```

Sistem terminalde `Starting Otonom-EH Dashboard at http://localhost:5000` mesajı verdiğinde tarayıcınızdan komuta arayüzüne giriş yapabilirsiniz.

---

## 🚀 Üstünlük ve Vizyon
Bu repo salt kodlama egzersizi değil, "Spektrum Yönetiminin Matematik ve Yapay Zekayla Nasıl Evrilebileceği" sorusuna cevap veren kapsamlı bir Bilişsel Elektronik Harp Bütünleşik Çözümü'dür. Gerçek radyolara (USRP/HackRF) entegre edilebilir asenkron ve modüler iskeleti ile geleceğin insansız muharebe sistemlerinin beyin modülü olmaya adaydır.