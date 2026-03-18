# 📡 Otonom Elektronik Harp Sistemi (Cognitive-EW-Suite) v3.0

![Otonom EW Suite Banner](banner.png)

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![TEKNOFEST](https://img.shields.io/badge/TEKNOFEST-2026-red.svg)
![Status](https://img.shields.io/badge/TRL-8-success.svg)
![AI Level](https://img.shields.io/badge/Cognitive_AI-Deep_Learning_%26_RL-orange.svg)

**Otonom Elektronik Harp Sistemi (Cognitive-EW-Suite)**, modern elektronik harp (EH) ve elektromanyetik spektrum operasyonlarında (EMSO) yapay zeka (AI) ve makine öğrenimi (ML) tekniklerini otonom karar mekanizmalarıyla birleştiren yeni nesil bir Bilişsel Elektronik Harp (Cognitive Electronic Warfare) platformudur.

Bu platform, statik tehdit kütüphanelerine (Emitter Threat Library) dayalı klasik EH sistemlerinin aksine; spektral ortamdaki fiziksel değişimleri dinamik olarak algılayabilen, öğrenebilen ve adaptif taarruz/savunma örüntüleri üretebilen otonom bir mimari sunmaktadır.

---

## 🏛️ Yönetici Özeti: Elektronik Harpte Yapay Zeka Paradigması

Gelişen LPI (Low Probability of Intercept) radarları, yazılım tanımlı radyolar (SDR) ve bilişsel frekans atlamalı (Frequency Hopping) haberleşme sistemleri, lineer ve kural tabanlı (Rule-Based) karıştırma (Jamming) tekniklerini işlevsiz hale getirmiştir. Bu bağlamda, düşmanın spektrumdaki kaçış ve adaptasyon paternlerini gerçek zamanlı olarak çözümleyebilmek için **Yapay Zeka (AI)** tabanlı sistemler artık bir tercih değil, zorunluluktur.

Bu proje, bir EH platformunun OODA (Gözlem, Yönelim, Karar, Eylem) döngüsünün her bir aşamasına yapay zeka ve ileri bilgisayarlı görü (Computer Vision) entegre ederek reaksiyon süresini insan kapasitesinin ötesine ($<100ms$) taşımayı hedefler.

---

## 🧠 Bilişsel Mimari ve Yapay Zeka Entegrasyonu

Sistem, elektromanyetik spektrumdaki sinyal tespiti, sınıflandırma ve taarruz optimizasyonu görevlerini birbirinden bağımsız çalışan, ancak eşgüdümlü karar alan üç ana AI/ML işlem bloğuna ayırmıştır:

### 1. Spektral Görü İşleme ve Anomali Tespiti (Computer Vision)
Klasik enerji tabanlı eşik (Threshold) tespiti yerine spektrum, 2 boyutlu bir zaman-frekans şelalesi (Waterfall Spectrogram) olarak analiz edilir.
- **OpenCV & Canny Edge Algoritmaları:** SDR modülünden akan PSD (Power Spectral Density) verileri `uint8` gri tonlamalı imaj matrislerine dönüştürülür.
- **Sinyal Morfolojisi Analizi:** Sistem, `cv2.findContours` fonksiyonları kullanılarak atmosferik solma (Atmospheric Fading) ve çevresel gürültünün yarattığı dezenformasyon filtreleyerek sinyal adacıklarının (blobs) merkez frekansını, bant genişliğini ve SNR marjını otonom olarak hesaplar.

### 2. PyTorch Tabanlı Derin Sınıflandırma Ağları (Deep Learning)
Tespit edilen bir sinyalin modülasyon tipini (BPSK, QPSK, 16QAM, FMCW, LoRa vb.) kestirmek için istatistiksel kurallar yerine **PyTorch** mimarisi kullanılarak Çok Katmanlı İleri Beslemeli Yapay Sinir Ağı (MLP - Multi-Layer Perceptron) devreye sokulur.
- **Tensör Ağ Yapısı:** Sinyalin bant genişliği (BW) ve sinyal-gürültü oranı (SNR) normalize edilmiş tensör girdileri olarak `Linear(2, 16) -> ReLU -> Linear(16,8) -> ReLU -> Linear(8, Classes)` zinciri boyunca ileri yönlü (Forward-Pass) işlenir.
- **Esnek Reaksiyon:** Ağ, klasik sistemlerin yanıldığı geniş bantlı ancak sönük (Faded) LPI sinyallerinin tanınmasında yüksek başarım göstermek üzere konfigüre edilmiştir.

### 3. Pekiştirmeli Öğrenme (Reinforcement Learning) ve Adaptif Elektronik Taarruz
Projenin temel otonomi unsuru olan Q-Learning adaptasyonu, Elektronik Destek (ED) ve Elektronik Taarruz (ET) arasındaki körleşmeyi (Blind-Spot) minimuma indirgemeyi hedefler. Algoritma "Ara Başık" (Look-Through) tekniğini optimize eder.
- **Dinamik Ödül/Ceza (Reward System):** ET (Karıştırma) esnasında ajan (Agent), uyguladığı taarruz sonrası spektrumdaki hedef sayısında bir düşüş algılarsa $(+10)$ ödül puanı alır. Hedefin gücü düşmezse, yani hedefin frekans atlatarak kaçtığı tespit edilirse ajan enerji israfı nedeniyle $(-5)$ puanlık ceza ile cezalandırılır.
- **Taarruz Kavraması:** Otonom ajan, zamanla hangi hedef profilinde ne kadar süre $T_{jam}$ (Karıştırma) ve $T_{look}$ (Dinleme) yapması gerektiğini öğrenerek "Optimum Duty Cycle" oranına yakınsar.

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

---

## 🛠️ Teknik Gereksinimler ve Kurulum

Proje, Derin Öğrenme, Sinyal İşleme ve Asenkron Web Haberleşmesi kütüphanelerinin eşgüdümlü birleşimini gerektirmektedir.

```bash
# Gerekli Taktik Sinyal, ML ve Ağ Paketlerinin Kurulumu
pip install -r requirements.txt eventlet

# Bilişsel EH Karar ve Destek Sisteminin Başlatılması
python main.py
```

Sistem başlatıldığında `http://localhost:5000` adresinden TCP/WS tabanlı Komuta Kontrol Enstrüman Panelinize erişebilirsiniz.

---

## 🚀 Akademik Vizyon ve Nihai Otonomi
Bu proje, salt bir yazılım mimarisi değil, elektromanyetik spektrumda hayatta kalmanın sadece "Daha akıllı algoritmalarla" mümkün olacağını gösteren akademik bir vizyondur. İnsansız Hava Araçları (İHA) ve Otonom Kara Araçları (İKA) için GNU Radio / UHD (USRP Hardware Driver) uyumluluğu gözetilerek yazılmış bu iskelet, modüler yapısı sayesinde gerçek donanımlarla bir "Otonom Elektronik Harp Subayı" olarak işlev görme nihai hedefine (TRL-9) adaydır.