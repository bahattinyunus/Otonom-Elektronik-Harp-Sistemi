# ELEKTRONİK HARP YARIŞMASI TEKNİK YETERLİLİK FORMU CEVAPLARI

Bu belge, "Otonom Elektronik Harp Sistemi (Cognitive-EW-Suite)" projesi kapsamında, TEKNOFEST 2026 Elektronik Harp Yarışması Teknik Yeterlilik Formu sorularına yönelik hazırlanan cevapları içermektedir.

---

**1. Yarışmaya katılacak olan Elektronik Harp (EH) Sistemi hangi alt sistemlerden oluşmaktadır?**
- [ ] Sadece Elektronik Destek
- [ ] Sadece Elektronik Taarruz
- [x] Elektronik Destek ve Elektronik Taarruz

**2. Yarışmaya katılacak olan EH Sistemi kaç adet Sistem’den oluşmaktadır?**
Yarışmaya toplamda 4 adet sistem birimi ile katılım sağlanacaktır. Elektronik Destek (ED) kapsamında konum belirleme görevi (TDOA) için 3 adet eşgüdümlü çalışan ED alıcı (sensör) sistemi kullanılacaktır. Elektronik Taarruz (ET) ve genel spektrum yönetimi için merkez ağ geçidi işlevi görecek 1 adet ED/ET kombine taarruz ve haberleşme/merkez birimi görev yapacaktır.

**3. Yarışmaya katılacak olan EH Sistemi hangi işlevleri yerine getirmektedir?**
- **Elektronik Destek:** Sinyal Tespiti, Parametre Çıkarımı, Sinyal İzleme/Dinleme, Yön Bulma (DF), Konum Belirleme, AI Destekli Sınıflandırma ve Neural Denoising (Diğer: max 300 karakter).
- **Elektronik Taarruz:** Sürekli Karıştırma, Ara-Bakışlı Karıştırma, Analog Telsiz Aldatma, GNSS Aldatma, DRFM tabanlı Hedef Simülasyonu ve FHSS Kestirimli Taarruz (Diğer: max 300 karakter).

**4. Yarışmaya katılacak olan EH Sistemini tanıtınız.**
Sistem donanım-bağımsız (HW-Agnostic) mimari ile SDR temelli (USRP B210 ve X310) olarak geliştirilecektir. Piyasadan tedarik edilmiş hazır arayüzler yerine, donanım seviyesi üstündeki tüm spektrum analiz, sinyal işleme, yapay zeka (PyTorch/CUDA) ve karar-destek algoritmaları tamamen özgün olarak tasarlanmıştır. Spektrum verisi, tarafımızca asenkron Flask-SocketIO altyapısıyla kodlanan "Siber Operatör Komuta Merkezi (C2 Dashboard)" arayüzü ile yönetilecek, sistem bilişsel otomasyon dahilinde hedefleri otonom tespit edip taarruz edecektir. 

**5. Sistem mimarinizi açıklayınız.**
Sistem Mimarisi 4 ana bloktan oluşur: (1) SDR Hardware Abstraction Layer, (2) Adaptive CV tabanlı Spektral Hedef Tespit ve CA-CFAR Modülü, (3) PyTorch Yapay Zeka Sınıflandırma ve LSTM FHSS Tahmin Ağı, (4) Deep Q-Network (DQN) tabanlı Otonom Görev Yöneticisi ve C2 Dashboard. _(Detaylı Sistem Blok Şeması, KYS sistemine "sistem_blok_semasi.png" adlı görsel olarak yüklenecektir.)_

**6. Sistemin entegre olacağı platformu açıklayınız.**
- **Seçim:** Karada, Taşınabilir (kullanım sırasında sabit)
- **Kullanım Şekli:** Sistem, arazide üçgen bir formasyon oluşturacak şekilde aralarında ağ bağlantısı (RF veya Mesh LAN) bulunan 3 farklı tripod üzeri konumlandırılmış sensör birimleri (USRP) ve bu birimlerin telemetrisini işleyerek yön/konum bulup angajman uygulayan bir Komuta Kontrol İstasyonu etrafında şekillenmektedir. _(Kullanım şeklini belirten operasyonel yerleşim görseli eklenecektir.)_

**7. Elektronik Destek Sisteminin “Çalışma Frekans Bandı” nedir?**
70 MHz – 6000 MHz (USRP B210 donanım yetenekleri ve anten aralığı doğrultusunda).

**8. Elektronik Destek Sistemi kaç kanaldan oluşacaktır? Almaç anlık bant genişliği için ne öngörülmektedir?**
- DF için Kanal Sayısı: 3 (Sistem geneli toplam sensör kanal sayısı)
- DF için Almaç Anlık Bant Genişliği: 56 MHz
- Monitör/İzleme için Kanal Sayısı: 1 (veya 2, USRP 2x2 MIMO)
- Monitör/İzleme için Anlık Bant Genişliği: 56 MHz

**9. Elektronik Destek Sistemi’nde “Sinyal Tespiti” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Sinyal tespiti klasik enerji tabanlı sabit eşikleme yerine, **CA-CFAR (Cell Averaging Constant False Alarm Rate)** algoritması ve **V4 Adaptive Bilgisayarlı Görü (CV)** modülü ile yapılır. Spektrum 2B Waterfall Spectrogram'a dönüştürülür, adaptive threshold ve morphological closing teknikleri kullanılarak dinamik gürültü zemini bastırılır. Bu sayede, atmosferik sönümleme (fading) ve çevresel gürültünün yarattığı dezenformasyon filtrelenir; sinyal adacıklarının SNR marjı otonom çıkarılır.

**10. Elektronik Destek Sistemi’nde “Parametre Çıkarımı” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Tespit edilen sinyal adacıkları üzerinden öncelikle geometrik/merkez frekans ve bant genişliği hesaplanır. Daha sonra sınıflandırma için **Spektral Momentler** (Basıklık/Kurtosis, Çarpıklık/Skewness, Düzlük/Flatness) analiz edilir. Bu istatistiksel öznitelikler, PyTorch Çok Katmanlı İleri Beslemeli Ağ (MLP) mimarisine verilerek sinyalin Modülasyon Tipi (BPSK, QPSK, 16QAM, FMCW, dar/geniş bant) çıkarılır. Ayrıca LSTM ağları kullanılarak frekans atlamalı (FHSS) sinyallerin hop aralıkları listelenir.

**11. Elektronik Destek Sistemi’nde “Sinyal İzleme/Dinleme” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Sinyal izleme, hedefin non-lineer manevralarını ve frekans atlamalarını yüksek hassasiyetle modelleyen **UKF (Unscented Kalman Filter)** izci mimarisi ile sağlanır. Analog ve sayısal sinyaller izlendiğinde, PSD verileri öncelikle 1D-CNN Autoencoder üzerinden geçirilip stokastik gürültüden (Denoising) arındırılır. Sayısal haberleşmenin I/Q bazband seviyesinde kayıt ve dinleme fonksiyonları C2 Dashboard altyapısına akıtılır.

**12. Elektronik Destek Sistemi’nde “Yön Bulma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Yön bulma işlemi, birden fazla (üç adet senkronize) sensör nodu arasındaki Zaman Farkı, yani **TDOA (Time Difference of Arrival)** yöntemi kullanılarak gerçekleştirilecektir. İlgili I/Q akışları, çapraz korelasyon tabanlı algoritmalar ile hedefin geliş açısını (Angle of Arrival - AoA) hesaplar. Hedefin geliş açısı için çevresel yansımalar ve gürültü dahil edildiğinde RMS doğruluk öngörüsü ~2-3 derece arasındadır.

**13. Elektronik Destek Sistemi’nde “Konum Bulma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Konum belirleme (Geolocation), sistemin eşgüdümlü konumlandırılmış minimum 3 sensör nodunun TDOA verilerini birleştirerek kurduğu hiperbolik kesişim denkleminin çözülmesi ile yapılır. Araziye 100-200 metre açıklıklarla üçgen konfigürasyonda dağıtılmış, tek bir merkezle haberleşen üniteler, ortak bir NTP/GPS zaman referansına göre kayıtları zaman damgasıyla eşleştirir ve hedefin XY koordinatlarını C2 Haritasına (Dashboard) çizer.

**14. Elektronik Destek Sistemi’nde Yapay Zekâ kullanım hakkında bilgi veriniz.**
Elektronik Destek (ED) alt sistemimizde, klasik enerji tabanlı eşikleme algoritmalarının LPI (Düşük Yakalanma Olasılığı) ve düşük SNR'li sinyallerde yetersiz kalması sebebiyle, sinyal tespiti ve sınıflandırması tamamen Yapay Zekâ mimarilerine devredilmiştir:
1. **Otonom Modülasyon Sınıflandırması (AMC):** Yakalanan sinyallerden çıkarılan spektral momentler (Kurtosis, Skewness, Flatness) ve I/Q bazbant verisi, PyTorch tabanlı Derin Sinir Ağına (Multi-Layer Perceptron / 1D-CNN) beslenerek sinyalin modülasyon tipi (QPSK, QAM, BPSK, FMCW vs.) sub-milisaniye hızında otonom olarak sınıflandırılır.
2. **RF Parmak İzi (Fingerprinting) ve Anomali Tespiti:** Spektral I/Q verilerindeki vericiye özgü mikro-sapmalar (hardware imperfections / transient behaviors) yapay zeka tarafından analiz edilerek, aynı modülasyonu kullanan dost ve düşman birimler cihaz bazında ayırt edilir (RFI Signature Hash).
3. **Nöral Gürültü Filtreleme (Neural Denoising):** Çevresel sönümlemeye (fading) uğramış zayıf sinyaller, Deep Autoencoder mimarisi üzerinden geçirilerek atmosferik stokastik RF gürültüsünden arındırılır ve taarruz (ET) ajanlarına "temizlenmiş hedef öznitelikleri" olarak aktarılır.

**15. Elektronik Destek Alt Sistemi’nin SwaP (Size, Weight and Power) bilgileri:**
- Fiziksel Boyut: USRP + Endüstriyel İşlem Birimi kombinasyonu için yaklaşık $250 \times 160 \times 60 \text{ mm}$ (SDR nodları bazında)
- Ağırlık: $\sim 2.5 \text{ kg}$
- Güç: Ortalama $30\text{W}$ DC besleme (Tripod/Batarya tabanlı çalıştırma için optimize edilmiş düşük enerji).

**16. Elektronik Taarruz Sisteminin Çalışma Frekans Bandı nedir?**
70 MHz – 6000 MHz (USRP SDR çıkışıyla senkronize, PA destekli TX).

**17. Elektronik Taarruz Sistemi kaç Alt Banttan oluşacaktır? Bant başına RF çıkışı gücü için ne öngörülmektedir?**
- **Karıştırma için Alt Bant Sayısı:** 2 Alt Bant (Örn: 100-1000 MHz Telsiz / Telemetri bandı; 1000-6000 MHz Radar / Link bandı)
- **Karıştırma Bant Başına RF Çıkış Gücü:** SDR'nin sinyal sentezi (max 100mW) uygun frekans bloklarına bölünmüş iki adet Güç Yükselteci (Power Amplifier - PA) ile desteklenecek olup, çıkış gücü taktik altyapıya göre $10\text{W} - 20\text{W}$ civarıdır. Yönlü (aktif DF sonrasında hüzme yönlendirmesi yapılan anten ~10 dBi kazanç) antenler vasıtasıyla hedefe odaklanılır.
- **Aldatma için Alt Bant Sayısı:** 1 Alt Bant (Özel operasyon / GNSS)
- **Aldatma Bant Başına RF Çıkış Gücü:** Yüksek güç ihtiyacı gerektirmeyen hassas aldatma görevleri için $1\text{W} - 5\text{W}$ civarı ve eşyönlü anten uygulaması öngörülmektedir.

**18. Elektronik Taarruz Sistemi’nde “Sürekli Karıştırma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Sürekli karıştırma, SDR FPGA gücü ve PyTorch tabanlı sistemin otonom parametre (Sweep Rate vb.) ayarlarıyla Spot, Baraj (Barrage) veya Çoklu Hedef (Multi-target Spot) biçiminde uygulanır. Otonom ajan, 5-10 hedefe (SDR örnekleme kapasitesi elverdiğince modüle edilen sub-carrier'lar vasıtasıyla) geniş bantta eş zamanlı reaksiyon gösterebilir; DRFM teknikleriyle düşmanın komuta kanalını bloke edecek waveform dizileri otonom sentezlenir.

**19. Elektronik Taarruz Sistemi’nde “Arabakışlı Karıştırma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Look-Through (Ana-bakış) karıştırma, rastgele veya kural tabanlı değil; Pytorch tabanlı **Deep Q-Network (DQN) Ajanı** tarafından "Optimum Duty Cycle" (Görev Döngüsü) yönetilerek gerçekleştirilir. Ajan $T_{\text{jam}}$ ve $T_{\text{look}}$ aralığını, hedefin spektrumdaki kaçış stratejisine göre optimize eder. Almacın $>50\text{ MHz}$ anlık bant genişliğinde reaksiyon (OODA) döngüsü, insan gözlemciden bağımsız $<50\text{ ms}$ gecikme seviyelerine düşürülerek ET-ED körleşmesi engellenir.

**20. Elektronik Taarruz Sistemi’nde “Analog Telsiz Aldatma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
ED esnasında analog AM/FM telsiz trafikleri kaydedilerek (IQ bazbant veri kayıt), "Dijital Radyo Frekans Hafızası (DRFM)" mantığında saklanır. Algoritma bu sesi C2 Dashboard "Operator Override" izniyle hedef telsizin sinyal özelliklerine otomatize eder (replay, pitch-shift, ses sentezleme veya sinyal bindirme). Operatör gürültü eklenmiş veya sahte ses içeriklerini aldatma amaçlı taarruz frekansından hibrid şekilde yayabilir.

**21. Elektronik Taarruz Sistemi’nde “GNSS Aldatma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
GNSS Aldatma, COTS (Hazır) açık kaynak SDR bazlı GNSS Spoofer modüllerinin otonom karar destek sistemimize entegrasyonuyla yapılmaktadır. L1 (1575.42 MHz) bandında, hedef İHA veya platformun TDOA ile alınan konumu doğrultusunda, platformu gerçek pozisyonundan kademeli olarak ("Walk-off" tekniği) istenen sanal bir noktaya veya sahte zaman referansına inandıracak düşük güçlü sentetik uydu sinyalleri yayınlanır.

**22. Elektronik Taarruz Sistemi’nde Yapay Zekâ kullanım hakkında bilgi veriniz.**
Elektronik Taarruz (ET) alt sistemimiz, kural-tabanlı (rule-based) reaktif karıştırma yerine, elektromanyetik spektrumu bir durum-uzayı (state-space) olarak ele alan "Bilişsel (Cognitive) ET" mimarileri kullanır:
1. **Derin Pekiştirmeli Öğrenme (DQN) ile Duty-Cycle Optimizasyonu:** Karıştırma esnasında kendi ED sistemimizin körleşmesini (fratricide) engellemek adına kullanılan Ara-Bakışlı (Look-Through) tekniğinin "Görev Döngüsü (Duty Cycle)" Deep Q-Network ajanı tarafından yönetilir. Ajan, ortamı sürekli dinleyerek Karıştırma ($T_{\text{jam}}$) ve Gözlem ($T_{\text{look}}$) sürelerini anlık spektral duruma (BDA - Hasar Tespit) göre ödül/ceza mekanizmasıyla optimize eder.
2. **Kestirimci Karıştırma (Anticipatory Jamming):** Hedef tehdit frekans atlamalı (FHSS) bir haberleşme altyapısı kullanıyorsa (ticari/taktiksel dronlar, kural-tabanlı radyolar vb.), hedefin atlama örüntüsü (hop sequence) Derin LSTM (Uzun Kısa Vadeli Bellek) zaman serisi tahmin modelleriyle analiz edilir. Yapay zeka, TRANSEC mülahazası içermeyen tekrarlı dizilimlerin bir sonraki sıçrayacağı frekans merkezini (hop) öngörerek o frekansa milisaniyeler öncesinden odaklanır; böylece reaktif değil "kestirimci/öngörülü" proaktif bir taarruz icra eder.

**23. Elektronik Taarruz Alt Sistemi’nin SwaP (Size, Weight and Power) bilgileri:**
- Fiziksel Boyut: USRP SDR + RF Güç Yükselteçleri (Power Amp) + Isı Dağıtıcı bloklar ile yaklaşık $350 \times 250 \times 150 \text{ mm}$ ebatlarındadır.
- Ağırlık: RF katı, anten bağlayıcıları ve soğutma sistemleri dahil $\sim 6.5 \text{ kg}$.
- Güç: DC Kaynak. Karıştırma (Gönderme) esnasında çekilen anlık yüksek akım gözetildiğinde ortalama $120\text{W} - 150\text{W}$ DC güç sarfiyatı (Batarya / Alternatör destekli).
