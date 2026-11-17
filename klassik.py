"""
Klassik matn dastlabki ishlov berish funksiyalari
Professional stemming, lemmatization va boshqa NLP operatsiyalar
"""

import re
import string
import math
from collections import Counter


# ==================== KLASSIK STEMMING ====================

class UzbekStemmer:
    """O'zbek tili uchun professional stemmer"""
    
    def __init__(self):
        self.suffixes = [
            # Ko'plik + kelishik
            'lardan', 'lardan', 'larda', 'larda', 'larga', 'larga',
            'larni', 'larni', 'larning', 'larning',
            
            # Ko'plik
            'lar', 'lar',
            
            # Kelishiklar
            'dan', 'dan', 'ga', 'ga', 'da', 'da',
            'ni', 'ning', 'nikiga', 'nikida',
            
            # Egalik
            'larim', 'larim', 'laring', 'laring', 'larimiz', 'larimiz',
            'laringiz', 'laringiz', 'lari', 'lari',
            'im', 'ing', 'imiz', 'ingiz', 'si',
            
            # Fe'l shakllari
            'moqda', 'moqda', 'yapti', 'yapti', 'yotgan', 'yotgan',
            'ayotgan', 'ayotgan', 'yotir', 'yotir',
            'moq', 'moq', 'ish', 'ish', 'gan', 'gan',
            'di', 'di', 'ydi', 'ydi', 'yapti', 'yapti',
            
            # Qiyoslik, kichraytirish
            'roq', 'roq', 'gina', 'gina',
            
            # So'z yasovchi qo'shimchalar
            'lik', 'lik', 'chilik', 'chilik', 'chi', 'chi',
            'dor', 'dor', 'siz', 'siz', 'li', 'li',
            
            # Inkor
            'ma', 'ma',
        ]
        self.min_word_length = 3
    
    def stem(self, word):
        """So'zning asosini topish"""
        if len(word) <= self.min_word_length:
            return word
        
        original_word = word
        for suffix in sorted(set(self.suffixes), key=len, reverse=True):
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if len(stem) >= self.min_word_length:
                    return stem
        
        return original_word


# ==================== KLASSIK LEMMATIZATION ====================

class UzbekLemmatizer:
    """O'zbek tili uchun professional lemmatizer"""
    
    def __init__(self):
        self.lemma_dict = {
            'kitob': 'kitob', 'kitoblar': 'kitob', 'kitobni': 'kitob',
            'kitoblarni': 'kitob', 'kitobning': 'kitob', 'kitoblarning': 'kitob',
            'kitobda': 'kitob', 'kitoblarda': 'kitob', 'kitobdan': 'kitob',
            'kitoblardan': 'kitob', 'kitobga': 'kitob', 'kitoblarga': 'kitob',
            
            'bola': 'bola', 'bolalar': 'bola', 'bolani': 'bola',
            'bolalarni': 'bola', 'bolaning': 'bola', 'bolalarning': 'bola',
            
            'odam': 'odam', 'odamlar': 'odam', 'odamni': 'odam',
            
            "o'qimoq": "o'qimoq", "o'qiydi": "o'qimoq", "o'qiyapti": "o'qimoq",
            "o'qidi": "o'qimoq", "o'qigan": "o'qimoq",
            
            'yozmoq': 'yozmoq', 'yozadi': 'yozmoq', 'yozayotgan': 'yozmoq',
            'yozdi': 'yozmoq', 'yozgan': 'yozmoq',
            
            'kelmoq': 'kelmoq', 'keldi': 'kelmoq', 'kelgan': 'kelmoq',
            'kelayotgan': 'kelmoq', 'kelyapti': 'kelmoq',
            
            'yaxshi': 'yaxshi', 'yaxshiroq': 'yaxshi',
            'katta': 'katta', 'kattaroq': 'katta',
        }
        self.stemmer = UzbekStemmer()
    
    def lemmatize(self, word):
        word_lower = word.lower()
        if word_lower in self.lemma_dict:
            return self.lemma_dict[word_lower]
        return self.stemmer.stem(word_lower)


# ==================== ASOSIY KLASSIK FUNKSIYALAR ====================

def kichik_registrga(text: str) -> str:
    """Matnni kichik harflarga o'tkazish"""
    return text.lower()


def raqamlarni_matnga_aylantirish(text: str) -> str:
    """Raqamlarni matnga aylantirish (Lotin va Kiril)"""
    def number_to_words_latin(num_str):
        """Lotin alifbosida raqamlarni so'zlarga aylantirish"""
        try:
            num = int(num_str)
        except:
            return num_str
        
        if num == 0:
            return "nol"
        
        ones = ["", "bir", "ikki", "uch", "to'rt", "besh", "olti", "yetti", "sakkiz", "to'qqiz"]
        tens = ["", "o'n", "yigirma", "o'ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to'qson"]
        
        if num < 0:
            return "minus " + number_to_words_latin(str(abs(num)))
        
        if num < 10:
            return ones[num]
        elif num < 100:
            return (tens[num // 10] + (" " + ones[num % 10] if num % 10 != 0 else "")).strip()
        elif num < 1000:
            yuz = ones[num // 100] + " yuz"
            qoldiq = num % 100
            if qoldiq == 0:
                return yuz
            return yuz + " " + number_to_words_latin(str(qoldiq))
        elif num < 1000000:
            ming = number_to_words_latin(str(num // 1000)) + " ming"
            qoldiq = num % 1000
            if qoldiq == 0:
                return ming
            return ming + " " + number_to_words_latin(str(qoldiq))
        elif num < 1000000000:
            million = number_to_words_latin(str(num // 1000000)) + " million"
            qoldiq = num % 1000000
            if qoldiq == 0:
                return million
            return million + " " + number_to_words_latin(str(qoldiq))
        else:
            return num_str
    
    def number_to_words_cyrillic(num_str):
        """Kiril alifbosida raqamlarni so'zlarga aylantirish"""
        try:
            num = int(num_str)
        except:
            return num_str
        
        if num == 0:
            return "нол"
        
        ones = ["", "бир", "икки", "уч", "тўрт", "беш", "олти", "етти", "саккиз", "тўққиз"]
        tens = ["", "ўн", "йигирма", "ўттиз", "қирқ", "эллик", "олтмиш", "етмиш", "саксон", "тўқсон"]
        
        if num < 0:
            return "минус " + number_to_words_cyrillic(str(abs(num)))
        
        if num < 10:
            return ones[num]
        elif num < 100:
            return (tens[num // 10] + (" " + ones[num % 10] if num % 10 != 0 else "")).strip()
        elif num < 1000:
            yuz = ones[num // 100] + " юз"
            qoldiq = num % 100
            if qoldiq == 0:
                return yuz
            return yuz + " " + number_to_words_cyrillic(str(qoldiq))
        elif num < 1000000:
            ming = number_to_words_cyrillic(str(num // 1000)) + " минг"
            qoldiq = num % 1000
            if qoldiq == 0:
                return ming
            return ming + " " + number_to_words_cyrillic(str(qoldiq))
        elif num < 1000000000:
            million = number_to_words_cyrillic(str(num // 1000000)) + " миллион"
            qoldiq = num % 1000000
            if qoldiq == 0:
                return million
            return million + " " + number_to_words_cyrillic(str(qoldiq))
        else:
            return num_str
    
    # Matnni tekshirish - Lotin yoki Kiril
    has_cyrillic = bool(re.search('[а-яА-ЯЎўҚқҒғҲҳ]', text))
    
    # Raqamlarni almashtirish
    def replace_number(match):
        if has_cyrillic:
            return number_to_words_cyrillic(match.group())
        else:
            return number_to_words_latin(match.group())
    
    result = re.sub(r'\b\d+\b', replace_number, text)
    return result


def qisqartmalarni_kengaytirish(text: str) -> str:
    """Qisqartmalarni to'liq shaklga keltirish"""
    # Matnni tekshirish - Lotin yoki Kiril
    has_cyrillic = bool(re.search('[а-яА-ЯЎўҚқҒғҲҳ]', text))
    
    if has_cyrillic:
        # Kiril qisqartmalari
        abbreviations = {
            'ЎзР': "Ўзбекистон Республикаси",
            'ОАВ': "Оммавий ахборот воситалари",
            'МДҲ': "Мустақил Давлатлар Ҳамдўстлиги",
            'БМТ': "Бирлашган Миллатлар Ташкилоти",
            'ЕИ': "Европа Иттифоқи",
            'АҚШ': "Америка Қўшма Штатлари",
            'РФ': "Россия Федерацияси",
            'ш.': 'шаҳар',
            'т.': 'туман',
            'в.': 'вилоят',
            'к.': 'кўча',
            'м.': 'маҳалла',
            'й.': 'йил',
            'с.': 'сана',
            'проф.': 'профессор',
            'доц.': 'доцент',
            'ва ҳ.к.': 'ва ҳокозо',
            'ва б.': 'ва бошқалар',
        }
    else:
        # Lotin qisqartmalari
        abbreviations = {
            'OzR': "O'zbekiston Respublikasi",
            "O'zR": "O'zbekiston Respublikasi",
            'OAV': "Ommaviy axborot vositalari",
            'MDH': "Mustaqil Davlatlar Hamdo'stligi",
            'BMT': "Birlashgan Millatlar Tashkiloti",
            'YeI': "Yevropa Ittifoqi",
            'AQSh': "Amerika Qo'shma Shtatlari",
            'AQSH': "Amerika Qo'shma Shtatlari",
            'RF': "Rossiya Federatsiyasi",
            'sh.': 'shahar',
            't.': 'tuman',
            'v.': 'viloyat',
            'k.': "ko'cha",
            'm.': 'mahalla',
            'y.': 'yil',
            's.': 'sana',
            'oy.': 'oy',
            'prof.': 'professor',
            'dots.': 'dotsent',
            'PhD': 'falsafa doktori',
            'DSc': 'fan doktori',
            'va h.k.': 'va hokazo',
            'va b.': 'va boshqalar',
            'va sh.k.': 'va shunga o\'xshashlar',
            'b-n': 'bilan',
            'b/n': 'bilan',
        }
    
    result = text
    for abbr, full in abbreviations.items():
        pattern = r'\b' + re.escape(abbr) + r'\b'
        result = re.sub(pattern, full, result, flags=re.IGNORECASE)
    
    return result


def tinish_belgilaridan_tozalash(text: str) -> str:
    """Matndagi tinish belgilarini olib tashlash + URL olib tashlash"""
    # Avval URLlarni olib tashlash
    # http://, https://, www. bilan boshlanuvchi URLlar
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'www\.\S+', ' ', text)
    # Email manzillar
    text = re.sub(r'\S+@\S+', ' ', text)
    
    # O'zbek harflarini saqlab tinish belgilarini olib tashlash:
    # o', g', O', G', o`/g` kabi harflardagi apostrof SAQLANADI.
    # Avval o'zbek harflarini vaqtincha placeholder bilan himoyalash
    text = re.sub(r"([oOgG])'", lambda m: m.group(1) + '\x00', text)  # apostrof → \x00
    text = re.sub(r"([oOgG])`", lambda m: m.group(1) + '\x00', text)  # teskari apostrof

    # Tinish belgilarini bo'sh joy bilan almashtirish
    punctuation = string.punctuation + '«»„"—–\u2018\u2019\u201a\u2026'
    translator = str.maketrans(punctuation, ' ' * len(punctuation))
    cleaned = text.translate(translator)

    # Placeholderni apostrofga qaytarish
    cleaned = cleaned.replace('\x00', "'")
    
    # Raqamlarni matnga aylantirish
    cleaned = raqamlarni_matnga_aylantirish(cleaned)
    
    # Qisqartmalarni kengaytirish
    cleaned = qisqartmalarni_kengaytirish(cleaned)
    
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def tokenizatsiya(text: str) -> str:
    """Matnni so'zlarga bo'lish (tokenizatsiya)"""
    words = text.split()
    return '\n'.join(words)


def stemming(text: str) -> str:
    """Professional stemming - so'zlarning asosini topish"""
    stemmer = UzbekStemmer()
    words = text.split()
    stemmed_words = [stemmer.stem(word) for word in words]
    return ' '.join(stemmed_words)


def lemmatizatsiya(text: str) -> str:
    """Professional lemmatization - so'zlarni lug'at shakliga keltirish"""
    lemmatizer = UzbekLemmatizer()
    words = text.split()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(lemmatized_words)


def stop_sozlardan_tozalash(text: str) -> str:
    """Stop so'zlarni olib tashlash"""
    stop_words = {
        'va', 'yoki', 'esa', 'lekin', 'ammo', 'bilan', 
        'uchun', 'bu', 'shu', "o'sha", 'ana', 'mana',
        'ham', 'yo', 'yoxud', 'biraq', 'chunki', 
        'agar', 'shunda', 'keyin', 'oldin', 'hozir',
        'bir', 'ikki', 'uch', "to'rt", 'besh',
        'men', 'sen', 'u', 'biz', 'siz', 'ular',
    }
    
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)


def orfografik_xatoliklarni_aniqlash(text: str) -> str:
    """Orfografik xatoliklarni aniqlash va to'g'rilash"""
    corrections = {
        'kitop': 'kitob',
        'maktap': 'maktab',
        'odam': 'odam',
        'salom': 'salom',
        'rahmat': 'rahmat',
        'xayr': 'hayr',
        'kutubxona': 'kutubxona',
        'darslik': 'darslik',
        'oquvchi': "o'quvchi",
        'oqituvchi': "o'qituvchi",
    }
    
    words = text.split()
    corrected = []
    
    for word in words:
        clean = word.strip('.,!?;:()[]{}"\'\'-«»—').lower()
        if clean in corrections:
            corrected.append(corrections[clean])
        else:
            corrected.append(word)
    
    return ' '.join(corrected)


# ==================== BELGILARNI SHAKLLANTIRISH ====================

def belgilarni_shakllantirish_onehot(text: str) -> str:
    """One-hot kodlash"""
    words = text.lower().split()
    unique_words = sorted(set(words))
    
    result = "=" * 60 + "\n"
    result += "ONE-HOT ENCODING NATIJASI\n"
    result += "=" * 60 + "\n\n"
    
    result += "📚 SO'ZLAR LUG'ATI:\n"
    result += "-" * 60 + "\n"
    for i, word in enumerate(unique_words):
        result += f"{i:3d}. {word}\n"
    
    result += f"\nJami so'zlar: {len(unique_words)} ta\n"
    result += "\n" + "=" * 60 + "\n"
    result += "\n📢 ONE-HOT VEKTORLAR:\n"
    result += "-" * 60 + "\n\n"
    
    for word in words:
        vector = ['0'] * len(unique_words)
        index = unique_words.index(word)
        vector[index] = '1'
        result += f"{word:15s} → [{', '.join(vector)}]\n"
    
    result += "\n" + "=" * 60 + "\n"
    result += f"✅ Vektor uzunligi: {len(unique_words)}\n"
    
    return result


def belgilarni_shakllantirish_tfidf(text: str) -> str:
    """TF-IDF hisoblash"""
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if not sentences:
        return "⚠️ Matn bo'sh!"
    
    docs = [sent.lower().split() for sent in sentences]
    all_words = sorted(set(word for doc in docs for word in doc))
    
    result = "=" * 70 + "\n"
    result += "TF-IDF NATIJASI\n"
    result += "=" * 70 + "\n\n"
    
    idf = {}
    num_docs = len(docs)
    
    result += "📊 IDF QIYMATlARI:\n"
    result += "-" * 70 + "\n"
    
    for word in all_words:
        df = sum(1 for doc in docs if word in doc)
        idf_value = math.log(num_docs / df) if df > 0 else 0
        idf[word] = idf_value
        result += f"{word:<20} {df:<10} {idf_value:<15.4f}\n"
    
    result += "\n✅ TF-IDF hisoblash yakunlandi!\n"
    
    return result


def belgilarni_shakllantirish_bow(text: str) -> str:
    """Bag of Words"""
    words = text.lower().split()
    word_freq = Counter(words)
    
    result = "=" * 60 + "\n"
    result += "BAG OF WORDS NATIJASI\n"
    result += "=" * 60 + "\n\n"
    
    result += "📚 SO'ZLAR LUG'ATI:\n"
    result += "-" * 60 + "\n"
    
    sorted_words = sorted(word_freq.keys())
    for i, word in enumerate(sorted_words):
        result += f"{i:3d}. {word}\n"
    
    result += f"\nJami noyob so'zlar: {len(sorted_words)} ta\n"
    
    result += "\n📊 CHASTOTA:\n"
    result += "-" * 60 + "\n"
    
    total_words = len(words)
    for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_words) * 100
        result += f"{word:<20} {count:<15} {percentage:6.2f}%\n"
    
    return result


def belgilarni_shakllantirish_word2vec(text: str) -> str:
    """Word2Vec simulyatsiyasi"""
    words = text.lower().split()
    unique_words = sorted(set(words))
    
    result = "=" * 70 + "\n"
    result += "WORD2VEC SIMULYATSIYASI\n"
    result += "=" * 70 + "\n\n"
    
    result += "⚠️ To'liq Word2Vec uchun 'gensim' kerak.\n\n"
    
    vector_size = 100
    result += f"📊 Parametrlar:\n"
    result += f"   Vector size: {vector_size}\n"
    result += f"   Jami so'zlar: {len(words)}\n"
    result += f"   Noyob so'zlar: {len(unique_words)}\n"
    
    return result
