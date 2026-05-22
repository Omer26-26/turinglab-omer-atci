# TuringLab — Mini Rapor

**Öğrenci:** Ömer Ataç  
**Ders:** Hesaplama Kuramı — Bilgisayar Mühendisliği  
**Tarih:** Mayıs 2026  

---

## 1. Giriş

TuringLab, Hesaplama Kuramı dersi kapsamında geliştirilmiş bir Turing makinesi simülatörüdür. Proje, soyut bir matematiksel model olan Turing makinesini somut bir yazılım artefaktına dönüştürerek hesaplama kavramının deneyimlenmesini amaçlamaktadır.

Sistem, YAML formatında tanımlanan Turing makinesi konfigürasyonlarını okuyup çalıştırabilen bir Python paketidir. Tek-şeritli deterministik Turing makinelerinin yanı sıra, bonus kapsamında çok-şeritli TM, non-deterministik TM, karşılaştırmalı analiz ve adım-adım görselleştirme özellikleri de barındırmaktadır.

Paketin temel kullanım alanları:
- YAML dosyasından makine tanımı yükleme
- Girdi dizgisi üzerinde simülasyon çalıştırma (verbose mod desteği ile)
- Çalışma geçmişinin (history) adım adım kaydedilmesi
- Farklı TM varyantlarının (çok-şeritli, non-deterministik) deneysel olarak karşılaştırılması

---

## 2. Mimari

### 2.1 Modül Organizasyonu

```
turinglab/
├── __init__.py          # Paket giriş noktası, public API export'ları
├── tm_engine.py         # Tek-şeritli deterministik TM motoru (SingleTapeTM)
├── multi_tape.py        # Çok-şeritli TM motoru (MultiTapeTM) [Bonus A]
├── ntm.py               # Non-deterministik TM motoru (NondeterministicTM) [Bonus B]
└── visualizer.py        # Adım-adım görselleştirici (TuringVisualizer) [Bonus D]
```

### 2.2 Şerit Temsili

Şerit, `Dict[int, str]` (sözlük) yapısıyla temsil edilmektedir. Bu kararın arkasında birkaç motivasyon vardır:

1. **Negatif indeks desteği:** Kafa sola hareket ettiğinde indeks negatife düşebilir. Liste tabanlı bir yapıda bu durum sürekli `insert(0, ...)` gerektirirdi; sözlük yapısında doğal olarak desteklenir.
2. **Sonsuz şerit illüzyonu:** Turing makinesi tanımı gereği şerit sonsuz uzunluktadır. Sözlükte olmayan bir indekse erişildiğinde `tape.get(i, self.blank)` ile boş sembol döndürülür — bu, sonsuz şeridin verimli bir simülasyonudur.
3. **Bellek verimliliği:** Yalnızca yazılmış hücreler bellekte tutulur; boş hücreler yer kaplamaz.

**Alternatif olarak** `deque` veya dinamik dizi kullanılabilirdi. Ancak bu yapılarda negatif indeks yönetimi ek karmaşıklık getirir ve Turing makinelerinin tipik kullanım deseninde (seyrek yazma, geniş aralık) sözlük yapısı daha uygundur.

### 2.3 Geçiş Fonksiyonu Temsili

Geçiş fonksiyonu `δ(q, a) = (q', b, D)` iç içe sözlük olarak tutulur: `transitions[state][read_char] = (next_state, write_char, move)`. YAML'dan gelen liste formatı, `__init__` içinde bu yapıya dönüştürülür. Bu sayede geçiş araması O(1) zamanda yapılır.

### 2.4 Tasarım Kararları

- **Durma koşulları:** Makine üç şekilde durur: (1) kabul durumuna geçiş, (2) ret durumuna geçiş, (3) tanımsız geçiş (no_transition). Ayrıca `max_steps` ile sonsuz döngü koruması sağlanır.
- **History kaydı:** Her adımda `Configuration(state, tape, head_position)` kaydedilir. Bu, hem hata ayıklama hem de görselleştirme için kritiktir.
- **YAML standardizasyonu:** Geçişler hem liste hem de sözlük formatında kabul edilir; bu esneklik farklı kaynaklardan gelen tanımları destekler.

---

## 3. Tasarlanan Turing Makineleri

### TM-1: Unary → Binary Çevirici (`unary_to_binary.yaml`)
Girdi olarak verilen unary sayıyı (1'ler dizisi) ikili (binary) sayıya çevirir. "Sayma ve artırma" stratejisi kullanılır: her `1` işaretlenirken, şerit sonundaki ikili sayaç bir artırılır. 10 durum ile O(n²) karmaşıklığında çalışır. En zorlu kısım, binary artırma sırasında elde (carry) yönetimi ve sınır sembolünün korunmasıydı.

### TM-2: İkili Karşılaştırıcı (`binary_compare.yaml`)
İki binary sayıyı (`N1#N2` formatında) karşılaştırır ve N1 > N2 ise kabul eder. İki fazlı bir algoritma kullanılır: önce uzunluk karşılaştırması, eşitse basamak bazında MSB'den başlayarak karşılaştırma. 14 durum ile O(n²) karmaşıklığında çalışır. **Bu, tasarlanan en zorlu makineydi** — uzunluk eşitliği durumunda basamak karşılaştırması için çok sayıda durum geçişi yönetilmesi gerekti.

### TM-3: Dizgi Kopyalayıcı (`string_copy.yaml`)
`{a, b}*` alfabesindeki bir dizgiyi şeridin sonuna kopyalar (çıktı: `w#w`). Karakter karakter işaretleme ve sona kopyalama stratejisi kullanılır. 9 durum, O(n²) karmaşıklık. Kopyalanan karakterin türünü (`a` mı `b` mi) hatırlamak için ayrı durumlara ihtiyaç duyulması, durum sayısını artıran ana faktördü.

### TM-4: Parantez Denetleyici (`student_choice.yaml`)
Dengeli parantez dizilerini kabul eden TM. "En içteki çifti sil" stratejisi ile çalışır: ilk `)` bulunur, geriye dönülerek eşleşen `(` bulunur, ikisi de `X` ile işaretlenir. 5 durum ile en kompakt tasarımdır. Tüm parantezler eşleşince kabul, eşleşmeyen parantez kalınca ret.

### Zorluk Sıralaması
En zordan en kolaya: **TM-2** (binary karşılaştırma) > **TM-1** (unary→binary) > **TM-3** (string copy) > **TM-4** (parantez). Karşılaştırma makinesinde iki fazlı algoritma ve çok sayıda yardımcı sembol yönetimi en büyük meydan okumaydı.

---

## 4. Kavramsal Tartışma

### Halting Problemi ve TuringLab

**Soru:** *Halting problemini TuringLab içinde "çözmek" mümkün mü? Neden değil?*

TuringLab simülatöründe bir Turing makinesinin durma (halting) davranışını tam olarak belirlemek teorik açıdan **imkânsızdır**. Bu sonuç, Alan Turing'in 1936 yılında kanıtladığı ünlü Halting Teoremi'nin doğrudan bir yansımasıdır.

Teorem şunu söyler: Herhangi bir Turing makinesi M ve girdi w verildiğinde, M'nin w üzerinde durup durmayacağını belirleyen genel bir algoritma (yani bir Turing makinesi H) var olamaz. Kanıt, çaprazlama (diagonalization) yöntemiyle yapılır: H'nin varlığı kabul edildiğinde, H'yi kullanan ama kendi üzerinde çelişkiye düşen bir D makinesi inşa edilebilir. D, "H benim duracağımı söylüyorsa sonsuz döngüye gir, durmayacağımı söylüyorsa dur" şeklinde çalışır. Bu durumda H, D'yi doğru analiz edemez — çelişki.

TuringLab'da bunun pratikte karşılığı `max_steps` parametresidir. Simülatörümüz bir makineyi en fazla `max_steps` adım çalıştırır; bu süre aşılırsa `timeout` sonucu döner. Ancak bu bir **çözüm** değil, bir **yaklaşımdır** (underapproximation). Timeout alan bir makine gerçekte şu üç durumdan birinde olabilir: (1) daha uzun sürede kabul edecek, (2) daha uzun sürede reddedecek, (3) asla durmayacak. TuringLab bunları ayırt edemez.

Bu sınırlama, hesaplanabilirlik kuramının temel bir sonucudur ve hiçbir programlama dili, kütüphane veya algoritma ile aşılamaz. Rice Teoremi bunu daha da genelleştirir: bir Turing makinesinin herhangi bir "önemsiz olmayan" semantik özelliği bile karar verilemezdir. TuringLab'ın `max_steps` yaklaşımı, pratikte makul bir uzlaşma sunar — ancak teorik sınırın farkında olmak, hesaplama kuramının özünü anlamak açısından kritiktir.

---

## 5. Sınırlar ve İleri Çalışma

### Mevcut Sınırlar
- **Performans:** Şerit sözlük tabanlı olduğu için büyük girdilerde Python'un inherent yavaşlığı hissedilir. C extension veya Cython ile hızlandırılabilir.
- **Girdi ayrıştırma:** Çok-şeritli TM'de girdi tek şeritten parse edilir; daha zengin bir girdi formatı tasarlanabilir.
- **Hata mesajları:** Geçersiz YAML konfigürasyonlarında hata mesajları daha açıklayıcı olabilir (hangi geçiş hatalı, hangi durum tanımsız vb.).

### Bir Hafta Daha Olsa Ne Eklerdim?
- **Universal Turing Machine (UTM):** Bir TM'in kodlanmış tanımını girdi olarak alıp simüle eden meta-makine. Bu, Church-Turing tezinin somut bir gösterimidir.
- **Web arayüzü:** Flask/FastAPI tabanlı bir web uygulaması ile tarayıcıdan TM tasarlama ve çalıştırma.
- **Otomatik durum diyagramı:** Graphviz ile YAML'dan otomatik durum geçiş diyagramı üretimi.
- **Lambda kalkülüs köprüsü:** Lambda ifadelerini TM'e derleyen bir modül — Church-Turing eşdeğerliğinin deneysel kanıtı.

---

## 6. Bonus Bölümleri

### Bonus A — Çok-Şeritli TM
`MultiTapeTM` sınıfı, k adet şeriti paralel olarak yönetir. Geçiş fonksiyonu `δ(q, a₁, a₂, ..., aₖ) = (q', b₁, b₂, ..., bₖ, D₁, D₂, ..., Dₖ)` şeklinde genişletilmiştir. 3-şeritli ikili toplama makinesi ile doğrulanmıştır.

### Bonus B — Non-Deterministik TM
`NondeterministicTM` sınıfı, BFS tabanlı hesaplama ağacı keşfi yapar. Aynı (durum, okunan) çifti için birden fazla geçiş tanımlanabilir. `max_depth` ve `max_branches` parametreleri ile sınırlandırılır. "01 alt-dizgisi var mı?" problemi ile test edilmiştir.

### Bonus C — Karşılaştırmalı Analiz
Aynı dil (L = {w | w'de '01' var}) tek-şeritli, çok-şeritli ve NTM ile çözülüp adım sayıları karşılaştırılmıştır. Sonuçlar `docs/comparison.png` grafiğinde sunulmaktadır.

### Bonus D — Görselleştirici
`TuringVisualizer` sınıfı, Pillow kütüphanesi ile her adımın görsel temsilini PNG olarak üretir. Şerit kutuları, kafa konumu ve durum etiketi gözükür. Ayrıca tüm adımları birleştiren animasyonlu GIF de üretilmektedir.

---

## 7. Kaynakça

1. Sipser, M. (2012). *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning.
2. Turing, A. M. (1936). On Computable Numbers, with an Application to the Entscheidungsproblem. *Proceedings of the London Mathematical Society*, 2(42), 230–265.
3. Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation* (3rd ed.). Pearson.
4. Python Software Foundation. (2024). *Python 3.x Documentation*. https://docs.python.org/3/
5. PyYAML Documentation. https://pyyaml.org/wiki/PyYAMLDocumentation
6. Pillow (PIL Fork) Documentation. https://pillow.readthedocs.io/
