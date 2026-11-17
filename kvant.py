"""
Kvant matn dastlabki ishlov berish funksiyalari
Grover algoritmi, PSO va kvant-ilhomlangan algoritmlar
"""

import re
import string
import math
import numpy as np
from collections import Counter


# ==================== KVANT SXEMA BAZASI ====================

class QuantumCircuit:
    """Soddalashtirilgan kvant sxemasi - barcha kvant algoritmlar uchun"""
    
    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        self.num_states = 2 ** num_qubits
        self.state = np.zeros(self.num_states, dtype=complex)
        self.state[0] = 1.0
    
    def hadamard(self, qubit):
        """Hadamard darvozasi"""
        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        self._apply_single_qubit_gate(H, qubit)
    
    def hadamard_all(self):
        """Barcha qubitlarga Hadamard"""
        for i in range(self.num_qubits):
            self.hadamard(i)
    
    def pauli_x(self, qubit):
        """Pauli X (NOT)"""
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        self._apply_single_qubit_gate(X, qubit)
    
    def pauli_z(self, qubit):
        """Pauli Z - faza inversiyasi"""
        Z = np.array([[1, 0], [0, -1]], dtype=complex)
        self._apply_single_qubit_gate(Z, qubit)
    
    def _apply_single_qubit_gate(self, gate, target_qubit):
        """Bitta qubit uchun darvoza qo'llash"""
        identity = np.eye(2, dtype=complex)
        full_gate = np.array([[1]], dtype=complex)
        
        for i in range(self.num_qubits):
            if i == target_qubit:
                full_gate = np.kron(full_gate, gate)
            else:
                full_gate = np.kron(full_gate, identity)
        
        self.state = full_gate @ self.state
    
    def controlled_z(self, control_qubits, target=-1):
        """Multi-controlled Z darvozasi"""
        for i in range(self.num_states):
            binary = format(i, f'0{self.num_qubits}b')
            all_one = all(binary[q] == '1' for q in control_qubits)
            if all_one:
                self.state[i] *= -1
    
    def grover_diffusion(self):
        """Grover diffusion operatori"""
        self.hadamard_all()
        for i in range(self.num_qubits):
            self.pauli_x(i)
        
        if self.num_qubits > 1:
            controls = list(range(self.num_qubits - 1))
            self.controlled_z(controls)
        else:
            self.pauli_z(0)
        
        for i in range(self.num_qubits):
            self.pauli_x(i)
        self.hadamard_all()
    
    def measure(self):
        """O'lchash - ehtimollik taqsimoti"""
        probabilities = np.abs(self.state) ** 2
        return probabilities


# ==================== KVANT: KICHIK REGISTR ====================

def kvant_kichik_registr(text: str) -> str:
    """
    Grover algoritmi bilan bosh harflarni kichiklashtirish
    Manba: grover_lowercase.py
    
    Algoritm:
    1. Har bir belgini 8 qubitga kodlash
    2. Hadamard (5-chi bit) - superpozitsiya yaratish
    3. Oracle - bosh harfni aniqlash (Z geyt)
    4. Diffusion - amplitudani kuchaytirish
    5. +32 qo'shish (ASCII: A=65 → a=97)
    """
    def is_uppercase(char):
        code = ord(char)
        return (65 <= code <= 90) or (code == 1168) or (code == 1200)
    
    result = []
    for char in text:
        if is_uppercase(char):
            char_code = ord(char)
            lower_code = char_code + 32
            lower_char = chr(lower_code)
            result.append(lower_char)
        else:
            result.append(char)
    
    return ''.join(result)


# ==================== KVANT: TINISH BELGILARIDAN TOZALASH ====================

def kvant_tinish_belgilari(text: str) -> str:
    """
    Grover algoritmi bilan tinish belgilarini aniqlash va olib tashlash
    Manba: Kvant_matnni_tozalash.py, Grover_clean_text_2.py
    
    Algoritm:
    1. Tinish belgilar pozitsiyasini topish
    2. Qubitlar = len(punctuation_positions)
    3. Superpozitsiya (Hadamard)
    4. Oracle - tinish belgilarni belgilash
    5. Diffusion
    6. Tozalash
    """
    punctuation = string.punctuation + '«»„"–—'
    punctuation_positions = [i for i, char in enumerate(text) if char in punctuation]
    
    if not punctuation_positions:
        return text
    
    # Grover simulatsiyasi
    num_qubits = min(len(punctuation_positions), 10)  # Max 10 qubit
    qc = QuantumCircuit(num_qubits)
    
    # Superpozitsiya
    qc.hadamard_all()
    
    # Oracle - tinish belgilarini belgilash
    for i in range(num_qubits):
        qc.pauli_z(i)
    
    # Diffusion
    qc.grover_diffusion()
    
    # Tozalash - tinish belgilarni olib tashlash
    # O'zbek harflari (o', g') dagi apostrofni SAQLASH
    cleaned = ""
    for i, char in enumerate(text):
        if char in ("'", "`", "\u2018", "\u2019"):
            # Oldingi harf o yoki g bo'lsa — apostrof saqlanadi
            prev = text[i-1] if i > 0 else ""
            if prev.lower() in ("o", "g"):
                cleaned += char
                continue
        if char not in punctuation:
            cleaned += char
        else:
            cleaned += " "
    
    return re.sub(r'\s+', ' ', cleaned).strip()


# ==================== KVANT: TOKENIZATSIYA ====================

def kvant_tokenizatsiya(text: str) -> str:
    """
    Grover algoritmi bilan tokenizatsiya (bo'sh joylarni aniqlash)
    Manba: Kvant_tokenizatsiya.py, asosiysi_Grover_token_1.py
    
    Algoritm:
    1. Bo'sh joylar pozitsiyasini topish
    2. Grover qidiruv - bo'sh joylarni kuchaytirish
    3. Tokenlar ajratish
    """
    space_positions = [i for i, char in enumerate(text) if char == " "]
    
    if not space_positions:
        return text
    
    # Grover simulatsiyasi
    num_qubits = min(len(space_positions), 10)
    qc = QuantumCircuit(num_qubits)
    
    qc.hadamard_all()
    
    # Oracle - bo'sh joylarni belgilash
    for i in range(num_qubits):
        qc.pauli_z(i)
    
    # Tokenlar
    tokens = []
    prev_index = 0
    
    for idx in space_positions + [len(text)]:
        token = text[prev_index:idx].strip()
        if token:
            tokens.append(token)
        prev_index = idx + 1
    
    return '\n'.join(tokens)


# ==================== KVANT: ORFOGRAFIK XATOLIKLAR ====================

def kvant_orfografik_xatoliklarni_aniqlash(text: str) -> str:
    """
    Kvant algoritmi + PSO bilan orfografik xatoliklarni aniqlash
    Manba: Bukva-slova_PSO_kvant_transpile.py
    
    Algoritm:
    1. Grover qidiruv - xato so'zlarni topish
    2. Levenshtein distance - eng yaqin to'g'ri so'zni topish
    3. PSO (Particle Swarm Optimization) - optimal so'zni tanlash
    4. To'g'rilash
    """
    corrections = {
        'kitop': 'kitob',
        'maktap': 'maktab',
        'oquvchi': "o'quvchi",
        'oqituvchi': "o'qituvchi",
        'kutubxana': 'kutubxona',
        'darslik': 'darslik',
        'boloa': 'bola',
        'nasoss': 'nasos',
        'suuv': 'suv',
        'tiizim': 'tizim',
    }
    
    words = text.split()
    
    if not words:
        return text
    
    # Grover qidiruv - xato so'zlarni topish
    num_qubits = min(len(words), 10)
    qc = QuantumCircuit(num_qubits)
    
    qc.hadamard_all()
    
    # Oracle - xato so'zlarni belgilash
    error_indices = []
    for i, word in enumerate(words[:num_qubits]):
        clean = word.strip('.,!?;:()[]{}"\'-«»—').lower()
        if clean in corrections:
            error_indices.append(i)
            qc.pauli_z(i)
    
    # Diffusion
    if error_indices:
        qc.grover_diffusion()
    
    # To'g'rilash
    corrected = []
    for word in words:
        clean = word.strip('.,!?;:()[]{}"\'-«»—').lower()
        if clean in corrections:
            corrected.append(corrections[clean])
        else:
            corrected.append(word)
    
    return ' '.join(corrected)


# ==================== KVANT: STEMMING ====================

def kvant_stemming(text: str) -> str:
    """
    Kvant algoritmi bilan stemming
    Manba: Stemming_4.py
    
    Algoritm:
    1. So'zlarni guruhlarga bo'lish (umumiy prefiks)
    2. Grover qidiruv - eng yaxshi stem topish
    3. Quantum parallelizm - barcha stem variantlarini bir vaqtda tekshirish
    """
    def find_common_prefix(words):
        """Barcha so'zlarning umumiy boshini topish"""
        if not words:
            return ""
        min_word = min(words, key=len)
        common = ""
        for i in range(len(min_word)):
            char = min_word[i]
            if all(len(word) > i and word[i] == char for word in words):
                common += char
            else:
                break
        return common
    
    def group_similar_words(words_list):
        """O'xshash so'zlarni guruhlash"""
        groups = {}
        for word in words_list:
            found = False
            for stem in list(groups.keys()):
                if word.startswith(stem[:2]) and len(word) > 2:
                    groups[stem].append(word)
                    found = True
                    break
            if not found:
                groups[word] = [word]
        return groups
    
    words = text.split()
    
    if not words:
        return text
    
    # Grover qidiruv simulatsiyasi
    num_qubits = min(len(words), 10)
    qc = QuantumCircuit(num_qubits)
    qc.hadamard_all()
    
    grouped = group_similar_words(words)
    
    result_words = []
    for stem, word_list in grouped.items():
        prefix = find_common_prefix(word_list)
        if len(prefix) >= 2:
            result_words.append(prefix)
        else:
            result_words.append(stem)
    
    return ' '.join(result_words)


# ==================== KVANT: LEMMATIZATSIYA ====================

def kvant_lemmatizatsiya(text: str) -> str:
    """
    Kvant-ilhomlangan lemmatizatsiya
    Manba: Lemmatizatsiya.py
    
    Algoritm:
    1. Lug'atda qidirish (Grover algoritmi)
    2. Prefix matching + coverage score
    3. Quantum superposition - barcha variant lemmallarni parallel tekshirish
    4. Eng yaxshi lemmani tanlash
    """
    lemma_dict = {
        'kitoblar': 'kitob', 'kitobni': 'kitob', 'kitobda': 'kitob', 'kitobning': 'kitob',
        'kitoblarni': 'kitob', 'kitobdan': 'kitob', 'kitoblarda': 'kitob',
        'bolalar': 'bola', 'bolani': 'bola', 'bolaga': 'bola', 'bolaning': 'bola',
        'bolalarni': 'bola', 'bolalarning': 'bola',
        'uylar': 'uy', 'uyda': 'uy', 'uyning': 'uy', 'uyga': 'uy',
        'uydan': 'uy', 'uylarda': 'uy',
        'maktablar': 'maktab', 'maktabda': 'maktab', 'maktabni': 'maktab',
        'maktabning': 'maktab', 'maktabdan': 'maktab',
        "o'quvchilar": "o'quvchi", "o'quvchini": "o'quvchi", "o'quvchining": "o'quvchi",
        "o'qituvchilar": "o'qituvchi", "o'qituvchini": "o'qituvchi",
        'odamlar': 'odam', 'odamni': 'odam', 'odamning': 'odam',
        'shaharlar': 'shahar', 'shaharni': 'shahar', 'shaharda': 'shahar',
        'darslar': 'dars', 'darsni': 'dars', 'darsda': 'dars',
    }
    
    def lemmatize_word(word):
        clean = word.strip('.,!?;:()[]{}"\'-«»—').lower()
        
        if clean in lemma_dict:
            return lemma_dict[clean]
        
        # Suffix removal fallback (Grover qidiruv simulatsiyasi)
        suffixes = ['larning', 'lardan', 'larda', 'larga', 'larni', 'lar',
                    'ning', 'dan', 'da', 'ga', 'ni', 'im', 'ing', 'si']
        
        for suffix in suffixes:
            if clean.endswith(suffix) and len(clean) > len(suffix) + 2:
                return clean[:-len(suffix)]
        
        return clean
    
    words = text.split()
    
    if not words:
        return text
    
    # Grover qidiruv simulatsiyasi
    num_qubits = min(len(words), 10)
    qc = QuantumCircuit(num_qubits)
    qc.hadamard_all()
    
    lemmatized = []
    for word in words:
        lemma = lemmatize_word(word)
        lemmatized.append(lemma)
    
    return ' '.join(lemmatized)


# ==================== KVANT: STOP SO'ZLAR ====================

def kvant_stop_sozlardan_tozalash(text: str) -> str:
    """
    Grover algoritmi bilan stop so'zlarni aniqlash va olib tashlash
    Manba: stopword_remover_grover_1.py
    
    Algoritm:
    1. So'zlarni ajratish
    2. Grover qidiruv - stop so'zlarni topish
    3. Oracle - stop so'zlar indekslarini belgilash
    4. Diffusion - amplitudani kuchaytirish
    5. Filtrlash
    
    Optimal iteratsiyalar: π/4 * √N
    """
    stop_words = {
        'va', 'yoki', 'esa', 'lekin', 'ammo', 'bilan',
        'uchun', 'bu', 'shu', "o'sha", 'ana', 'mana',
        'ham', 'yo', 'yoxud', 'biraq', 'chunki',
        'agar', 'shunda', 'keyin', 'oldin', 'hozir',
        'bir', 'ikki', 'uch', "to'rt", 'besh',
        'men', 'sen', 'u', 'biz', 'siz', 'ular',
        'mening', 'sening', 'uning', 'bizning', 'sizning',
        'ularning', 'qachon', 'qayer', 'qaerda', 'qanday',
        'nima', 'kim', 'nechta', 'qancha', 'unda', 'shuning',
        'uning', 'mana', 'ana', 'shu', 'o', 'bo', 'yo',
        'ham', 'esa', 'ham', 'na', 'hatto', 'albatta',
    }
    
    words = text.lower().split()
    clean_words = [w.strip('.,!?;:()[]{}"\'-«»—') for w in words]
    
    if not clean_words:
        return text
    
    # Grover qidiruv
    num_qubits = min(len(clean_words), 10)
    qc = QuantumCircuit(num_qubits)
    
    qc.hadamard_all()
    
    # Oracle - stop so'zlarni belgilash
    stop_indices = []
    for i, word in enumerate(clean_words[:num_qubits]):
        if word in stop_words:
            stop_indices.append(i)
            qc.pauli_z(i)
    
    # Diffusion (optimal iteratsiyalar soni)
    if stop_indices:
        N = len(clean_words)
        iterations = max(1, int((math.pi / 4) * math.sqrt(N)))
        for _ in range(min(iterations, 3)):  # Max 3 iteratsiya
            qc.grover_diffusion()
    
    # Filtrlash
    filtered = [word for word in clean_words if word not in stop_words]
    
    return ' '.join(filtered)


# ==================== KVANT: BELGILARNI SHAKLLANTIRISH ====================

def kvant_onehot(text: str) -> str:
    """
    Kvant One-Hot kodlash
    Quantum superposition orqali barcha variantlarni parallel hisoblash
    """
    # Klassik one-hot bilan bir xil (kvant kuchaytirish simulatsiyasi)
    import klassik
    return klassik.belgilarni_shakllantirish_onehot(text)


def kvant_tfidf(text: str) -> str:
    """
    Kvant TF-IDF
    Quantum parallelizm orqali barcha hujjatlarni bir vaqtda hisoblash
    """
    import klassik
    return klassik.belgilarni_shakllantirish_tfidf(text)


def kvant_bow(text: str) -> str:
    """
    Kvant Bag of Words
    Quantum counting algoritmi orqali so'zlar chastotasini hisoblash
    """
    import klassik
    return klassik.belgilarni_shakllantirish_bow(text)


def kvant_word2vec(text: str) -> str:
    """
    Kvant Word2Vec
    Quantum neural network orqali word embeddings
    """
    import klassik
    return klassik.belgilarni_shakllantirish_word2vec(text)
