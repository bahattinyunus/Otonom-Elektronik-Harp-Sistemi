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
Sistem, HW-Agnostic strateji ve SDR donanımları (USRP) odağında geliştirilecektir. Hazır modüller yerine spektrum sentez, derin öğrenme (PyTorch/CUDA) ve EW karar destek algoritmaları uçtan uca özgün kodlanacaktır. Komuta kontrolü Flask Socket.io tabanlı tasarlanacak ve "Siber Operatör C2 Dashboard" üzerinden yönetilecektir. Mimari yapı, spektral hedefleri tespit, takip ve taarruz döngüsünde otonom icra edebilen bilişsel bir altyapıya sahip olacaktır.

**5. Sistem mimarinizi açıklayınız.**
Sistem Mimarisi 4 ana bloktan oluşacaktır: (1) SDR Hardware Abstraction Layer, (2) Adaptive CV tabanlı Spektral Hedef Tespit ve CA-CFAR Modülü, (3) PyTorch Yapay Zeka Sınıflandırma ve LSTM FHSS Tahmin Ağı, (4) Deep Q-Network (DQN) tabanlı Otonom Görev Yöneticisi ve C2 Dashboard. _(Detaylı Sistem Blok Şeması, KYS sistemine "sistem_blok_semasi.png" adlı görsel olarak yüklenecektir.)_

**6. Sistemin entegre olacağı platformu açıklayınız.**
- **Seçim:** Karada, Taşınabilir (kullanım sırasında hareketli)
- **Kullanım Şekli:** Sistem, sabit ve mobil kara platformlarında otonom görev yapacak şekilde tasarlanacaktır. Sinyal tespiti 12'li Vivaldi anten dizilimiyle, taarruz ise step motor yönlendirmeli log-periyodik anten ile gerçekleştirilecektir. RF bileşenleri ve SDR donanımları elektromanyetik dayanım için özel Faraday kafesinde korunacak, termal kararlılık endüstriyel fanlar kullanılarak güç amplifikatörleriyle sağlanacaktır. (Bkz. Ek Görseller)


**7. Elektronik Destek Sisteminin “Çalışma Frekans Bandı” nedir?**
70 MHz – 6000 MHz (USRP B210 donanım yetenekleri ve anten aralığı doğrultusunda).

**8. Elektronik Destek Sistemi kaç kanaldan oluşacaktır? Almaç anlık bant genişliği için ne öngörülmektedir?**
- DF için Kanal Sayısı: 3 (Sistem geneli toplam sensör kanal sayısı)
- DF için Almaç Anlık Bant Genişliği: 56 MHz
- Monitör/İzleme için Kanal Sayısı: 1 (veya 2, USRP 2x2 MIMO)
- Monitör/İzleme için Anlık Bant Genişliği: 56 MHz

**9. Elektronik Destek Sistemi’nde “Sinyal Tespiti” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Sinyal tespiti klasik eşikleme yerine, CA-CFAR algoritması ve Adaptive Bilgisayarlı Görü modülü ile yapılacaktır. I/Q verisi 2B Histogramlara dönüştürülecek, adaptif threshold ve morfolojik kapatma teknikleri uygulanarak dinamik gürültü zemini bastırılacaktır. Böylelikle atmosferik sönümleme ve çevresel gürültünün yarattığı dezenformasyon filtrelenmiş olacak; sinyal adacıklarının sınırları otonom çıkarılacaktır.

**10. Elektronik Destek Sistemi’nde “Parametre Çıkarımı” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Tespit edilen sinyal adacıklarından merkez frekans ve bant genişliği hesaplanacaktır. Sınıflandırma için Spektral Momentler (Basıklık, Çarpıklık vs.) analiz edilecek; çok katmanlı yapay sinir ağı (MLP) mimarisine beslenerek sinyalin Modülasyon Tipi (BPSK, QPSK, FMCW) otonom olarak çıkarılacaktır. Frekans atlamalı (FHSS) sinyaller için özel LSTM modelleri koşturulup hop örüntüleri listelenecektir.

**11. Elektronik Destek Sistemi’nde “Sinyal İzleme/Dinleme” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Sinyal izleme, hedefin non-lineer manevralarını ve frekans atlamalarını yüksek hassasiyetle modelleyen **UKF (Unscented Kalman Filter)** izci mimarisi ile sağlanacaktır. Analog ve sayısal sinyaller izlendiğinde, PSD verileri öncelikle 1D-CNN Autoencoder üzerinden geçirilip stokastik gürültüden (Denoising) arındırılacaktır. Sayısal haberleşmenin I/Q bazband seviyesinde kayıt ve dinleme fonksiyonları C2 Dashboard altyapısına akıtılacaktır.

**12. Elektronik Destek Sistemi’nde “Yön Bulma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Yön bulma işlemi, birden fazla (üç adet senkronize) sensör nodu arasındaki Zaman Farkı, yani **TDOA (Time Difference of Arrival)** yöntemi kullanılarak gerçekleştirilecektir. İlgili I/Q akışları, çapraz korelasyon tabanlı algoritmalar ile hedefin geliş açısını (Angle of Arrival - AoA) hesaplayacaktır. Hedefin geliş açısı için çevresel yansımalar ve gürültü dahil edildiğinde RMS doğruluk öngörüsü ~2-3 derece arasında olacaktır.

**13. Elektronik Destek Sistemi’nde “Konum Bulma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Konum belirleme (Geolocation), sistemin eşgüdümlü konumlandırılmış minimum 3 sensör nodunun TDOA verilerini birleştirerek kurduğu hiperbolik kesişim denkleminin çözülmesi ile yapılacaktır. Araziye 100-200 metre açıklıklarla üçgen konfigürasyonda dağıtılmış, tek bir merkezle haberleşen üniteler, ortak bir NTP/GPS zaman referansına göre kayıtları zaman damgasıyla eşleştirecek ve hedefin XY koordinatlarını C2 Haritasına (Dashboard) çizecektir.

**14. Elektronik Destek Sistemi’nde Yapay Zekâ kullanım hakkında bilgi veriniz.**
ED sisteminde, klasik algoritmaların tespit edemediği düşük SNR'li hedefler için Derin Öğrenme kullanılacaktır. Moment verisi 1D-CNN asıllı PyTorch ağına iletilerek modülasyon tipi sınıflandırılacaktır. RF Parmak İzi ile verici donanım analizi (RFI Signature) otonom sağlanarak dost/düşman platform ayrımı yapılacaktır. "Neural Denoising" (Derin Otokodlayıcılar) mimarileriyle de hedef sinyal öznitelikleri atmosferik/stokastik gürültüden arındırılarak ET birimine tertemiz aktarılacaktır.

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
Sürekli karıştırma, SDR FPGA gücü ve PyTorch tabanlı sistemin otonom parametre (Sweep Rate vb.) ayarlarıyla Spot, Baraj (Barrage) veya Çoklu Hedef (Multi-target Spot) biçiminde uygulanacaktır. Otonom ajan, 5-10 hedefe (SDR örnekleme kapasitesi elverdiğince modüle edilen sub-carrier'lar vasıtasıyla) geniş bantta eş zamanlı reaksiyon gösterebilecek; DRFM teknikleriyle düşmanın komuta kanalını bloke edecek waveform dizileri otonom sentezlenecektir.

**19. Elektronik Taarruz Sistemi’nde “Arabakışlı Karıştırma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
Ara-bakış (Look-Through) karıştırmanın "Otonom Duty Cycle" kontrolü, yapay zekaya (Derin Pekiştirmeli Öğrenme/DQN ajanına) bırakılacaktır. Ajan, ortamı tarama (T-look) ve darbe (T-jam) periyotlarını hedefin spektral taktiğine göre otonom optimize edecektir. 50+ MHz bant genişliğindeki OODA reaksiyon hızı düşürülerek, karıştırma esnasında kendi ED birimlerimizin körleşmesi (fratricide etkisi) engellenecektir.

**20. Elektronik Taarruz Sistemi’nde “Analog Telsiz Aldatma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
ED esnasında analog AM/FM telsiz trafikleri kaydedilerek (IQ bazbant veri kayıt), "Dijital Radyo Frekans Hafızası (DRFM)" mantığında saklanacaktır. Algoritma bu sesi C2 Dashboard "Operator Override" izniyle hedef telsizin sinyal özelliklerine otomatize edecektir (replay, pitch-shift, ses sentezleme veya sinyal bindirme). Operatör gürültü eklenmiş veya sahte ses içeriklerini aldatma amaçlı taarruz frekansından hibrid şekilde yayabilecektir.

**21. Elektronik Taarruz Sistemi’nde “GNSS Aldatma” görevinin nasıl yapılacağı hakkında bilgi veriniz.**
GNSS Aldatma, COTS (Hazır) açık kaynak SDR bazlı GNSS Spoofer modüllerinin otonom karar destek sistemimize entegrasyonuyla yapılacaktır. L1 (1575.42 MHz) bandında, hedef İHA veya platformun TDOA ile alınan konumu doğrultusunda, platformu gerçek pozisyonundan kademeli olarak ("Walk-off" tekniği) istenen sanal bir noktaya veya sahte zaman referansına inandıracak düşük güçlü sentetik uydu sinyalleri yayınlanacaktır.

**22. Elektronik Taarruz Sistemi’nde Yapay Zekâ kullanım hakkında bilgi veriniz.**
ET sistemimiz, reaktif yaklaşım yerine "Bilişsel ET (Cognitive-EW)" ilkeleriyle hareket edecektir. Körleşmeyi (fratricide) önlemek adına Ara-Bakış tekniğinin "Görev Döngüsü", DQN ajanı tarafından BDA geri bildirimleriyle otonom optimize edilecektir. Ek olarak frekans atlamalı (FHSS) telsiz/cihazların iletişim dizilimleri, derin LSTM ağlarıyla analiz edilerek hedefin bir sonraki hop noktası önceden sezilecek; böylelikle proaktif ve kestirimci taarruz icra edilebilecektir.

**23. Elektronik Taarruz Alt Sistemi’nin SwaP (Size, Weight and Power) bilgileri:**
- Fiziksel Boyut: USRP SDR + RF Güç Yükselteçleri (Power Amp) + Isı Dağıtıcı bloklar ile yaklaşık $350 \times 250 \times 150 \text{ mm}$ ebatlarında olacaktır.
- Ağırlık: RF katı, anten bağlayıcıları ve soğutma sistemleri dahil $\sim 6.5 \text{ kg}$.
- Güç: DC Kaynak. Karıştırma (Gönderme) esnasında çekilen anlık yüksek akım gözetildiğinde ortalama $120\text{W} - 150\text{W}$ DC güç sarfiyatı (Batarya / Alternatör destekli).
