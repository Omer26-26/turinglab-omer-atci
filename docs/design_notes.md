# TuringLab Tasarım Notları

Bu doküman, Bölüm 2 kapsamında tasarlanan Turing makinelerinin tasarım kararlarını ve algoritmalarını içerir.

---

## TM-1: Unary -> Binary Çevirici (unary_to_binary.yaml)

### 1. Strateji
Unary sayıyı (1'ler dizisi) ikili (binary) sayıya çevirmek için "sayma ve artırma" stratejisi kullanılmıştır.
- Şeridin sonuna bir ayraç (`#`) eklenir.
- Soldaki her bir `1` karakteri `X` ile işaretlenir.
- Her işaretleme sonrası ayracın sağındaki ikili sayı bir artırılır (Binary Increment algoritması).
- Tüm `1`ler bittiğinde şerit temizlenerek sadece ikili sonuç bırakılır.

### 2. Durum Sayısı
10 durum kullanıldı. İşaretleme, sona gitme, binary artırma, elde (carry) yönetimi ve temizlik aşamaları için bu sayı gereklidir.

### 3. Şerif Alfabesi Seçimi
`X` işaretleyici olarak, `#` ise girdi ile çıktı arasındaki sınır olarak seçildi.

### 4. Karmaşıklık
Her unary `1` için şerit boyu kadar git-gel yapıldığı için karmaşıklık $O(n^2)$'dir.

### 5. Hata Ayıklama Hikayesi
Binary artırma sırasında kafa konumunun `#` sınırını aşıp soldaki veriyi bozması en büyük problemdi. Sınır kontrolü eklenerek çözüldü.

---

## TM-2: İkili Karşılaştırıcı (binary_compare.yaml)

### 1. Strateji
İki sayının büyüklüğünü karşılaştırmak için "Basamak Eşleştirme ve Fark Yakalama" algoritması kullanıldı.
- Önce her iki sayının uzunlukları kontrol edilir. Daha uzun olan sayı (başta sıfır olmadığı varsayımıyla) daha büyüktür.
- Uzunluklar eşitse, soldan sağa ilk farklı basamak sonucu belirler (1 > 0).

### 2. Durum Sayısı
Yaklaşık 14 durum. Uzunluk takibi ve basamak karşılaştırması için durumlar arası geçişler yoğundur.

### 3. Şerif Alfabesi Seçimi
`X/Y` (N1 için) ve `x/y` (N2 için) kullanılarak hangi basamakların işlendiği takip edildi.

### 4. Karmaşıklık
Her basamak için git-gel yapıldığı için $O(n^2)$'dir.

### 5. Hata Ayıklama Hikayesi
Aynı uzunluktaki sayılarda ilk farkın (MSB) tespiti zordu. Durumları "N1 muhtemelen büyük" veya "N2 muhtemelen büyük" şeklinde güncelleyerek çözüm sağlandı.

---

## TM-3: Dizgi Kopyalayıcı (string_copy.yaml)

### 1. Strateji
Her karakteri tek tek işaretleyip şeridin sonuna kopyalama.
- Soldaki ilk `a` veya `b` karakteri büyük harf (`A` veya `B'`) ile işaretlenir.
- Şeridin sonuna (`#` sonrası) ilgili karakter yazılır.
- Başa dönülüp işlem tekrarlanır, sonunda işaretler geri düzeltilir.

### 2. Durum Sayısı
9 durum. Kopyalanan karakterin türünü (`a` mı `b` mi) hatırlamak için farklı kopyalama durumları kullanıldı.

### 3. Şerif Alfabesi Seçimi
`A` ve `B'` işaretleyici olarak kullanıldı.

### 4. Karmaşıklık
$O(n^2)$.

### 5. Hata Ayıklama Hikayesi
Ayraç (`#`) karakterinin başta olmaması durumunda ilk adımda eklenmesi mantığını kurmak başta kafa karıştırıcıydı.

---

## TM-4: Parantez Denetleyici (student_choice.yaml)

### 1. Strateji
"En İçteki Çifti Sil" stratejisi.
- İlk bulunan kapatma parantezi `)` işaretlenir.
- Sola gidilerek en yakın açma parantezi `(` bulunur ve işaretlenir.
- İşlem tüm şerit bitene kadar sürer.

### 2. Durum Sayısı
5 durum. Çok verimli bir algoritmadır.

### 3. Şerif Alfabesi Seçimi
`X` karakteri "eşleşmiş" parantezleri temsil eder.

### 4. Karmaşıklık
$O(n^2)$.

### 5. Hata Ayıklama Hikayesi
En zorlandığım kısım, `(` kalıp kalmadığını kontrol eden `q_verify` aşamasında başa dönme mantığıydı.
