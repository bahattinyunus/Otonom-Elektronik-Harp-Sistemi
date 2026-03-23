# 📡 Otonom Elektronik Harp Sistemi (Cognitive-EW-Suite) v9.0

![Otonom EW Suite Banner](banner.png)

![Version](https://img.shields.io/badge/version-9.0.0-gold.svg)
![TEKNOFEST](https://img.shields.io/badge/TEKNOFEST-2026-red.svg)
![Status](https://img.shields.io/badge/TRL-10.0-success.svg)
![AI Level](https://img.shields.io/badge/Cognitive_AI-Protection_&_Intelligence-gold.svg)

**Otonom Elektronik Harp Sistemi (Cognitive-EW-Suite)**, modern elektronik harp (EH) ve elektromanyetik spektrum operasyonlarında (EMSO) Derin Öğrenme (Deep Learning) ve Pekiştirmeli Öğrenme (Reinforcement Learning) metodolojilerini spektral analiz süreçlerine entegre eden otonom bir Bilişsel Elektronik Harp (Cognitive EW) platformudur.

### 🏭 SDR Hardware Abstraction Layer (HAL) - [v0.4]
Sistem, donanım bağımsızlığı (HW Agnostic) vizyonuyla yeniden mimarize edilmiştir. `SDRInterface` soyutlama katmanı sayesinde; RTLSDR, HackRF, USRP veya simüle edilmiş bir `RFEnvironment` arasında geçiş yapmak sadece bir konfigürasyon değişikliği (`config.py`) kadar kolaydır. Bu, saha operasyonlarında farklı sensör setlerinin "Tak-Çalıştır" mantığıyla sisteme dahil edilmesini sağlar.

### 📡 CA-CFAR: Dinamik Eşikleme ve Gürültü Adaptasyonu - [v0.6]
Klasik sistemlerin aksine, bu suite spektrumu sabit bir eşik (Threshold) ile taramaz. **CA-CFAR (Cell Averaging Constant False Alarm Rate)** algoritması ile:
- Her bin için çevre (Training) hücrelerin gürültü ortalaması alınır.
- Sinyal sızıntısını önleyen Koruma (Guard) hücreleri ile net SNR ölçümü yapılır.
- Sistem, karıştırma (Jamming) altında dahi otonom olarak gürültü zeminini takip eder ve duyarlılığını buna göre ayarlar.

---

## 🏛️ Yönetici Özeti: Elektronik Harpte Yapay Zeka Paradigması

Gelişen LPI (Low Probability of Intercept) radarları, yazılım tanımlı radyolar (SDR) ve bilişsel frekans atlamalı (Frequency Hopping) haberleşme dalga şekilleri, eylemsiz, donanım-sabiti, kural tabanlı (Rule-Based) karıştırma (Jamming) ve aldatma (Spoofing) tekniklerini asimetrik harekat ortamında zafiyete uğratmıştır. Düşman elektronik harp aygıtlarının spektrum üzerindeki kaçış, gizlenme ve adaptasyon paternlerini kestirebilmek için deterministik algoritmalar çökmüş; varyans analizi ile beslenen **Yapay Zeka (AI)** tabanlı karar-destek ve komuta kontrol (C2) sistemleri operasyonel bir zorunluluk haline gelmiştir.

Bu araştırma / prototip projesi, Elektronik Destek (ES) ile tespit edilen elektromanyetik vektörleri, Bilgisayarlı Görü (Computer Vision) ile spektral öznitelik haritalarına çevirmeyi, PyTorch Çok Katmanlı Algılayıcı (MLP) modülleriyle modülasyon tespiti yapmayı ve Markov Karar Süreçleri'ni (MDP) modelleyen Q-Learning ajanı vasıtasıyla Elektronik Taarruz (EA) "Look-Through" parametrelerini optimum efektif noktaya taşımayı, reaksiyon süresini $<100ms$ aralığına düşürerek hedefler.

---

## 🧠 Bilişsel Mimari ve Yapay Zeka Entegrasyonu

Sistem, elektromanyetik spektrumdaki sinyal tespiti, sınıflandırma ve taarruz optimizasyonu görevlerini birbirinden bağımsız çalışan, ancak eşgüdümlü karar alan üç ana AI/ML işlem bloğuna ayırmıştır:

### 1. Spektral Görü İşleme ve Anomali Tespiti (V4 Adaptive CV)
Klasik enerji tabanlı eşik (Threshold) tespiti yerine spektrum, 2 boyutlu bir zaman-frekans şelalesi (Waterfall Spectrogram) olarak analiz edilir. v4.0 ile birlikte dedektör çok daha robust hale getirilmiştir:
- **Adaptive Thresholding:** `cv2.adaptiveThreshold` kullanılarak yerel gürültü ortalamasına göre dinamik eşikleme yapılır. Bu sayede spektrumun farklı bölgelerindeki gürültü varyasyonlarından etkilenmez.
- **Morphological Closing:** Sönümlenmiş (faded) veya parçalı sinyal bloklarını `cv2.MORPH_CLOSE` ile birleştirerek tekil hedef sürekliliğini sağlar.
- **Sinyal Morfolojisi Analizi:** Sistem, `cv2.findContours` fonksiyonları kullanılarak atmosferik solma (Atmospheric Fading) ve çevresel gürültünün yarattığı dezenformasyon filtreleyerek sinyal adacıklarının (blobs) merkez frekansını, bant genişliğini ve SNR marjını otonom olarak hesaplar.

### 2. İleri Seviye RF Simülasyonu ve Karıştırma (V5 Deceptive EW)
Simülasyon ortamı, laboratuvar koşullarından gerçek harekat ortamına yaklaştırılmıştır:
- **FMCW (Chirp) Radarlar:** Frekansı zamanla doğrusal olarak değişen (LFM) radar sinyalleri simüle edilir.
- **Multipath Fading Model:** Sinyallerin yansıma ve faz farkı kaynaklı sönümlenmelerini (fading) simüle eden matematiksel model entegre edilmiştir.
- **DRFM (Digital Radio Frequency Memory) Jamming:** Tespit edilen aktif sinyallerin anlık frekans ve zaman kopyaları oluşturularak spektrumda aldatıcı "Ghost" (Hayalet) hedefler yaratılır.

### 3. Sürü Zekası ve HIL Telemetri (V7 Integration)
- **Collaborative Swarm Registry:** Çoklu düğüm operasyonları için "Dost/Paydaş" frekans planı ve RFI hash kayıt defteri entegre edilmiştir.
- **REST Telemetry API (v1):** Dış sistemler (SDR, Flight Controller) için gerçek zamanlı istihbarat ve taarruz verisi sunan standart JSON API endpoint'i (HIL Ready).
- **Interference Avoidance RL:** Reinforcement Learning ajanı, sürü üyelerinin haberleşme sağlığını bozmamak için dost frekanslardan kaçınma (de-confliction) mantığına kavuşturulmuştur.

### 4. Nöral Gürültü Temizleme ve Bilişsel Sentez (V8 Neural Fusion)
- **Neural Autoencoder Denoiser:** PSD verileri 1D-CNN Autoencoder üzerinden geçirilerek stokastik gürültüden arındırılır.
- **Cognitive Waveform Synthesis:** LPI (Düşük Yakalanma Olasılığı) sinyalleri ve aldatıcı "Phantom" hedefler spektrum üzerinde dinamik olarak sentezlenir.
- **UKF (Unscented Kalman Filter) Tracking:** Hedef takip algoritması, non-lineer manevraları yüksek hassasiyetle takip edebilen UKF mimarisine yükseltilmiştir.

### 5. Stratejik Otonomi ve Görev Durum Makinesi (v0.7 Mission Control)
Sistem, reaktif bir loop yerine artık proaktif bir **Mission State Machine** tarafından yönetilmektedir:
- **SCAN (Arama):** Enerji tasarruflu geniş bant tarama ve anomali keşfi.
- **TRACK (Kilitlenme):** Tehdidin özniteliklerini (Modülasyon, RFI Signature) çıkarma ve LSTM Predictor ile gelecek frekansını tahmin etme.
- **ENGAGE (Taarruz):** Pekiştirmeli öğrenme ajanı vasıtasıyla optimize edilmiş karıştırma sinyali uygulama.
- **EVALUATE (BDA - Hasar Tespit):** Angajman sonrası saniyeler içinde karıştırmayı durdurup hedefin etkisizleştiğini (Signal Kill) veya kaçtığını otonom olarak doğrulama.

---

### 🛡️ Bilişsel Korunma ve Operasyonel İstihbarat (V9 Protection & Intel)
- **Electronic Protection (EP) Agent:** Dost unsurları düşman karıştırmasından korumak için otonom frekans atlama (Frequency Hopping) rotaları oluşturan RL ajanı.
- **Mission Intelligence Analyzer:** Görev süresince toplanan büyük veriyi (Big Data) işleyerek EH operatörüne stratejik özetler sunan bilişsel raporlama ünitesi.
- **Spectral Security Index:** Spektrumun güvenilirlik ve kullanılabilirlik oranını anlık olarak hesaplayan yeni nesil metrik sistemi.

## 🧠 Bilişsel Yapay Zeka Mimarisi (Phase 3)

Sistem, basit kural tabanlı algoritmaların ötesine geçerek şu gelişmiş Derin Öğrenme (Deep Learning) bileşenlerini kullanır:

### 1. Derin LSTM Tabanlı Frekans Atlamalı Tahminleyici (Hop Predictor)
- **Modül:** `modules/predictor/hop_predictor.py`
- **Görev:** `QPSK` veya `Radar` gibi frekans atlamalı (FHSS) sinyallerin geçmiş verilerini analiz ederek bir sonraki frekans adımını (hop) yaklaşık **%85+ doğrulukla** tahmin eder.
- **Teknoloji:** PyTorch tabanlı Çok Katmanlı (Multi-Layer) Sequence-to-One LSTM Sinir Ağı (Dropout Entegrasyonlu).

### 2. Deep Q-Network (DQN) Electronic Attack (EA) Optimizer
- **Modül:** `modules/optimizer/et_optimizer.py`
- **Görev:** Sürekli değişen RF spektrum ortamını 4 boyutlu bir durum uzayı olarak alır, tehdit seviyesi ve AI tahmin isabetine göre en uygun jamming politikasını (Standby, Spot, Barrage, Look-Through, Deceptive Jam) otonom olarak seçer.
- **Teknoloji:** PyTorch tabanlı Deep Q-Network (DQN) mimarisi. Bellman denklemini iteratif olarak çözerek Epsilon-Greedy politikasıyla (Experience Replay Buffer kullanılarak) eğitilir.
- **Ödül Fonksiyonu:** Tahmin edilen frekansa yapılan başarılı taarruzlar için ekstra ödül (+25 pts) alarak "Anticipatory Jamming" yeteneğini geliştirir.

### 3. Bilişsel Analiz Dashboard
- **Görselleştirme:** Sinir ağlarının içsel durumunu ve gelecek tahminlerini canlı olarak raporlar.

### 2. PyTorch Tabanlı Derin Sınıflandırma Ağları (Deep Learning)
Tespit edilen bir sinyalin modülasyon tipini (BPSK, QPSK, 16QAM, FMCW, LoRa vb.) kestirmek için istatistiksel kurallar yerine **PyTorch** mimarisi kullanılarak Çok Katmanlı İleri Beslemeli Yapay Sinir Ağı (MLP - Multi-Layer Perceptron) devreye sokulur.
- **Tensör Ağ Yapısı:** Sinyalin bant genişliği (BW) ve sinyal-gürültü oranı (SNR) normalize edilmiş tensör girdileri olarak `Linear(2, 16) -> ReLU -> Linear(16,8) -> ReLU -> Linear(8, Classes)` zinciri boyunca ileri yönlü (Forward-Pass) işlenir.
- **Esnek Reaksiyon:** Ağ, klasik sistemlerin yanıldığı geniş bantlı ancak sönük (Faded) LPI sinyallerinin tanınmasında yüksek başarım göstermek üzere konfigüre edilmiştir.

### 3. Pekiştirmeli Öğrenme (Reinforcement Learning) ve Adaptif Elektronik Taarruz
Projenin temel otonomi unsuru olan Q-Learning adaptasyonu, Elektronik Destek (ED) ve Elektronik Taarruz (ET) arasındaki körleşmeyi (Blind-Spot) minimuma indirgemeyi hedefler. Algoritma "Ara Başık" (Look-Through) tekniğini optimize eder.
- **Dinamik Ödül/Ceza (Reward System):** ET (Karıştırma) esnasında ajan (Agent), uyguladığı taarruz sonrası spektrumdaki hedef sayısında bir düşüş algılarsa $(+10)$ ödül puanı alır. Hedefin gücü düşmezse, yani hedefin frekans atlatarak kaçtığı tespit edilirse ajan enerji israfı nedeniyle $(-5)$ puanlık ceza ile cezalandırılır.
- **Taarruz Kavraması:** Otonom ajan, zamanla hangi hedef profilinde ne kadar süre $T_{jam}$ (Karıştırma) ve $T_{look}$ (Dinleme) yapması gerektiğini öğrenerek "Optimum Duty Cycle" oranına yakınsar.

### 4. Bilişsel Sınıflandırma: Spektral Momentler ve Uzman Sistem (Expert System)
Sinyal tipi kestiriminde sadece ham güç değerleri değil, istatistiksel spektral momentler kullanılır:
- **Kurtosis (Basıklık):** Sinyalin impulsif yapısını (örn: Radar darbeleri) analiz eder.
- **Skewness (Çarpıklık):** Spektral asimetri üzerinden modülasyon saflığını ölçer.
- **Flatness (Düzlük):** Sinyalin bant genişliğindeki güç dağılımını (Gürültü vs. Geniş Bant Haberleşme) ayırt eder.

---

## 🧮 Alt Sistemler ve Taktik Destek Unsurları

### Zaman Farkı (TDOA) ile Otonom Yön Bulucu (DF)
Hedefin geliş açısı (Angle of Arrival - AoA), birden fazla karşılama anteni (Antenna Array) simülasyonu üzerinden, sinyallerin varış zamanı farkları (TDOA) ölçülerek hesaplanır. 
Gerçek bir savaş alanı simülasyonu sağlamak için hedefin bulunduğu ideal açı değerinin üzerine $\mu=0, \sigma=2.0$ varyansına sahip Gaussian White Noise (Beyaz Gürültü) eklenir. Sistem, Radar (Polar) ekranında bu bulanıklaşmış hedefe kilitlenme işlemi uygular.

### Taktik Görev Veri Kaydedicisi (SQLite Blackbox)
Sistemin sensörlerinin tespit ettiği her anomali ve RL Ajanının aldığı her karıştırma/bekleme (Jamming/Standby) kararı asenkron mimari ile `sqlite3` tabanlı `mission_log.db` görev bilgisayarına kaydedilir. Bu veritabanı, görevin sonlanmasının ardından EH subayları ve istihbarat birimleri tarafından Görev Sonu Kritik Analizi (AAR - After Action Report) için yapılandırılmıştır.

---

## 💻 Siber Operatör Komuta Merkezi (C2 Dashboard)
Salt otonom bir yapay zeka yerine "Human-on-the-loop" (İnsan Denetiminde Kontrol) felsefesi benimsenmiştir. Flask-SocketIO üzerinden beslenen ve saniyede 10 kare hızında akış sağlayan komuta arayüzü aşağıdaki modülleri içerir:

1.  **Dinamik Waterfall Spektrogrami:** HTML5 Canvas nesnesi ile `uint8` veri bloklarının 2 boyutlu Siber-Neon skalaya dönüştürülmüş anlık akışı.
2.  **TDOA Polar Savaş Radarı (Chart.js):** Sinyallerin AoA dağılımlarını Kutupsal (Polar) Gülgoncası haritası üzerinde görselleştirir.
3.  **Gerçek Zamanlı Q-Ödül Grafiği:** Ajanın o an uyguladığı karıştırma algoritmalarından sağladığı başarılı/başarısız geri bildirim döngüsünü zamana bağlı çizer.
4.  **Operatör Override (Müdahale) Paneli:** Kullanıcı, tek bir tıklamayla Otonom Yapay Zekayı devreden çıkarıp MANUEL yetkiyi alabilir; karıştırma görevlerini ve çevresel RF spektrum gürültü eşiğini (Noise Floor) $(-120dB)$ ila $(-40dB)$ arasında anlık tahsis edebilir.
5. **AAR Görev Raporu:** Her görevin ardından, "AAR RAPORUNU İNDİR" butonuyla tüm `Track_ID`, `RFI_Hash`, `AoA` logları CSV formatında anlık raporlanır.

---

## 🛠️ Teknik Gereksinimler ve Kurulum

Proje, Derin Öğrenme, Sinyal İşleme ve Asenkron Web Haberleşmesi kütüphanelerinin eşgüdümlü birleşimini gerektirmektedir.

```bash
# Gerekli Taktik Sinyal, ML ve Ağ Paketlerinin Kurulumu
pip install -r requirements.txt eventlet

# Bilişsel EH Karar ve Destek Sisteminin Başlatılması
python main.py
```

### 🐳 Docker ile Otonom Başlatma (Production-Ready)
Sistem tüm bağımlılıklarıyla birlikte sanallaştırılmıştır. Kapsayıcıyı derleyip ayağa kaldırmak için:
```bash
docker-compose up --build -d
```

Sistem başlatıldığında `http://localhost:5000` adresinden TCP/WS tabanlı Komuta Kontrol Enstrüman Panelinize erişebilirsiniz.
Ağ analizi tamamlandıktan sonra operatör arayüzünden Görev Sonu Raporunu (AAR CSV) tek tıkla çekebilirsiniz.

---

## 🎓 Bilişsel EH Akademisi: Derinlemesine Teknik Kavramlar

Sistemin çalışma prensiplerini daha iyi anlamak için temel alınan bazı ileri seviye kavramlar aşağıda açıklanmıştır:

### 1. Spektral Momentler Neden Önemli?
Bir sinyalin sadece gücüne (Power) bakmak, onun kimliğini belirlemek için yetersizdir.
- **Kurtosis (Basıklık):** Gaussian (Normal) gürültünün basıklığı 3'tür. Eğer bu değer 10-20 seviyelerine çıkıyorsa, spektrumda "Darbeli" (Impulsive) bir yapı (örn: LPI Radar) olduğu kesinleşir.
- **Skewness (Çarpıklık):** Sinyalin merkez frekansa göre ne kadar asimetrik olduğunu ölçer. Tek yan bantlı (SSB) veya frekans kayması olan sinyalleri yakalamada kritiktir.

### 2. OODA Döngüsü Otomasyonu
Hızlı bir EH operasyonu için **Gözlem -> Yönelim -> Karar -> Eylem** döngüsünün insan gecikmesinden (~200-500ms) kurtulması gerekir.
- Bu suite, OODA döngüsünü tamamen RAM üzerinde, asenkron `MissionStateMachine` ile yöneterek bu süreyi **<50ms** seviyesine çeker. 
- Bu, saniyede 1000 defa sekerek kaçmaya çalışan (Fast Hopping) bir telsizi dahi "Takipte" tutabilmeyi sağlar.

### 3. CFAR Algoritması: Neden Sabit Eşik Kullanmıyoruz?
Eğer eşik sabitse, düşman spektruma gürültü (Noise Jamming) bastığında sistem her şeyi "Sinyal" zanneder veya hiçbir şeyi göremez. 
**CA-CFAR**, her frekans hücresi için "Gürültü Nedir?" sorusunu o anda cevaplar. Bu, dinamik bir koruma kalkanıdır.

---

## 🚀 Akademik Vizyon ve Nihai Otonomi
Bu proje, salt bir yazılım mimarisi değil, elektromanyetik spektrumda hayatta kalmanın sadece "Daha akıllı algoritmalarla" mümkün olacağını gösteren akademik bir vizyondur. İnsansız Hava Araçları (İHA) ve Otonom Kara Araçları (İKA) için GNU Radio / UHD (USRP Hardware Driver) uyumluluğu gözetilerek yazılmış bu iskelet, modüler yapısı sayesinde gerçek donanımlarla bir "Otonom Elektronik Harp Subayı" olarak işlev görme nihai hedefine (TRL-9) adaydır.