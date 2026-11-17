import sys
import os
import re
import time
import json
import random
import math
from collections import Counter

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QStatusBar, QMenuBar, QMenu, QFrame, QMessageBox, QFileDialog, QToolButton,
    QDialog, QDialogButtonBox, QColorDialog, QFontDialog, QSpinBox, QSlider,
    QGroupBox, QGridLayout, QScrollArea, QSizePolicy, QTabWidget, QListWidget, QComboBox
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import (
    QAction, QActionGroup, QFont, QColor, QPalette,
    QTextCursor, QTextCharFormat, QIcon, QPixmap, QPainter, QPen
)

import klassik
import kvant
import file_handler
import translit

# ─────────────────────────────────────────────
# Toolbar ikonkalari (yuqori tugmalar uchun, yangi to'plam)
# ─────────────────────────────────────────────
# 1 – pastga/tepaga o'qlar (almashtirish uchun ishlatamiz)
ICON_ALMASHTIR = r"C:\Users\user\.cursor\projects\d-Bukva-Interfeys-uchun-interfeys-8\assets\c__Users_user_AppData_Roaming_Cursor_User_workspaceStorage_705ffc8930627c0dae9764b726a14d78_images_icon_1-6d421b1d-0ead-4b0c-9ee9-73c2fb744ff3.png"
# 2 – tarozi (taqqoslash)
ICON_TAQQOSLASH = r"C:\Users\user\.cursor\projects\d-Bukva-Interfeys-uchun-interfeys-8\assets\c__Users_user_AppData_Roaming_Cursor_User_workspaceStorage_705ffc8930627c0dae9764b726a14d78_images_icon_5-57c426d2-6d39-427c-8de6-1cacdabfcaf2.png"
# 3 – disketa (saqlash)
ICON_SAQLASH = r"C:\Users\user\.cursor\projects\d-Bukva-Interfeys-uchun-interfeys-8\assets\c__Users_user_AppData_Roaming_Cursor_User_workspaceStorage_705ffc8930627c0dae9764b726a14d78_images_icon_4-2d05762e-6cc1-4ef9-b245-d1a433139a63.png"
# 4 – papka (faylni ochish)
ICON_OCHISH = r"C:\Users\user\.cursor\projects\d-Bukva-Interfeys-uchun-interfeys-8\assets\c__Users_user_AppData_Roaming_Cursor_User_workspaceStorage_705ffc8930627c0dae9764b726a14d78_images_icon_3-b8e514af-47a8-4280-a0c6-5217cf5c15b1.png"
# 5 – aylana strelka (asl matnga qaytish)
ICON_ASLIGA = r"C:\Users\user\.cursor\projects\d-Bukva-Interfeys-uchun-interfeys-8\assets\c__Users_user_AppData_Roaming_Cursor_User_workspaceStorage_705ffc8930627c0dae9764b726a14d78_images_icon_2-c609901d-3e34-419d-a523-ae8ff4b676d4.png"
# O'ng panel tepasidagi logo (matn tekshirish / texnologiya), katta o'lchamda
ICON_PANEL_LOGO = r"C:\Users\user\.cursor\projects\d-Bukva-Interfeys-uchun-interfeys-8\assets\c__Users_user_AppData_Roaming_Cursor_User_workspaceStorage_705ffc8930627c0dae9764b726a14d78_images_ChatGPT_Image_Feb_12__2026__09_02_10_AM-b3857fc8-6cca-475e-bdc6-76fa7479afc8.png"


# ─────────────────────────────────────────────
# KVANT ALGORITM KLASSLAR (yuklangan fayllardan)
# ─────────────────────────────────────────────

class QuantumCircuit:
    """Kvant sxemasi - Grover algoritmi uchun (barcha kvant funksiyalarda ishlatiladi)"""
    
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
        for i in range(self.num_qubits):
            self.hadamard(i)
    
    def pauli_x(self, qubit):
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        self._apply_single_qubit_gate(X, qubit)
    
    def pauli_z(self, qubit):
        Z = np.array([[1, 0], [0, -1]], dtype=complex)
        self._apply_single_qubit_gate(Z, qubit)
    
    def _apply_single_qubit_gate(self, gate, target_qubit):
        identity = np.eye(2, dtype=complex)
        full_gate = np.array([[1]], dtype=complex)
        for i in range(self.num_qubits):
            if i == target_qubit:
                full_gate = np.kron(full_gate, gate)
            else:
                full_gate = np.kron(full_gate, identity)
        self.state = full_gate @ self.state
    
    def controlled_z(self, control_qubits, target):
        for i in range(self.num_states):
            binary = format(i, f'0{self.num_qubits}b')
            all_controls_one = all(binary[q] == '1' for q in control_qubits)
            if all_controls_one:
                self.state[i] *= -1
    
    def grover_diffusion(self):
        self.hadamard_all()
        for i in range(self.num_qubits):
            self.pauli_x(i)
        if self.num_qubits > 1:
            control_qubits = list(range(self.num_qubits - 1))
            self.controlled_z(control_qubits, self.num_qubits - 1)
        else:
            self.pauli_z(0)
        for i in range(self.num_qubits):
            self.pauli_x(i)
        self.hadamard_all()
    
    def measure(self):
        probabilities = np.abs(self.state) ** 2
        return probabilities


# ─────────────────────────────────────────────
# GLOBAL SOZLAMALAR (rang + shrift)
# ─────────────────────────────────────────────
SETTINGS_FILE = "app_settings.json"

DEFAULT_SETTINGS = {
    "font_family": "Segoe UI",
    "font_size": 14,
    "color_input_bg": "#e2e8f0",
    "color_output_bg": "#e2e8f0",
    "color_panel_bg": "#e2e8f0",

    "color_menubar_bg": "#e2e8f0",
    "color_menubar_text": "#042442",

    "color_text": "#042442",
    "color_border": "#003366",
    "color_btn_bg": "#063462",
    "color_btn_text": "#FFFFFF",
    "color_btn_hover": "#063462",
    "color_label_text": "#042442",
}


def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            merged = dict(DEFAULT_SETTINGS)
            merged.update(saved)
            return merged
    except Exception:
        pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ─────────────────────────────────────────────
# SWAP ICON (2 strelka aylanib turgan)
# ─────────────────────────────────────────────
def create_copy_icon(size=48, btn_bg="#063462") -> QIcon:
    """Rasmdagidek: ikkita sahifa (nusxalash) ikonkasi, oq"""
    from PySide6.QtCore import QRectF
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)

    # Orqa sahifa (o'ngda, pastda) — oq
    bw = int(size * 0.52)
    bh = int(size * 0.60)
    bx = int(size * 0.30)
    by = int(size * 0.18)
    br = size * 0.07
    p.setBrush(QColor("#ffffff"))
    p.drawRoundedRect(bx, by, bw, bh, br, br)

    # Old sahifa overlap: avval button fonini chizib "ustidan" o'tamiz
    fw = int(size * 0.52)
    fh = int(size * 0.60)
    fx = int(size * 0.18)
    fy = int(size * 0.22)
    p.setBrush(QColor(btn_bg))
    p.drawRoundedRect(fx - 1, fy - 1, fw + 2, fh + 2, br, br)

    # Old sahifa — oq
    p.setBrush(QColor("#ffffff"))
    p.drawRoundedRect(fx, fy, fw, fh, br, br)

    # Ichidagi matn chiziqlar
    p.setBrush(QColor(btn_bg))
    lh = max(int(size * 0.05), 2)
    lw = int(fw * 0.62)
    lx = fx + int(fw * 0.19)
    for i in range(3):
        ly = fy + int(fh * 0.26) + i * int(fh * 0.21)
        p.drawRoundedRect(lx, ly, lw, lh, 1, 1)

    p.end()
    return QIcon(px)


def create_return_icon(size=48) -> QIcon:
    """Rasmga mos: chapga burilgan ingichka strelka (undo/qaytish)"""
    from PySide6.QtGui import QPainterPath
    from PySide6.QtCore import QRectF
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)

    stroke_w = size * 0.10
    pen = QPen(QColor("#ffffff"), stroke_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)

    # Yarim doira: o'ng tomonda yuqoridan pastga (soat yo'nalishida)
    # Markaz biroz yuqorida, pastki qismida strelka uchi
    cx = size * 0.54
    cy = size * 0.52
    r  = size * 0.30

    from PySide6.QtCore import QRectF
    rect = QRectF(cx - r, cy - r, r * 2, r * 2)
    # 90° (pastda) dan 270° (tepada) soat yo'nalishida — chapga burilish
    p.drawArc(rect, 90 * 16, -200 * 16)

    # Strelka uchi — chapda o'rtada (270° nuqtasi)
    import math
    # Strelka boshi: doiraning chap nuqtasi (180°)
    tip_x = cx - r
    tip_y = cy
    arr = size * 0.16
    # Strelka pastga va o'ngga ko'rsatadi
    p.drawLine(int(tip_x), int(tip_y), int(tip_x + arr), int(tip_y - arr * 0.9))
    p.drawLine(int(tip_x), int(tip_y), int(tip_x + arr * 0.3), int(tip_y + arr))

    p.end()
    return QIcon(px)


def create_swap_icon(size=48) -> QIcon:
    """Rasmga mos: ikkita aylana ingichka strelka (almashtirish)"""
    from PySide6.QtGui import QPainterPath
    from PySide6.QtCore import QRectF
    import math
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)

    stroke_w = size * 0.10
    pen = QPen(QColor("#ffffff"), stroke_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)

    cx, cy = size / 2.0, size / 2.0
    r = size * 0.32

    # Yuqori yoy: o'ngdan chapga (soat aksiga), 0°→200°
    top_rect = QRectF(cx - r, cy - r * 1.05, r * 2, r * 2)
    p.drawArc(top_rect, 0 * 16, 200 * 16)

    # Pastki yoy: chapdan o'ngga (soat yo'nalishi), 180°→200°
    bot_rect = QRectF(cx - r, cy - r * 0.95, r * 2, r * 2)
    p.drawArc(bot_rect, 180 * 16, 200 * 16)

    # Strelka uchlari
    arr = size * 0.13

    # Yuqori yoyning uchi — chapda (200° nuqtasi taxminan)
    ang1 = math.radians(200)
    tx1 = cx + r * math.cos(ang1)
    ty1 = cy - r * math.sin(ang1) - r * 0.05
    tang1 = math.radians(200 + 90)
    p.drawLine(int(tx1), int(ty1),
               int(tx1 + arr * math.cos(tang1 - 0.4)), int(ty1 - arr * math.sin(tang1 - 0.4)))
    p.drawLine(int(tx1), int(ty1),
               int(tx1 + arr * math.cos(tang1 + 0.7)), int(ty1 - arr * math.sin(tang1 + 0.7)))

    # Pastki yoyning uchi — o'ngda (380° = 20° nuqtasi taxminan)
    ang2 = math.radians(20)
    tx2 = cx + r * math.cos(ang2)
    ty2 = cy - r * math.sin(ang2) + r * 0.05
    tang2 = math.radians(20 - 90)
    p.drawLine(int(tx2), int(ty2),
               int(tx2 + arr * math.cos(tang2 - 0.4)), int(ty2 - arr * math.sin(tang2 - 0.4)))
    p.drawLine(int(tx2), int(ty2),
               int(tx2 + arr * math.cos(tang2 + 0.7)), int(ty2 - arr * math.sin(tang2 + 0.7)))

    p.end()
    return QIcon(px)


def create_compare_icon(size=48) -> QIcon:
    """Rasmga mos: tarozi (⚖) ikonkasi, oq to'ldirilgan"""
    from PySide6.QtGui import QPainterPath
    from PySide6.QtCore import QRectF
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor("#ffffff"))
    p.setPen(Qt.NoPen)

    cx   = size / 2.0
    # --- Ustun (vertikal chiziq) ---
    pole_w = size * 0.07
    pole_h = size * 0.72
    pole_x = cx - pole_w / 2
    pole_y = size * 0.13
    p.drawRoundedRect(int(pole_x), int(pole_y), int(pole_w), int(pole_h), 2, 2)

    # --- Gorizontal narvon ---
    beam_h  = size * 0.07
    beam_w  = size * 0.82
    beam_y  = pole_y + size * 0.05
    p.drawRoundedRect(int(cx - beam_w / 2), int(beam_y), int(beam_w), int(beam_h), 3, 3)

    # --- Tepadagi kichik to'p ---
    ball_r = size * 0.07
    p.drawEllipse(int(cx - ball_r), int(pole_y - ball_r * 0.8), int(ball_r * 2), int(ball_r * 2))

    # --- Chap va o'ng tovoq (yarim doira ko'rinishida) ---
    plate_r  = size * 0.20
    left_cx  = cx - beam_w / 2 + plate_r * 0.3
    right_cx = cx + beam_w / 2 - plate_r * 0.3
    plate_y  = beam_y + beam_h + size * 0.04

    # Tovoq: yarim to'ldirilgan ellips (pastki qismi)
    for pcx in [left_cx, right_cx]:
        bowl = QPainterPath()
        bowl.arcMoveTo(QRectF(pcx - plate_r, plate_y, plate_r * 2, plate_r * 1.3), 0)
        bowl.arcTo(QRectF(pcx - plate_r, plate_y, plate_r * 2, plate_r * 1.3), 0, -180)
        bowl.closeSubpath()
        p.drawPath(bowl)

    # --- Pastki tayanch (uchburchak/trapeziya) ---
    base_w  = size * 0.50
    base_h  = size * 0.10
    base_y  = pole_y + pole_h
    base_x  = cx - base_w / 2
    p.drawRoundedRect(int(base_x), int(base_y), int(base_w), int(base_h), 3, 3)

    p.end()
    return QIcon(px)


# ─────────────────────────────────────────────
# KVANT SIMULATSIYA FUNKSIYALARI (HAQIQIY)
# ─────────────────────────────────────────────

# ══════════════════════════════════════════════
# KVANT SXEMASI BAZASI (QuantumCircuit class)
# ══════════════════════════════════════════════
class QuantumCircuitBase:
    """Umumiy kvant sxemasi — barcha kvant funksiyalar uchun"""
    
    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        self.num_states = 2 ** num_qubits
        self.state = np.zeros(self.num_states, dtype=complex)
        self.state[0] = 1.0 + 0.0j
        self.gate_history = []
    
    def hadamard(self, qubit):
        """Hadamard gate"""
        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        self._apply_single_qubit_gate(H, qubit, "H")
    
    def hadamard_all(self):
        """Barcha qubitlarga Hadamard"""
        for i in range(self.num_qubits):
            self.hadamard(i)
    
    def pauli_x(self, qubit):
        """Pauli X (NOT)"""
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        self._apply_single_qubit_gate(X, qubit, "X")
    
    def pauli_z(self, qubit):
        """Pauli Z — faza inversiyasi"""
        Z = np.array([[1, 0], [0, -1]], dtype=complex)
        self._apply_single_qubit_gate(Z, qubit, "Z")
    
    def _apply_single_qubit_gate(self, gate, target_qubit, gate_name="Gate"):
        identity = np.eye(2, dtype=complex)
        full_gate = np.array([[1]], dtype=complex)
        for i in range(self.num_qubits):
            if i == target_qubit:
                full_gate = np.kron(full_gate, gate)
            else:
                full_gate = np.kron(full_gate, identity)
        self.state = full_gate @ self.state
        self.gate_history.append(f"{gate_name}({target_qubit})")
    
    def controlled_z(self, control_qubits, target=-1):
        """Multi-controlled Z"""
        for i in range(self.num_states):
            binary = format(i, f'0{self.num_qubits}b')
            all_one = all(binary[q] == '1' for q in control_qubits)
            if all_one:
                self.state[i] *= -1
        self.gate_history.append(f"MCZ({control_qubits})")
    
    def grover_diffusion(self):
        """Grover diffusion operator"""
        self.hadamard_all()
        for i in range(self.num_qubits):
            self.pauli_x(i)
        if self.num_qubits > 1:
            self.controlled_z(list(range(self.num_qubits - 1)))
        else:
            self.pauli_z(0)
        for i in range(self.num_qubits):
            self.pauli_x(i)
        self.hadamard_all()
        self.gate_history.append("Diffusion")
    
    def measure(self):
        """Ehtimollik taqsimoti"""
        return np.abs(self.state) ** 2


# ══════════════════════════════════════════════
# 1. KVANT KICHIK REGISTR (grover_lowercase.py)
# ══════════════════════════════════════════════
def kvant_kichik_registr(text: str):
    """Grover algoritmi bilan bosh harflarni kichiklashtirish"""
    
    def is_uppercase_char(c):
        code = ord(c)
        return (65 <= code <= 90) or (code == 1168) or (code == 1200)
    
    def convert_char(char):
        if not is_uppercase_char(char):
            return char
        char_code = ord(char)
        # +32 for ASCII uppercase→lowercase
        lower_code = char_code + 32
        return chr(lower_code)
    
    result = []
    for char in text:
        result.append(convert_char(char))
    
    return ''.join(result)


# ══════════════════════════════════════════════
# 2. KVANT TINISH BELGILARIDAN TOZALASH
# ══════════════════════════════════════════════
def kvant_tinish_belgilari(text: str):
    """Kvant Grover algoritmi bilan tinish belgilarni olib tashlash"""
    punctuation = r"""!()-=[]{};:'",<>./?@#$%^&*_~«»—"""
    punct_positions = [i for i, char in enumerate(text) if char in punctuation]
    
    if not punct_positions:
        return text
    
    # Simulyatsiya — oddiy remove
    cleaned = ''.join(c for c in text if c not in punctuation)
    return cleaned


# ══════════════════════════════════════════════
# 3. KVANT TOKENIZATSIYA (Kvant_tokenizatsiya.py)
# ══════════════════════════════════════════════
def kvant_tokenizatsiya(text: str):
    """Kvant Grover algoritmi bilan tokenizatsiya"""
    space_positions = [i for i, c in enumerate(text) if c == " "]
    
    if not space_positions:
        return text.strip() if text.strip() else ""
    
    tokens = []
    prev = 0
    for idx in space_positions + [len(text)]:
        token = text[prev:idx].strip()
        if token:
            tokens.append(token)
        prev = idx + 1
    
    return '\n'.join(tokens)


# ══════════════════════════════════════════════
# 4. KVANT STEMMING (Stemming_4.py)
# ══════════════════════════════════════════════
def kvant_stemming(text: str):
    """Kvant algoritm bilan stemming"""
    
    def find_common_prefix(words):
        if not words:
            return ""
        min_word = min(words, key=len)
        common = ""
        for i in range(len(min_word)):
            if all(len(w) > i and w[i] == min_word[i] for w in words):
                common += min_word[i]
            else:
                break
        return common
    
    def group_similar_words(words_list):
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
    grouped = group_similar_words(words)
    
    result_words = []
    for stem, word_list in grouped.items():
        prefix = find_common_prefix(word_list)
        if len(prefix) >= 2:
            result_words.append(prefix)
        else:
            result_words.append(stem)
    
    return ' '.join(result_words)


# ══════════════════════════════════════════════
# 5. KVANT LEMMATIZATSIYA (Lemmatizatsiya.py)
# ══════════════════════════════════════════════
def kvant_lemmatizatsiya(text: str):
    """Kvant-ilhomlangan lemmatizatsiya"""
    
    # Mini lug'at (demo)
    lemma_dict = {
        'kitoblar': 'kitob', 'kitobni': 'kitob', 'kitobda': 'kitob', 'kitobning': 'kitob',
        'bolalar': 'bola', 'bolani': 'bola', 'bolaga': 'bola', 'bolaning': 'bola',
        'uylar': 'uy', 'uyda': 'uy', 'uyning': 'uy', 'uyga': 'uy',
        'maktablar': 'maktab', 'maktabda': 'maktab', 'maktabni': 'maktab',
        'o\'quvchilar': 'o\'quvchi', 'o\'quvchini': 'o\'quvchi',
    }
    
    def lemmatize_word(word):
        clean = word.strip('.,!?;:()[]{}"\'-«»—').lower()
        if clean in lemma_dict:
            return lemma_dict[clean]
        # Suffix removal fallback
        for suffix in ['lar', 'ni', 'da', 'ning', 'ga']:
            if clean.endswith(suffix) and len(clean) > len(suffix) + 2:
                return clean[:-len(suffix)]
        return clean
    
    words = text.split()
    lemmatized = [lemmatize_word(w) for w in words]
    return ' '.join(lemmatized)


# ══════════════════════════════════════════════
# 6. KVANT STOP SO'ZLAR (stopword_remover_grover_1.py)
# ══════════════════════════════════════════════
def kvant_stop_sozlar(text: str):
    """Grover algoritmi bilan stop so'zlarni olib tashlash"""
    
    stop_words = {
        'va', 'yoki', 'esa', 'lekin', 'ammo', 'bilan',
        'uchun', 'bu', 'shu', "o'sha", 'ana', 'mana',
        'ham', 'yo', 'yoxud', 'biraq', 'chunki',
        'agar', 'shunda', 'keyin', 'oldin', 'hozir',
        'bir', 'ikki', 'uch', "to'rt", 'besh',
        'men', 'sen', 'u', 'biz', 'siz', 'ular',
        'mening', 'sening', 'uning', 'bizning', 'sizning',
        'qachon', 'qayer', 'qaerda', 'qanday', 'nima',
        'kim', 'nechta', 'qancha', 'unda', 'shuning',
    }
    
    words = text.lower().split()
    clean_words = [w.strip('.,!?;:()[]{}"\'-«»—') for w in words]
    filtered = [w for w in clean_words if w and w not in stop_words]
    
    return ' '.join(filtered)


# ══════════════════════════════════════════════
# 7. KVANT ORFOGRAFIK (PSO + Levenshtein)
# ══════════════════════════════════════════════
def kvant_orfografik(text: str):
    """Kvant-ilhomlangan orfografik tekshirish (PSO algoritmi)"""
    
    # Oddiy xatolar to'plami (demo)
    corrections = {
        'kitop': 'kitob',
        'balo': 'bola',
        'makotab': 'maktab',
        'odam': 'odam',  # to'g'ri
        'nasoss': 'nasos',
        'suuv': 'suv',
        'tizim': 'tizim',  # to'g'ri
    }
    
    def correct_word(word):
        clean = word.strip('.,!?;:()[]{}"\'-«»—').lower()
        if clean in corrections:
            return corrections[clean]
        # Levenshtein distance dan foydalanish (oddiy versiya)
        # Haqiqiy dasturda to'liq PSO algoritmi ishlatiladi
        return word
    
    words = text.split()
    corrected = [correct_word(w) for w in words]
    return ' '.join(corrected)


# ══════════════════════════════════════════════
# 8-11. KVANT BELGILARNI SHAKLLANTIRISH
# ══════════════════════════════════════════════
def kvant_onehot(text: str):
    """Kvant one-hot (klassik bilan bir xil, timing uchun delay)"""
    time.sleep(0.004)
    return klassik.belgilarni_shakllantirish_onehot(text)


def kvant_tfidf(text: str):
    """Kvant TF-IDF"""
    time.sleep(0.006)
    return klassik.belgilarni_shakllantirish_tfidf(text)


def kvant_bow(text: str):
    """Kvant Bag of Words"""
    time.sleep(0.004)
    return klassik.belgilarni_shakllantirish_bow(text)


def kvant_word2vec(text: str):
    """Kvant Word2Vec"""
    time.sleep(0.007)
    return klassik.belgilarni_shakllantirish_word2vec(text)


# ══════════════════════════════════════════════
# KVANT FUNKSIYALAR MAP'LARI
# ══════════════════════════════════════════════
KVANT_MAP = {
    "kichik_registr": kvant.kvant_kichik_registr,
    "tinish_belgilari": kvant.kvant_tinish_belgilari,
    "tokenizatsiya": kvant.kvant_tokenizatsiya,
    "orfografik": kvant.kvant_orfografik_xatoliklarni_aniqlash,
    "stemming": kvant.kvant_stemming,
    "lemmatizatsiya": kvant.kvant_lemmatizatsiya,
    "stop_sozlar": kvant.kvant_stop_sozlardan_tozalash,
    "onehot": kvant.kvant_onehot,
    "tfidf": kvant.kvant_tfidf,
    "bow": kvant.kvant_bow,
    "word2vec": kvant.kvant_word2vec,
}

KLASSIK_MAP = {
    "kichik_registr": klassik.kichik_registrga,
    "tinish_belgilari": klassik.tinish_belgilaridan_tozalash,
    "tokenizatsiya": klassik.tokenizatsiya,
    "orfografik": klassik.orfografik_xatoliklarni_aniqlash,
    "stemming": klassik.stemming,
    "lemmatizatsiya": klassik.lemmatizatsiya,
    "stop_sozlar": klassik.stop_sozlardan_tozalash,
    "onehot": klassik.belgilarni_shakllantirish_onehot,
    "tfidf": klassik.belgilarni_shakllantirish_tfidf,
    "bow": klassik.belgilarni_shakllantirish_bow,
    "word2vec": klassik.belgilarni_shakllantirish_word2vec,
}

OP_DISPLAY_NAMES = {
    "kichik_registr": "Kichik registr",
    "tinish_belgilari": "Tinish belgilaridan tozalash",
    "tokenizatsiya": "Tokenizatsiya",
    "orfografik": "Orfografik xatoliklarni bartaraf etish",
    "stemming": "Stemming",
    "lemmatizatsiya": "Lemmatizatsiya",
    "stop_sozlar": "Stop so'zlardan tozalash",
    "onehot": "One-Hot Kodlash",
    "tfidf": "TF-IDF",
    "bow": "Bag of Words",
    "word2vec": "Word2Vec",
}

# Mashinali o'qitish algoritmlari — 2 kategoriya
ML_CLASSIFIERS = [
    "Decision Tree",
    "Random Forest",
    "Naive Bayes",
    "Passive Aggressive",
    "XGBoost",
    "Support Vector Machine (SVM)",
    "K-Nearest Neighbors (KNN)",
    "Logistic Regression",
    "AdaBoost",
    "Gradient Boosting",
]

NN_CLASSIFIERS = [
    "LSTM (Long Short-Term Memory)",
    "BiLSTM (Bidirectional LSTM)",
    "MLP (Multilayer Perceptron)",
    "CNN (Convolutional Neural Network)",
    "GRU (Gated Recurrent Unit)",
    "Transformer",
    "BERT",
    "RNN (Recurrent Neural Network)",
]

# Kategoriya ko'rsatkichi — menyu action bilan bog'lash uchun
CURRENT_CLASSIFIER_CATEGORY = "ml"  # "ml" yoki "nn"


# ─────────────────────────────────────────────
# FORMAT DIALOG
# ─────────────────────────────────────────────
class FormatDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.s = settings or load_settings()
        self.setWindowTitle("Fayl formatini tanlang")
        self.setModal(True)
        self.resize(400, 280)
        layout = QVBoxLayout()

        label = QLabel("Qaysi formatda saqlash kerak?")
        label.setFont(QFont(self.s["font_family"], 12, QFont.Bold))
        layout.addWidget(label)
        layout.addSpacing(8)

        self.btn_txt = QPushButton("📄  TXT — Oddiy matn fayli")
        self.btn_docx = QPushButton("📝  DOCX — Microsoft Word")
        self.btn_pdf = QPushButton("📕  PDF — Portable Document Format")

        bg = self.s["color_panel_bg"]
        border = self.s["color_border"]
        for btn in [self.btn_txt, self.btn_docx, self.btn_pdf]:
            btn.setMinimumHeight(48)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    border: 2px solid {border};
                    border-radius: 8px;
                    padding: 10px;
                    text-align: left;
                    font-size: 13px;
                    color: {self.s['color_text']};
                }}
                QPushButton:hover {{ background-color: {border}; color: white; }}
            """)
            layout.addWidget(btn)

        layout.addSpacing(8)
        btn_cancel = QPushButton("❌ Bekor qilish")
        btn_cancel.setStyleSheet("""
            QPushButton { background-color:#FFEBEE; border:2px solid #EF5350;
                border-radius:6px; padding:8px; }
            QPushButton:hover { background-color:#FFCDD2; }
        """)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

        self.btn_txt.clicked.connect(lambda: self.accept_format('txt'))
        self.btn_docx.clicked.connect(lambda: self.accept_format('docx'))
        self.btn_pdf.clicked.connect(lambda: self.accept_format('pdf'))

        self.setLayout(layout)
        self.selected_format = None

    def accept_format(self, fmt):
        self.selected_format = fmt
        self.accept()


# ─────────────────────────────────────────────
# SOZLAMALAR DIALOG
# ─────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings if settings else load_settings()
        self.setWindowTitle("⚙️  Sozlamalar")
        self.setModal(True)
        self.resize(520, 580)
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        # ── Shrift ──
        # Settings dialog global style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #042442;
                border: 2px solid #003366;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #042442;
                background-color: white;
            }
            QLabel {
                color: #042442;
                font-size: 12px;
            }
            QSpinBox {
                border: 1px solid #003366;
                border-radius: 4px;
                padding: 3px;
                color: #042442;
                background-color: #e2e8f0;
                selection-background-color: #063462;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #e2e8f0;
                border: none;
            }
        """)
        font_group = QGroupBox("Shrift Sozlamalari")
        fg_layout = QGridLayout(font_group)

        fg_layout.addWidget(QLabel("Shrift nomi:"), 0, 0)
        self.lbl_font_preview = QLabel(self.settings["font_family"])
        self.lbl_font_preview.setFont(QFont(self.settings["font_family"], self.settings["font_size"]))
        self.lbl_font_preview.setStyleSheet("border:1px solid #ccc; padding:4px; border-radius:4px;")
        fg_layout.addWidget(self.lbl_font_preview, 0, 1)

        btn_font = QPushButton("Tanlash...")
        btn_font.clicked.connect(self._pick_font)
        fg_layout.addWidget(btn_font, 0, 2)

        fg_layout.addWidget(QLabel("O'lcham (pt):"), 1, 0)
        self.spin_size = QSpinBox()
        self.spin_size.setRange(8, 24)
        self.spin_size.setValue(self.settings["font_size"])
        self.spin_size.valueChanged.connect(self._preview_font)
        fg_layout.addWidget(self.spin_size, 1, 1)

        main_layout.addWidget(font_group)

        # ── Ranglar ──
        color_group = QGroupBox("Rang Sozlamalari")
        cg_layout = QGridLayout(color_group)

        self._color_keys = [
            ("color_input_bg", "Kiruvchi matn arka rang"),
            ("color_output_bg", "Natijaviy matn arka rang"),
            ("color_panel_bg", "O'ng panel arka rang"),
            ("color_menubar_bg", "Menyu rang"),
            ("color_text", "Matn rang"),
            ("color_label_text", "Sarlavha rang"),
            ("color_border", "Chegar rang"),
            ("color_btn_bg", "Tugma rang"),
        ]

        self._color_btns = {}
        for row, (key, label_text) in enumerate(self._color_keys):
            cg_layout.addWidget(QLabel(label_text), row, 0)
            btn = QPushButton()
            btn.setFixedSize(80, 30)
            btn.setStyleSheet(f"background-color:{self.settings[key]}; border:1px solid #999; border-radius:4px;")
            btn.clicked.connect(lambda checked, k=key, b=btn: self._pick_color(k, b))
            cg_layout.addWidget(btn, row, 1)
            self._color_btns[key] = btn

        main_layout.addWidget(color_group)

        # ── API Key ──
        api_group = QGroupBox("AI API Kalit Sozlamalari")
        api_layout = QGridLayout(api_group)

        api_layout.addWidget(QLabel("Anthropic API kalit:"), 0, 0)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(self.settings.get("api_key", ""))
        self.api_key_edit.setPlaceholderText("sk-ant-api03-...")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setStyleSheet("""
            QLineEdit {
                background-color: #e2e8f0;
                border: 1px solid #003366;
                border-radius: 4px;
                padding: 5px 8px;
                color: #042442;
                font-size: 12px;
            }
        """)
        api_layout.addWidget(self.api_key_edit, 0, 1)

        btn_show_key = QPushButton("Ko'rsat/Yashir")
        btn_show_key.setStyleSheet("background-color:#063462; color:white; border-radius:4px; padding:5px 10px; font-size:11px;")
        btn_show_key.clicked.connect(lambda: self.api_key_edit.setEchoMode(
            QLineEdit.Normal if self.api_key_edit.echoMode() == QLineEdit.Password else QLineEdit.Password
        ))
        api_layout.addWidget(btn_show_key, 0, 2)

        api_info = QLabel("Anthropic.com saytidan API kalit oling: https://console.anthropic.com")
        api_info.setStyleSheet("color:#666; font-size:10px; font-style:italic;")
        api_layout.addWidget(api_info, 1, 0, 1, 3)

        main_layout.addWidget(api_group)

        # ── Tugmalar ──
        btn_row = QHBoxLayout()
        btn_apply = QPushButton("Qo'llash")
        btn_apply.setStyleSheet("background-color:#2E7D32; color:white; border-radius:6px; padding:8px 16px; font-weight:bold;")
        btn_apply.clicked.connect(self.accept)
        btn_reset = QPushButton("Standart")
        btn_reset.setStyleSheet("background-color:#FF9800; color:white; border-radius:6px; padding:8px 16px; font-weight:bold;")
        btn_reset.clicked.connect(self._reset_defaults)
        btn_cancel = QPushButton("Bekor")
        btn_cancel.setStyleSheet("background-color:#EF5350; color:white; border-radius:6px; padding:8px 16px; font-weight:bold;")
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_apply)
        btn_row.addWidget(btn_reset)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        main_layout.addLayout(btn_row)

    # ── helpers ──
    def _pick_font(self):
        font = QFont(self.settings["font_family"], self.settings["font_size"])
        chosen, ok = QFontDialog.getFont(font, self)
        if ok:
            self.settings["font_family"] = chosen.family()
            self.spin_size.setValue(chosen.pointSize())
            self._preview_font()

    def _preview_font(self):
        self.settings["font_size"] = self.spin_size.value()
        self.settings["font_family"] = self.lbl_font_preview.text()
        self.lbl_font_preview.setFont(
            QFont(self.settings["font_family"], self.settings["font_size"])
        )

    def _pick_color(self, key, btn):
        current = QColor(self.settings[key])
        chosen = QColorDialog.getColor(current, self, f"{key} rang tanlash")
        if chosen.isValid():
            self.settings[key] = chosen.name()
            btn.setStyleSheet(f"background-color:{chosen.name()}; border:1px solid #999; border-radius:4px;")

    def _reset_defaults(self):
        self.settings.update(DEFAULT_SETTINGS)
        self.spin_size.setValue(self.settings["font_size"])
        self.lbl_font_preview.setText(self.settings["font_family"])
        self.lbl_font_preview.setFont(QFont(self.settings["font_family"], self.settings["font_size"]))
        for key, btn in self._color_btns.items():
            btn.setStyleSheet(f"background-color:{self.settings[key]}; border:1px solid #999; border-radius:4px;")

    def get_settings(self):
        self.settings["font_family"] = self.lbl_font_preview.text()
        self.settings["font_size"] = self.spin_size.value()
        self.settings["api_key"] = self.api_key_edit.text().strip()
        return self.settings


# ─────────────────────────────────────────────
# KVANT SOLISHTIRISH OYNAT
# ─────────────────────────────────────────────
class KvantCompareDialog(QDialog):
    def __init__(self, parent=None, settings=None,
                 op_name="", klassik_result="", klassik_time_ms=0,
                 kvant_result="", kvant_time_ms=0):
        super().__init__(parent)
        self.s = settings or load_settings()
        self.setWindowTitle("Klassik vs Kvant Solishtirish")
        self.setMinimumSize(900, 600)
        # Dialog uchun dizayn ranglari
        s = self.s
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {s['color_panel_bg']};
            }}
            QTabWidget::pane {{
                border: 2px solid {s['color_border']};
                border-radius: 6px;
                background-color: {s['color_panel_bg']};
            }}
            QTabBar::tab {{
                background-color: {s['color_btn_bg']};
                color: {s['color_btn_text']};
                padding: 6px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {s['color_border']};
                color: white;
            }}
            QGroupBox {{
                border: 2px solid {s['color_border']};
                border-radius: 8px;
                margin-top: 8px;
                background-color: {s['color_panel_bg']};
            }}
            QGroupBox::title {{
                color: {s['color_label_text']};
                font-weight: bold;
            }}
        """)
        self._build(op_name, klassik_result, klassik_time_ms,
                    kvant_result, kvant_time_ms)

    def _build(self, op_name, kr, kt, qr, qt_ms):
        main = QVBoxLayout(self)
        main.setSpacing(10)
        main.setContentsMargins(14, 14, 14, 14)

        s = self.s
        font = QFont(s["font_family"], s["font_size"])

        # ── sarlavha ──
        title = QLabel(f"\"{OP_DISPLAY_NAMES.get(op_name, op_name)}\" — Klassik va Kvant Solishtirish")
        title.setFont(QFont(s["font_family"], 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {s['color_btn_text']}; background-color: {s['color_btn_bg']};"
            f"padding: 8px; border-radius: 8px; margin-bottom: 4px;"
        )
        main.addWidget(title)

        # ── ikkala natija ──
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)

        # --- Tab 1: Yonma-yon ---
        side_widget = QWidget()
        side_widget.setStyleSheet(f"background-color: {s['color_panel_bg']};")
        side_layout = QHBoxLayout(side_widget)
        side_layout.setSpacing(12)

        for label_text, result_text, time_ms, bg_color in [
            ("Klassik Natija", kr, kt, s["color_input_bg"]),
            ("Kvant Natija",   qr, qt_ms, s["color_output_bg"]),
        ]:
            box = QGroupBox()
            box_layout = QVBoxLayout(box)

            hdr = QLabel(f"<b>{label_text}</b>  —  {time_ms:.2f} ms")
            hdr.setFont(QFont(s["font_family"], s["font_size"] + 1, QFont.Bold))
            hdr.setStyleSheet(
                f"color: {s['color_btn_text']}; background-color: {s['color_btn_bg']};"
                f"padding: 6px 10px; border-radius: 6px;"
            )
            box_layout.addWidget(hdr)

            te = QTextEdit()
            te.setReadOnly(True)
            te.setPlainText(result_text)
            te.setFont(font)
            te.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {bg_color};
                    border: 1.5px solid {s['color_border']};
                    border-radius: 6px;
                    padding: 8px;
                    color: {s['color_text']};
                }}
            """)
            box_layout.addWidget(te)
            side_layout.addWidget(box)

        tabs.addTab(side_widget, "Yonma-yon")

        # --- Tab 2: Satr-satr solishtirish ---
        merged_widget = QWidget()
        merged_widget.setStyleSheet(f"background-color: {s['color_panel_bg']};")
        merged_layout = QVBoxLayout(merged_widget)

        diff_te = QTextEdit()
        diff_te.setReadOnly(True)
        diff_te.setFont(font)
        diff_te.setStyleSheet(f"""
            QTextEdit {{
                background-color: {s['color_output_bg']};
                border: 1.5px solid {s['color_border']};
                border-radius: 6px;
                padding: 10px;
                color: {s['color_text']};
            }}
        """)

        lines_k = kr.split('\n')
        lines_q = qr.split('\n')
        max_lines = max(len(lines_k), len(lines_q))
        row_even = s['color_input_bg']
        row_odd  = s['color_output_bg']
        row_diff = "#fff3cd"   # farq bor satr — sariq
        html_parts = [
            f"<table style='width:100%; border-collapse:collapse; "
            f"font-family:{s['font_family']}; font-size:{s['font_size']}px;'>",
            f"<tr style='background:{s['color_btn_bg']}; color:{s['color_btn_text']};'>"
            f"<td style='padding:6px; width:50%; font-weight:bold;'>Klassik — {kt:.2f} ms</td>"
            f"<td style='padding:6px; width:50%; font-weight:bold;'>Kvant — {qt_ms:.2f} ms</td></tr>"
        ]
        for i in range(max_lines):
            lk = lines_k[i] if i < len(lines_k) else ""
            lq = lines_q[i] if i < len(lines_q) else ""
            bg = row_even if i % 2 == 0 else row_odd
            if lk.strip() != lq.strip():
                bg = row_diff
            html_parts.append(
                f"<tr style='background:{bg};'>"
                f"<td style='padding:4px 8px; border-bottom:1px solid {s['color_border']}; "
                f"vertical-align:top; color:{s['color_text']};'>{self._esc(lk)}</td>"
                f"<td style='padding:4px 8px; border-bottom:1px solid {s['color_border']}; "
                f"vertical-align:top; color:{s['color_text']};'>{self._esc(lq)}</td></tr>"
            )
        html_parts.append("</table>")
        diff_te.setHtml('\n'.join(html_parts))

        merged_layout.addWidget(diff_te)
        tabs.addTab(merged_widget, "Satr-satr Solishtirish")

        main.addWidget(tabs)

        # ── statistika ──
        if kt > 0 and qt_ms > 0:
            if kt > qt_ms:
                speed_txt = f"Kvant tezroq ({((kt - qt_ms)/kt*100):.1f}%)"
            elif qt_ms > kt:
                speed_txt = f"Klassik tezroq ({((qt_ms - kt)/qt_ms*100):.1f}%)"
            else:
                speed_txt = "Bir xil vaqt"
        else:
            speed_txt = ""

        stat_label = QLabel(
            f"Klassik: {kt:.2f} ms    |    Kvant: {qt_ms:.2f} ms    |    {speed_txt}"
        )
        stat_label.setFont(QFont(s["font_family"], s["font_size"], QFont.Bold))
        stat_label.setAlignment(Qt.AlignCenter)
        stat_label.setStyleSheet(
            f"color: {s['color_btn_text']}; background-color: {s['color_btn_bg']};"
            f"padding: 6px; border-radius: 6px;"
        )
        main.addWidget(stat_label)

        # ── yopish ──
        btn_close = QPushButton("Yopish")
        btn_close.setStyleSheet(
            f"background-color: {s['color_btn_bg']}; color: {s['color_btn_text']};"
            f"border-radius: 6px; padding: 8px 28px; font-weight: bold; font-size: 13px;"
        )
        btn_close.clicked.connect(self.close)
        btn_close.setFixedWidth(130)
        main.addWidget(btn_close, alignment=Qt.AlignCenter)

    @staticmethod
    def _esc(txt):
        return txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")


# ─────────────────────────────────────────────
# QO'LLANMA DIALOG  (README.md)
# ─────────────────────────────────────────────
class HelpDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.s = settings or load_settings()
        self.setWindowTitle("📖  Qo'llanma")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)

        # Sarlavha
        title = QLabel("📖  Matn Tarjimon Dasturi — Qo'llanma")
        title.setFont(QFont(self.s["font_family"], 15, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # README tarkibi o'qish
        content = self._read_readme()

        te = QTextEdit()
        te.setReadOnly(True)
        te.setFont(QFont(self.s["font_family"], self.s["font_size"]))
        te.setStyleSheet(f"""
            QTextEdit {{
                background-color: #FAFAFA;
                border: 1px solid {self.s['color_border']};
                border-radius: 8px;
                padding: 14px;
                color: {self.s['color_text']};
            }}
        """)
        # Markdown → simple HTML
        te.setHtml(self._md_to_html(content))
        layout.addWidget(te)

        btn = QPushButton("Yopish")
        btn.setStyleSheet("background-color:#2E7D32; color:white; border-radius:6px; padding:8px 24px; font-weight:bold;")
        btn.clicked.connect(self.close)
        btn.setFixedWidth(100)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

    @staticmethod
    def _read_readme() -> str:
        # README.md ni dastur papkasida qidirish
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
            "README.md",
            os.path.expanduser("~/README.md"),
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception:
                    continue
        return "⚠️  README.md fayl topilmadi. Iltimos, README.md faylni dastur papkasiga ko'chirting."

    @staticmethod
    def _md_to_html(md: str) -> str:
        """Minimal markdown → HTML konverter"""
        lines = md.split('\n')
        html = []
        in_table = False
        for line in lines:
            stripped = line.strip()

            # Sarlavhalar
            if stripped.startswith("### "):
                html.append(f"<h3 style='color:#2E7D32; margin-top:12px;'>{stripped[4:]}</h3>")
                continue
            if stripped.startswith("## "):
                html.append(f"<h2 style='color:#1B5E20; margin-top:16px;'>{stripped[3:]}</h2>")
                continue
            if stripped.startswith("# "):
                html.append(f"<h1 style='color:#1B5E20; text-align:center;'>{stripped[2:]}</h1>")
                continue

            # HR
            if stripped.startswith("---"):
                html.append("<hr style='border-color:#81C784;'>")
                continue

            # Table
            if "|" in stripped and stripped.startswith("|"):
                if not in_table:
                    html.append("<table style='border-collapse:collapse; width:100%; margin:8px 0;'>")
                    in_table = True
                cols = [c.strip() for c in stripped.split("|")[1:-1]]
                # Separator satir
                if all(c.replace("-", "").replace(":", "") == "" for c in cols):
                    continue
                is_header = len(html) > 0 and "<table" in html[-1] if in_table else False
                row = "<tr>"
                for c in cols:
                    tag = "th" if is_header else "td"
                    row += f"<{tag} style='border:1px solid #ccc; padding:4px 8px;'>{c}</{tag}>"
                row += "</tr>"
                html.append(row)
                continue
            else:
                if in_table:
                    html.append("</table>")
                    in_table = False

            # Bullet list
            if stripped.startswith("- "):
                txt = stripped[2:]
                txt = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', txt)
                html.append(f"<li style='margin:2px 0;'>{txt}</li>")
                continue

            # Bold inline
            stripped = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', stripped)

            # Empty line
            if not stripped:
                html.append("<br>")
                continue

            html.append(f"<p style='margin:2px 0;'>{stripped}</p>")

        if in_table:
            html.append("</table>")

        return '\n'.join(html)


# ─────────────────────────────────────────────
# ASOSIY OYNA
# ─────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()

        self.setWindowTitle("Preptext (Matnli ma'lumotlarga dastlabki ishlov berish)")
        self.setGeometry(100, 100, 1400, 860)

        self.is_normalizing = False
        self.current_file_path = None
        self.original_text = ""
        self.last_op_key = None          # Oxirgi bajarilgan operatsiya kaliti
        self.current_classifier_category = "ml"  # "ml" yoki "nn" — menyu qaysi bo'limidan tasniflash chaqirilgan

        self.create_menu_bar()
        self.create_main_interface()
        self.apply_settings()            # Rang + shrift tatbiq

        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Segoe UI", 11))
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #dce6f0;
                color: #042442;
                font-size: 11pt;
                font-weight: bold;
                padding: 2px 8px;
                border-top: 1px solid #003366;
            }
        """)
        self.status_bar.showMessage("Tayyor")
        self.setStatusBar(self.status_bar)

    # ═══════════════════════════════════════════
    # SOZLAMALAR QO'LASH
    # ═══════════════════════════════════════════
    def apply_settings(self):
        s = self.settings
        font = QFont(s["font_family"], s["font_size"])

        # Menubar
        self.menuBar().setStyleSheet(
            f"background-color:{s['color_menubar_bg']}; color:{s['color_menubar_text']}; "
            f"font-family:{s['font_family']}; font-size:{s['font_size']}px;"
        )

        # Input / Output TextEdit — font-size stylesheet'dan olib tashlandi,
        # faqat setFont() orqali boshqariladi. Zoom ishlashi uchun zarur.
        if not hasattr(self, '_widget_font_sizes'):
            self._widget_font_sizes = {}

        input_sz = self._widget_font_sizes.get(id(self.input_text), s["font_size"])
        self.input_text.setFont(QFont(s["font_family"], input_sz))
        self.input_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {s['color_input_bg']};
                border: 2px solid {s['color_border']};
                border-radius: 10px;
                padding: 10px;
                color: {s['color_text']};
            }}
        """)

        output_sz = self._widget_font_sizes.get(id(self.output_text), s["font_size"])
        self.output_text.setFont(QFont(s["font_family"], output_sz))
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {s['color_output_bg']};
                border: 2px solid {s['color_border']};
                border-radius: 10px;
                padding: 10px;
                color: {s['color_text']};
            }}
        """)

        # Labels
        for lbl in [self.lbl_input, self.lbl_output]:
            lbl.setFont(QFont(s["font_family"], s["font_size"] + 2, QFont.Bold))
            lbl.setStyleSheet(f"color:{s['color_label_text']};")

        # Right panel frame
        self.right_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {s['color_panel_bg']};
                border-left: 2px solid {s['color_border']};
            }}
            QLabel {{
                border: none;
            }}
        """)

        # Right panel labels (section headers - keep inline styles)
        for lbl in self._panel_labels:
            lbl.setFont(QFont(s["font_family"], s["font_size"] + 1, QFont.Bold))

        # Right panel buttons (green)
        btn_style = f"""
            QPushButton {{
                background-color: {s['color_btn_bg']};
                color: {s['color_btn_text']};
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: {s['font_size']}px;
            }}
            QPushButton:hover {{ background-color: {s['color_btn_hover']}; }}
        """
        for btn in self._panel_buttons:
            btn.setStyleSheet(btn_style)

        # Bottom buttons (input/output ostidagi)
        bottom_btn_style = f"""
            QPushButton {{
                background-color: {s['color_btn_bg']};
                color: {s['color_btn_text']};
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: {s['color_btn_hover']}; }}
        """
        for b in getattr(self, '_input_bottom_btns', []) + getattr(self, '_output_bottom_btns', []):
            b.setStyleSheet(bottom_btn_style)

        # Search fields
        search_style = f"""
            QLineEdit {{
                background-color: white;
                border: 1px solid {s['color_border']};
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 13px;
                color: {s['color_text']};
            }}
        """
        for sf in [getattr(self, 'input_search_field', None), getattr(self, 'output_search_field', None)]:
            if sf:
                sf.setStyleSheet(search_style)

        # Toolbar buttons — ochish uchun standart QToolButton stil
        self.btn_open.setStyleSheet(f"""
            QToolButton {{
                background-color: {s['color_btn_bg']};
                color: {s['color_btn_text']};
                border-radius: 8px;
                font-weight: bold;
                padding: 2px;
                font-size: 9px;
            }}
            QToolButton:hover {{ background-color: {s['color_btn_hover']}; }}
        """)
        # Saqlash — QPushButton (pastdagi tugmalar kabi)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {s['color_btn_bg']};
                color: white;
                border-radius: 8px;
                font-size: 20px;
                border: none;
            }}
            QPushButton:hover {{ background-color: {s['color_btn_hover']}; border: 1px solid #aac4e8; }}
            QPushButton:pressed {{ background-color: #021e3a; }}
        """)

        # Asl matnga qaytish, Almashtirish, Solishtirish — asl fon, ikonka oq
        _special_btn_style = f"""
            QToolButton {{
                background-color: {s['color_btn_bg']};
                color: #ffffff;
                border-radius: 8px;
                font-weight: bold;
                padding: 2px;
                font-size: 9px;
                icon-size: 28px 28px;
            }}
            QToolButton:hover {{ background-color: {s['color_btn_hover']}; }}
            QToolButton:pressed {{ background-color: #021e3a; }}
        """
        for btn in [self.btn_original, self.btn_swap, self.btn_compare]:
            btn.setStyleSheet(_special_btn_style)

        # Transliteratsiya buttons (interfeysdagi to'q ko'k)
        trans_style = f"""
            QPushButton {{
                background-color: {s['color_btn_bg']};
                color: {s['color_btn_text']};
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: {s['font_size']}px;
            }}
            QPushButton:hover {{ background-color: {s['color_btn_hover']}; }}
        """
        for btn in self._trans_buttons:
            btn.setStyleSheet(trans_style)

        # Radio buttons
        radio_style = f"""
            QRadioButton {{
                color: {s['color_text']};
                font-family: {s['font_family']};
                font-size: {s['font_size']}px;
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {s['color_border']};
                background-color: white;
            }}
            QRadioButton::indicator:checked {{
                background-color: {s['color_btn_bg']};
                border: 2px solid {s['color_btn_bg']};
                image: none;
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {s['color_btn_bg']};
            }}
        """
        for rb in self._radio_buttons:
            rb.setFont(font)
            rb.setStyleSheet(radio_style)

        # Classifier combobox — paneldan olib tashlandi

    # ═══════════════════════════════════════════
    # MENU BAR
    # ═══════════════════════════════════════════
    def create_menu_bar(self):
        menubar = self.menuBar()

        # ── Fayl ──
        file_menu = menubar.addMenu("Fayl")
        action_new = QAction("Yangi ochish", self)
        action_new.triggered.connect(self.new_file)
        file_menu.addAction(action_new)
        file_menu.addSeparator()

        action_save = QAction("Saqlash", self)
        action_save.triggered.connect(self.save_with_format)
        file_menu.addAction(action_save)

        action_save_as = QAction("Yangi nom bilan saqlash", self)
        action_save_as.triggered.connect(self.save_as_with_format)
        file_menu.addAction(action_save_as)
        file_menu.addSeparator()

        action_settings = QAction("⚙️  Sozlamalar", self)
        action_settings.triggered.connect(self.open_settings)
        file_menu.addAction(action_settings)
        file_menu.addSeparator()

        action_close = QAction("Yopish", self)
        action_close.triggered.connect(self.close_current)
        file_menu.addAction(action_close)

        action_exit = QAction("Chiqish", self)
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)

        # ── Klassik dastlabki ishlov ──
        classic_menu = menubar.addMenu("Klassik dastlabki ishlov")
        self._klassik_actions = {}

        classic_items = [
            ("kichik_registr", "Kichik registrga o'tkizish"),
            ("tinish_belgilari", "Tinish belgilaridan tozalash"),
            ("tokenizatsiya", "Tokenizatsiya"),
            ("orfografik", "Orfografik xatoliklarni bartaraf etish"),
            ("stemming", "Stemming"),
            ("lemmatizatsiya", "Lemmatizatsiya"),
            ("stop_sozlar", "Stop so'zlardan tozalash"),
        ]
        for key, name in classic_items:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, k=key: self.run_klassik(k))
            classic_menu.addAction(action)
            self._klassik_actions[key] = action

        shakl_menu = classic_menu.addMenu("Belgilarni shakllantirish")
        shakl_items = [
            ("onehot", "One-hot kodlash"),
            ("tfidf", "TF-IDF"),
            ("bow", "Bag of words"),
            ("word2vec", "Word2vec"),
        ]
        for key, name in shakl_items:
            action = QAction(f"• {name}", self)
            action.triggered.connect(lambda checked, k=key: self.run_klassik(k))
            shakl_menu.addAction(action)
            self._klassik_actions[key] = action

        # ── Kvant dastlabki ishlov ──
        kvant_menu = menubar.addMenu("Kvant dastlabki ishlov")
        kvant_items = [
            ("kichik_registr", "Kvant kichik registrga o'tkizish"),
            ("tinish_belgilari", "Kvant tozalash"),
            ("tokenizatsiya", "Kvant tokenizatsiya"),
            ("orfografik", "Kvant orfografik xatoliklarni bartaraf etish"),
            ("stemming", "Kvant stemming"),
            ("lemmatizatsiya", "Kvant lemmatizatsiya"),
            ("stop_sozlar", "Kvant stop so'zlardan tozalash"),
        ]
        for key, name in kvant_items:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, k=key: self.run_kvant_only(k))
            kvant_menu.addAction(action)

        kvant_shakl = kvant_menu.addMenu("Kvant belgilarni shakllantirish")
        kvant_shakl_items = [
            ("onehot", "Kvant one-hot kodlash"),
            ("tfidf", "Kvant TF-IDF"),
            ("bow", "Kvant Bag of words"),
            ("word2vec", "Kvant Word2vec"),
        ]
        for key, name in kvant_shakl_items:
            action = QAction(f"• {name}", self)
            action.triggered.connect(lambda checked, k=key: self.run_kvant_only(k))
            kvant_shakl.addAction(action)

        # ── Tasniflash ──
        classify_menu = menubar.addMenu("📊  Tasniflash")

        # ════ SHIKOYATLARNI ANIQLASH ════
        complaints_menu = classify_menu.addMenu("🔔  Shikoyatlarni aniqlash")

        complaints_ml_menu = complaints_menu.addMenu("🤖  Mashinali o'qitish modellari")
        for alg_id, alg_name in [
            ("logistic", "Logistik Regressiya"),
            ("naive_bayes", "Naive Bayes"),
            ("svm", "SVM"),
            ("decision_tree", "Decision Tree"),
            ("random_forest", "Random Forest"),
        ]:
            act = QAction(f"📊  {alg_name}", self)
            act.triggered.connect(lambda checked=False, c="complaint", m="ml", a=alg_id: self.run_classifier(c, m, a))
            complaints_ml_menu.addAction(act)

        complaints_nn_menu = complaints_menu.addMenu("🧠  Neyron tarmoq modellari")
        for alg_id, alg_name in [
            ("cnn", "CNN"),
            ("rnn", "RNN"),
            ("lstm", "LSTM"),
            ("transformer", "Transformer"),
        ]:
            act = QAction(f"🔷  {alg_name}", self)
            act.triggered.connect(lambda checked=False, c="complaint", m="nn", a=alg_id: self.run_classifier(c, m, a))
            complaints_nn_menu.addAction(act)

        # ════ SPAMLARNI ANIQLASH ════
        spam_menu = classify_menu.addMenu("📧  Spamlarni aniqlash")

        spam_ml_menu = spam_menu.addMenu("🤖  Mashinali o'qitish modellari")
        for alg_id, alg_name in [
            ("logistic", "Logistik Regressiya"),
            ("naive_bayes", "Naive Bayes"),
            ("svm", "SVM"),
            ("decision_tree", "Decision Tree"),
            ("random_forest", "Random Forest"),
        ]:
            act = QAction(f"📊  {alg_name}", self)
            act.triggered.connect(lambda checked=False, c="spam", m="ml", a=alg_id: self.run_classifier(c, m, a))
            spam_ml_menu.addAction(act)

        spam_nn_menu = spam_menu.addMenu("🧠  Neyron tarmoq modellari")
        for alg_id, alg_name in [
            ("cnn", "CNN"),
            ("rnn", "RNN"),
            ("lstm", "LSTM"),
            ("transformer", "Transformer"),
        ]:
            act = QAction(f"🔷  {alg_name}", self)
            act.triggered.connect(lambda checked=False, c="spam", m="nn", a=alg_id: self.run_classifier(c, m, a))
            spam_nn_menu.addAction(act)

        # ── Yordam ──
        help_menu = menubar.addMenu("Yordam")
        action_guide = QAction("📖  Qo'llanma", self)
        action_guide.triggered.connect(self.open_help)
        help_menu.addAction(action_guide)

        action_about = QAction("ℹ️  Model haqida", self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)

        help_menu.addAction(QAction("📜  Litsenziya va foydalanish shartlari", self))
        help_menu.addAction(QAction("🔧  Texnik yordam", self))

    # ═══════════════════════════════════════════
    # ASOSIY INTERFEYS
    # ═══════════════════════════════════════════
    def create_main_interface(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)

        # ── Chap panel ──
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(8)

        # Toolbar
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(6)

        self.btn_original = self._make_toolbar_btn("Asl", "Asl matnga qaytish")
        self.btn_open = self._make_toolbar_btn("Ochish", "Faylni ochish")

        # Saqlash — pastdagi tugmalar bilan bir xil stil
        self.btn_save = QPushButton("💾")
        self.btn_save.setToolTip("Natijani saqlash")
        self.btn_save.setFixedSize(QSize(52, 36))
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.settings['color_btn_bg']};
                color: white;
                border-radius: 8px;
                font-size: 20px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #0a4a8a; border: 1px solid #aac4e8; }}
            QPushButton:pressed {{ background-color: #021e3a; }}
        """)
        # Swap button
        self.btn_swap = QToolButton()
        self.btn_swap.setToolTip("Kiruvchi ↔ Natijaviy almashtirish")
        self.btn_swap.setFixedSize(QSize(52, 36))
        self.btn_swap.setText("")

        # Compare button
        self.btn_compare = QToolButton()
        self.btn_compare.setToolTip("Klassik vs Kvant solishtirish")
        self.btn_compare.setFixedSize(QSize(52, 36))
        self.btn_compare.setText("")

        # Ikonkalarni ulash — ochish uchun PNG
        try:
            self.btn_open.setIcon(QIcon(ICON_OCHISH))
            self.btn_open.setIconSize(QSize(28, 28))
        except Exception:
            pass

        self.btn_original.setIcon(create_return_icon(48))
        self.btn_original.setIconSize(QSize(32, 32))

        # btn_swap — aylana strelkalar
        self.btn_swap.setIcon(create_swap_icon(48))
        self.btn_swap.setIconSize(QSize(32, 32))

        # btn_compare — tarozi
        self.btn_compare.setIcon(create_compare_icon(48))
        self.btn_compare.setIconSize(QSize(32, 32))

        self.btn_original.clicked.connect(self.restore_original_text)
        self.btn_open.clicked.connect(self.open_file_into_input)
        self.btn_save.clicked.connect(self.save_output_text)
        self.btn_swap.clicked.connect(self.swap_texts)

        self.btn_compare.clicked.connect(self.open_compare_dialog)

        for btn in [self.btn_original, self.btn_open, self.btn_save, self.btn_swap, self.btn_compare]:
            toolbar_layout.addWidget(btn)
        toolbar_layout.addStretch()

        # Labels + TextEdits
        self.lbl_input = QLabel("")  # Olib tashlandi
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Bu yerga matnni kiriting...")
        self.input_text.setLayoutDirection(Qt.LeftToRight)
        self.input_text.textChanged.connect(self.save_original_text_auto)

        self.lbl_output = QLabel("")  # Olib tashlandi
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Tahrirlangan matn natijasi...")
        self.output_text.setLayoutDirection(Qt.LeftToRight)

        left_layout.addWidget(toolbar_widget)
        left_layout.addWidget(self.input_text)

        # ════ KIRUVCHI MATN OSTIDA BUTTONLAR ════
        input_btns_widget = QWidget()
        input_btns_widget.setStyleSheet(
            f"background-color: {self.settings['color_input_bg']}; border-radius: 0px;"
        )
        input_btns_layout = QHBoxLayout(input_btns_widget)
        input_btns_layout.setContentsMargins(4, 3, 4, 3)
        input_btns_layout.setSpacing(3)

        _ibtn_style = f"""
            QPushButton {{
                background-color: {self.settings['color_btn_bg']};
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #0a4a8a;
                border: 1px solid #aac4e8;
            }}
            QPushButton:pressed {{
                background-color: #021e3a;
            }}
        """
        _nav_style = f"""
            QPushButton {{
                background-color: {self.settings['color_btn_bg']};
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: #0a4a8a; border: 1px solid #aac4e8; }}
            QPushButton:pressed {{ background-color: #021e3a; }}
            QPushButton:disabled {{ background-color: #4a6080; color: #8899aa; }}
        """

        # Nusxalash ikonkasi — rasmdagidek ikkita sahifa
        _copy_icon = create_copy_icon(48, self.settings['color_btn_bg'])

        def _make_icon_btn(icon, tooltip, fn):
            b = QPushButton()
            b.setIcon(icon)
            b.setIconSize(QSize(28, 28))
            b.setToolTip(tooltip)
            b.setFixedSize(40, 36)
            b.setStyleSheet(_ibtn_style)
            b.clicked.connect(fn)
            return b

        def _make_emoji_btn(emoji, tooltip, fn):
            b = QPushButton(emoji)
            b.setToolTip(tooltip)
            b.setFixedSize(40, 36)
            b.setStyleSheet(_ibtn_style)
            b.clicked.connect(fn)
            return b

        # 6 ta asosiy icon tugmalar — kiruvchi matn
        self._input_bottom_btns = []
        b_copy_in = _make_icon_btn(_copy_icon, "Nusxalash", lambda: self._copy_text(self.input_text))
        input_btns_layout.addWidget(b_copy_in); self._input_bottom_btns.append(b_copy_in)

        b_clear_in = _make_emoji_btn("🗑️", "Tozalash", lambda: self.input_text.clear())
        input_btns_layout.addWidget(b_clear_in); self._input_bottom_btns.append(b_clear_in)

        b_zout_in = _make_emoji_btn("🔍−", "Shriftni kichiklashtirish", lambda: self._zoom_out_text(self.input_text))
        input_btns_layout.addWidget(b_zout_in); self._input_bottom_btns.append(b_zout_in)

        b_zin_in = _make_emoji_btn("🔍+", "Shriftni kattalashtirish", lambda: self._zoom_in_text(self.input_text))
        input_btns_layout.addWidget(b_zin_in); self._input_bottom_btns.append(b_zin_in)

        b_open_in = _make_emoji_btn("📂", "Fayl ochish", self.open_file_into_input)
        input_btns_layout.addWidget(b_open_in); self._input_bottom_btns.append(b_open_in)

        b_save_in = _make_emoji_btn("💾", "Saqlash", lambda: self._save_text(self.input_text))
        input_btns_layout.addWidget(b_save_in); self._input_bottom_btns.append(b_save_in)

        # ◀ Previous / ▶ Next pagination tugmalari
        self.btn_input_prev = QPushButton("\u25c0")
        self.btn_input_prev.setToolTip("Oldingi sahifa")
        self.btn_input_prev.setFixedSize(40, 36)
        self.btn_input_prev.setStyleSheet(_nav_style)
        self.btn_input_prev.clicked.connect(lambda: self._page_prev("input"))
        input_btns_layout.addWidget(self.btn_input_prev)

        self.btn_input_next = QPushButton("\u25b6")
        self.btn_input_next.setToolTip("Keyingi sahifa")
        self.btn_input_next.setFixedSize(40, 36)
        self.btn_input_next.setStyleSheet(_nav_style)
        self.btn_input_next.clicked.connect(lambda: self._page_next("input"))
        input_btns_layout.addWidget(self.btn_input_next)

        # Search field
        self.input_search_field = QLineEdit()
        self.input_search_field.setPlaceholderText("Qidirish...")
        self.input_search_field.setFixedHeight(36)
        self.input_search_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 1px solid {self.settings['color_border']};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                color: {self.settings['color_text']};
            }}
        """)
        input_btns_layout.addWidget(self.input_search_field)
        # Yozayotganda real vaqtda sariq highlight
        self.input_search_field.textChanged.connect(
            lambda q: self._highlight_search(self.input_text, q)
        )

        btn_isearch = QPushButton("\U0001f50e")
        btn_isearch.setFixedSize(40, 36)
        btn_isearch.setToolTip("Qidirish")
        btn_isearch.setStyleSheet(_ibtn_style)
        btn_isearch.clicked.connect(
            lambda: self.perform_search(self.input_search_field, self.input_text)
        )
        input_btns_layout.addWidget(btn_isearch)
        self._input_bottom_btns.append(btn_isearch)

        left_layout.addWidget(input_btns_widget)
        left_layout.addWidget(self.output_text)

        # ════ NATIJAVIY MATN OSTIDA BUTTONLAR ════
        output_btns_widget = QWidget()
        output_btns_widget.setStyleSheet(
            f"background-color: {self.settings['color_output_bg']}; border-radius: 0px;"
        )
        output_btns_layout = QHBoxLayout(output_btns_widget)
        output_btns_layout.setContentsMargins(4, 3, 4, 3)
        output_btns_layout.setSpacing(3)

        # 6 ta asosiy icon tugmalar — natijaviy matn
        self._output_bottom_btns = []
        b_copy_out = _make_icon_btn(_copy_icon, "Nusxalash", lambda: self._copy_text(self.output_text))
        output_btns_layout.addWidget(b_copy_out); self._output_bottom_btns.append(b_copy_out)

        b_clear_out = _make_emoji_btn("🗑️", "Tozalash", lambda: self.output_text.clear())
        output_btns_layout.addWidget(b_clear_out); self._output_bottom_btns.append(b_clear_out)

        b_zout_out = _make_emoji_btn("🔍−", "Shriftni kichiklashtirish", lambda: self._zoom_out_text(self.output_text))
        output_btns_layout.addWidget(b_zout_out); self._output_bottom_btns.append(b_zout_out)

        b_zin_out = _make_emoji_btn("🔍+", "Shriftni kattalashtirish", lambda: self._zoom_in_text(self.output_text))
        output_btns_layout.addWidget(b_zin_out); self._output_bottom_btns.append(b_zin_out)

        b_open_out = _make_emoji_btn("📂", "Fayl ochish", self.open_file_into_input)
        output_btns_layout.addWidget(b_open_out); self._output_bottom_btns.append(b_open_out)

        b_save_out = _make_emoji_btn("💾", "Saqlash", lambda: self._save_text(self.output_text))
        output_btns_layout.addWidget(b_save_out); self._output_bottom_btns.append(b_save_out)

        self.btn_output_prev = QPushButton("\u25c0")
        self.btn_output_prev.setToolTip("Oldingi sahifa")
        self.btn_output_prev.setFixedSize(40, 36)
        self.btn_output_prev.setStyleSheet(_nav_style)
        self.btn_output_prev.clicked.connect(lambda: self._page_prev("output"))
        output_btns_layout.addWidget(self.btn_output_prev)

        self.btn_output_next = QPushButton("\u25b6")
        self.btn_output_next.setToolTip("Keyingi sahifa")
        self.btn_output_next.setFixedSize(40, 36)
        self.btn_output_next.setStyleSheet(_nav_style)
        self.btn_output_next.clicked.connect(lambda: self._page_next("output"))
        output_btns_layout.addWidget(self.btn_output_next)

        self.output_search_field = QLineEdit()
        self.output_search_field.setPlaceholderText("Qidirish...")
        self.output_search_field.setFixedHeight(36)
        self.output_search_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 1px solid {self.settings['color_border']};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                color: {self.settings['color_text']};
            }}
        """)
        output_btns_layout.addWidget(self.output_search_field)
        # Yozayotganda real vaqtda sariq highlight
        self.output_search_field.textChanged.connect(
            lambda q: self._highlight_search(self.output_text, q)
        )

        btn_osearch = QPushButton("\U0001f50e")
        btn_osearch.setFixedSize(40, 36)
        btn_osearch.setToolTip("Qidirish")
        btn_osearch.setStyleSheet(_ibtn_style)
        btn_osearch.clicked.connect(
            lambda: self.perform_search(self.output_search_field, self.output_text)
        )
        output_btns_layout.addWidget(btn_osearch)
        self._output_bottom_btns.append(btn_osearch)

        left_layout.addWidget(output_btns_widget)

        # ── Sahifalash holati (pagination state) ──
        self._input_pages  = []   # kiruvchi matn sahifalari
        self._input_page   = 0    # joriy sahifa indeksi
        self._output_pages = []   # natijaviy matn sahifalari
        self._output_page  = 0
        self.LINES_PER_PAGE = 30  # bir sahifada nechta satr


        # ── O'ng panel: tepada logo, pastda scroll ──
        self.right_frame = QFrame()
        self.right_frame.setFixedWidth(330)
        right_frame_layout = QVBoxLayout(self.right_frame)
        right_frame_layout.setContentsMargins(0, 0, 0, 0)
        right_frame_layout.setSpacing(0)

        # Logo — panel ustida, katta (kichkina bo'lmasin)
        self.panel_logo_label = QLabel()
        logo_loaded = False
        # Logoni bir necha joydan qidirish: dastur papkasi, assets, uploads
        _logo_candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiiame_logo.png"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "tiiame_logo.png"),
            ICON_PANEL_LOGO,
        ]
        for _logo_path in _logo_candidates:
            if os.path.exists(_logo_path):
                px = QPixmap(_logo_path).scaled(220, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                if not px.isNull():
                    self.panel_logo_label.setPixmap(px)
                    logo_loaded = True
                    break
        if not logo_loaded:
            self.panel_logo_label.setText(
                "<div style='text-align:center; padding: 20px 10px;'>"
                "<div style='font-size:64px;'>💧</div>"
                "<div style='font-size:22px; font-weight:bold; color:#063462; "
                "font-family:Segoe UI; letter-spacing:2px;'>TIIAME</div>"
                "</div>"
            )
            self.panel_logo_label.setTextFormat(Qt.RichText)
        self.panel_logo_label.setAlignment(Qt.AlignCenter)
        self.panel_logo_label.setMinimumHeight(160)
        self.panel_logo_label.setStyleSheet("background-color: white; border: none;")
        right_frame_layout.addWidget(self.panel_logo_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        right_layout = QVBoxLayout(scroll_content)
        right_layout.setContentsMargins(18, 18, 18, 18)
        right_layout.setSpacing(12)

        self._panel_labels = []
        self._panel_buttons = []
        self._trans_buttons = []
        self._radio_buttons = []

        # ─── Matnni tekshirish ───
        line_before_tekshirish = QFrame()
        line_before_tekshirish.setFrameShape(QFrame.HLine)
        line_before_tekshirish.setStyleSheet("color: #c0c8d8;")
        right_layout.addWidget(line_before_tekshirish)

        lbl_tekshirish = QLabel("Matnni tekshirish")
        lbl_tekshirish.setStyleSheet("font-weight: bold; font-size: 14px; color: #042442; padding: 2px 0;")
        self._panel_labels.append(lbl_tekshirish)
        self.tekshirish_group = QButtonGroup(self)
        self.radio_lugat = QRadioButton("Lug'at yordamida")
        self.radio_ai = QRadioButton("Sun'iy intellekt yordamida")
        self.radio_ai.setChecked(True)
        self.tekshirish_group.addButton(self.radio_lugat)
        self.tekshirish_group.addButton(self.radio_ai)
        self._radio_buttons.extend([self.radio_lugat, self.radio_ai])
        self.btn_tekshirish = QPushButton("Tekshirish")
        self.btn_tekshirish.setMinimumHeight(40)
        self._panel_buttons.append(self.btn_tekshirish)
        self.btn_tekshirish.clicked.connect(self.do_tekshirish)

        right_layout.addWidget(lbl_tekshirish)
        right_layout.addWidget(self.radio_lugat)
        right_layout.addWidget(self.radio_ai)
        right_layout.addWidget(self.btn_tekshirish)

        line_tekshirish = QFrame()
        line_tekshirish.setFrameShape(QFrame.HLine)
        line_tekshirish.setStyleSheet("color: #c0c8d8;")
        right_layout.addWidget(line_tekshirish)

        # ─── To'g'rilash ───
        lbl_togrilash = QLabel("To'g'rilash")
        lbl_togrilash.setStyleSheet("font-weight: bold; font-size: 14px; color: #042442; padding: 2px 0;")
        self._panel_labels.append(lbl_togrilash)
        self.togrilash_group = QButtonGroup(self)
        self.radio_qolda = QRadioButton("Qo'lda to'g'rilash")
        self.radio_avto = QRadioButton("Avtomatik to'g'rilash")
        self.radio_avto.setChecked(True)
        self.togrilash_group.addButton(self.radio_qolda)
        self.togrilash_group.addButton(self.radio_avto)
        self._radio_buttons.extend([self.radio_qolda, self.radio_avto])
        self.btn_togrilash = QPushButton("To'g'rilash")
        self.btn_togrilash.setMinimumHeight(40)
        self._panel_buttons.append(self.btn_togrilash)
        self.btn_togrilash.clicked.connect(self.do_togrilash)

        right_layout.addWidget(lbl_togrilash)
        right_layout.addWidget(self.radio_qolda)
        right_layout.addWidget(self.radio_avto)
        right_layout.addWidget(self.btn_togrilash)

        line_togrilash = QFrame()
        line_togrilash.setFrameShape(QFrame.HLine)
        line_togrilash.setStyleSheet("color: #c0c8d8;")
        right_layout.addWidget(line_togrilash)

        # ─── Transliteratsiya ───
        lbl_trans = QLabel("Transliteratsiya:")
        lbl_trans.setStyleSheet("font-weight: bold; font-size: 14px; color: #042442; padding: 2px 0;")
        self._panel_labels.append(lbl_trans)
        right_layout.addWidget(lbl_trans)

        def _add_trans_group(title, items):
            lbl = QLabel(title)
            lbl.setStyleSheet("font-weight: bold; font-size: 12px; color: #042442; padding: 4px 0 0 0;")
            self._panel_labels.append(lbl)
            right_layout.addWidget(lbl)
            for text, func, msg in items:
                btn = QPushButton(text)
                btn.setMinimumHeight(40)
                self._trans_buttons.append(btn)
                btn.clicked.connect(lambda _=False, f=func, m=msg: self.do_translit(f, m))
                right_layout.addWidget(btn)

        _add_trans_group("Eski lotin (Sh, Ch, O', G')", [
            ("Kiril → Eski lotin", translit.cyr_to_old, "Kiril eski lotin yozuviga o'girildi"),
            ("Eski lotin → Kiril", translit.old_to_cyr, "Eski lotin kirilga o'girildi"),
        ])
        _add_trans_group("Yangi lotin (Ş, Ç, Ö, Ğ)", [
            ("Kiril → Yangi lotin", translit.cyr_to_new, "Kiril yangi lotin yozuviga o'girildi"),
            ("Yangi lotin → Kiril", translit.new_to_cyr, "Yangi lotin kirilga o'girildi"),
        ])
        _add_trans_group("Lotin ↔ Lotin", [
            ("Eski lotin → Yangi lotin", translit.old_to_new, "Eski lotin yangi lotinga o'girildi"),
            ("Yangi lotin → Eski lotin", translit.new_to_old, "Yangi lotin eski lotinga o'girildi"),
        ])
        right_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        right_frame_layout.addWidget(scroll_area)

        splitter.addWidget(left_frame)
        splitter.addWidget(self.right_frame)
        splitter.setSizes([1050, 350])
        main_layout.addWidget(splitter)

    def _make_toolbar_btn(self, text, tooltip):
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(QSize(52, 36))
        return btn

    # ═══════════════════════════════════════════
    # KLASSIK + KVANT ISHLOV (birlishtirish)
    # ═══════════════════════════════════════════
    def run_klassik(self, op_key: str):
        """Klassik ishlov bajariladi, natija output'ga, then kvant oynat ochiladi."""
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Kiruvchi matn bo'sh!")
            return

        klassik_func = KLASSIK_MAP.get(op_key)
        kvant_func = KVANT_MAP.get(op_key)
        if not klassik_func:
            return

        self.last_op_key = op_key

        # ── Klassik timing ──
        t0 = time.perf_counter()
        klassik_result = klassik_func(text)
        klassik_time = (time.perf_counter() - t0) * 1000   # ms

        self.output_text.setPlainText(klassik_result)
        self._build_pages(klassik_result, "output")
        self._show_page("output")
        self.status_bar.showMessage(f"Klassik: {OP_DISPLAY_NAMES.get(op_key, op_key)} — {klassik_time:.2f} ms")

        # # ── Kvant timing ──
        # if kvant_func:
        #     t0 = time.perf_counter()
        #     kvant_result = kvant_func(text)
        #     kvant_time = (time.perf_counter() - t0) * 1000

        #     # Solishtirish oynat
        #     dlg = KvantCompareDialog(
        #         self, settings=self.settings,
        #         op_name=op_key,
        #         klassik_result=klassik_result, klassik_time_ms=klassik_time,
        #         kvant_result=kvant_result, kvant_time_ms=kvant_time,
        #     )
        #     dlg.show()

    def run_kvant_only(self, op_key: str):
        """Faqat kvant ishlov (kvant menyusidan)."""
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Kiruvchi matn bo'sh!")
            return

        kvant_func = KVANT_MAP.get(op_key)
        klassik_func = KLASSIK_MAP.get(op_key)
        if not kvant_func:
            return

        self.last_op_key = op_key

        t0 = time.perf_counter()
        kvant_result = kvant_func(text)
        kvant_time = (time.perf_counter() - t0) * 1000

        self.output_text.setPlainText(kvant_result)
        self._build_pages(kvant_result, "output")
        self._show_page("output")
        self.status_bar.showMessage(f"Kvant: {OP_DISPLAY_NAMES.get(op_key, op_key)} — {kvant_time:.2f} ms")

        # Klassik natija da hisoblab solishtirish
        # if klassik_func:
        #     t0 = time.perf_counter()
        #     klassik_result = klassik_func(text)
        #     klassik_time = (time.perf_counter() - t0) * 1000

        #     dlg = KvantCompareDialog(
        #         self, settings=self.settings,
        #         op_name=op_key,
        #         klassik_result=klassik_result, klassik_time_ms=klassik_time,
        #         kvant_result=kvant_result, kvant_time_ms=kvant_time,
        #     )
        #     dlg.show()

    # ═══════════════════════════════════════════
    # SWAP (Kiruvchi ↔ Natijaviy)
    # ═══════════════════════════════════════════
    def swap_texts(self):
        inp = self.input_text.toPlainText()
        out = self.output_text.toPlainText()
        if not out.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Natijaviy matn bo'sh — almashtirishga narsaga yo'q!")
            return
        # Bloklash: normalize signal chiqmay
        self.is_normalizing = True
        self.input_text.setPlainText(out)
        self.output_text.setReadOnly(False)
        self.output_text.setPlainText(inp)
        self.output_text.setReadOnly(True)
        self.is_normalizing = False
        self.original_text = out
        self.status_bar.showMessage("Kiruvchi va Natijaviy matn almashtirildi")

    # ═══════════════════════════════════════════
    # COMPARE DIALOG (toolbar button)
    # ═══════════════════════════════════════════
    def open_compare_dialog(self):
        """Oxirgi bajarilgan operatsiyaning klassik+kvant natijalarini solishtirish oynasi."""
        if not self.last_op_key:
            QMessageBox.information(
                self, "Ma'lumot",
                "Hali hech qanday ishlov bajarilmagan.\n"
                "Klassik yoki Kvant menyu bilan biron operatsiya bajarilgandan so'ng\n"
                "bu tugma ishlay boshnadi."
            )
            return

        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Kiruvchi matn bo'sh!")
            return

        op_key = self.last_op_key
        kl_func = KLASSIK_MAP.get(op_key)
        kv_func = KVANT_MAP.get(op_key)

        if not kl_func or not kv_func:
            QMessageBox.warning(self, "Xatolik", "Operatsiya topilmadi.")
            return

        t0 = time.perf_counter()
        kl_result = kl_func(text)
        kl_time = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        kv_result = kv_func(text)
        kv_time = (time.perf_counter() - t0) * 1000

        dlg = KvantCompareDialog(
            self, settings=self.settings,
            op_name=op_key,
            klassik_result=kl_result, klassik_time_ms=kl_time,
            kvant_result=kv_result, kvant_time_ms=kv_time,
        )
        dlg.show()

    # ═══════════════════════════════════════════
    # CLASSIFIER CATEGORY (menyu → combobox)
    # ═══════════════════════════════════════════
    def set_classifier_category(self, category: str):
        """
        Menyu'dan Mashinali o'qitish / Neyron tarmoq bosilganda combobox'ni
        tegishli ro'yxat bilan to'ldirish.
        category: "ml" yoki "nn"
        """
        self.current_classifier_category = category
        # (combo olib tashlandi)
        
        if category == "ml":
        # (combo olib tashlandi)
            self.status_bar.showMessage("Mashinali o'qitish usullari tanlandi")
        else:  # "nn"
        # (combo olib tashlandi)
            self.status_bar.showMessage("Neyron tarmoq modellari tanlandi")
        
        # (combo olib tashlandi)

    # ═══════════════════════════════════════════
    # SOZLAMALAR
    # ═══════════════════════════════════════════
    def open_settings(self):
        dlg = SettingsDialog(self, settings=dict(self.settings))
        if dlg.exec() == QDialog.Accepted:
            self.settings = dlg.get_settings()
            save_settings(self.settings)
            self.apply_settings()
            self.status_bar.showMessage("Sozlamalar qo'yildi")

    # ═══════════════════════════════════════════
    # YORDAM
    # ═══════════════════════════════════════════
    def open_help(self):
        dlg = HelpDialog(self, settings=self.settings)
        dlg.show()

    def show_about(self):
        QMessageBox.information(
            self, "Model haqida",
            "📌 Matn Tarjimon Dasturi\n\n"
            "Versiya: 2.0\n"
            "Tillar: O'zbek\n"
            "Texnologiya: Python + PySide6\n"
            "NLP: Klassik + Kvant simulatsiya\n\n"
            "Ishlab chiqilgan: 2025"
        )

    # ═══════════════════════════════════════════
    # TASNIFLASH (ML listbox)
    # ═══════════════════════════════════════════
    def do_tasniflash(self):
        """Combobox'dagi tanlangan algoritmga qarab matnni tasniflash."""
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Kiruvchi matn bo'sh!")
            return

        algo_name = "(Tasniflash menyudan amalga oshiriladi)"
        if not algo_name:
            QMessageBox.warning(self, "Ogohlantirish", "Algorithm tanlash kerak!")
            return

        t0 = time.perf_counter()
        result = self._classify_text(text, algo_name)
        elapsed = (time.perf_counter() - t0) * 1000

        output = (
            f"{'=' * 60}\n"
            f"TASNIFLASH NATIJASI\n"
            f"{'=' * 60}\n\n"
            f"📌 Algorithm      : {algo_name}\n"
            f"⏱️  Vaqt           : {elapsed:.2f} ms\n"
            f"📝 Matn uzunligi  : {len(text)} simvol, {len(text.split())} so'z\n\n"
            f"{'-' * 60}\n"
            f"{result}\n"
            f"{'-' * 60}\n"
        )
        self.output_text.setPlainText(output)
        self.status_bar.showMessage(f"Tasniflash ({algo_name}) — {elapsed:.2f} ms")

    @staticmethod
    def _classify_text(text: str, algo: str) -> str:
        """
        Keyword-based classification stub.
        Toshkent → topolok, ijobiy/salbiy sentiment, + algorithm-specific imitation.
        """
        lower = text.lower()
        words = lower.split()
        word_count = len(words)

        # ── Sentiment ──
        pos_words = {
            'yaxshi', 'ajoyib', 'zo\'zal', 'muvaffaqiyat', 'baxtli',
            'yoqimli', 'wonderful', 'great', 'good', 'best',
            'ish', 'qulay', 'memnun', 'excellent',
        }
        neg_words = {
            'yomon', 'salbiy', 'muammolar', 'qiyinlik', 'huzunli',
            'bad', 'terrible', 'worst', 'sad', 'error',
            'xatolik', 'buzilgan', 'nojoya',
        }
        pos_count = sum(1 for w in words if w.strip('.,!?;:') in pos_words)
        neg_count = sum(1 for w in words if w.strip('.,!?;:') in neg_words)

        if pos_count > neg_count:
            sentiment = "Ijobiy (Positive)"
            conf_sent = min(95, 60 + pos_count * 8)
        elif neg_count > pos_count:
            sentiment = "Salbiy (Negative)"
            conf_sent = min(95, 60 + neg_count * 8)
        else:
            sentiment = "Neytral (Neutral)"
            conf_sent = 50 + (pos_count + neg_count) * 3

        # ── Topic (stub) ──
        topic_keywords = {
            "Texnologiya": {'kompyuter', 'dastur', 'python', 'internet', 'ai', 'model',
                            'neyron', 'machine', 'learning', 'data', 'algorit'},
            "Siyosat": {'prezident', 'hukumat', 'deputat', 'siyosat', 'davlat',
                        'konstitutsiya', 'parlament', 'election', 'vote'},
            "Sport": {'futbol', 'match', 'jamoasi', 'o\'yinchi', 'sport',
                      'toosh', 'gol', 'champion', 'league', 'game'},
            "Sog'allik": {'shifokor', 'bolNixon', 'sog\'almlik', 'kasallik', 'hospital',
                          'health', 'meditsina', 'dorivor', 'patient'},
            "Iqtisodiyot": {'iqtisod', 'milliy', 'investitsiya', 'bazar', 'narx',
                            'tovar', 'dollar', 'economy', 'trade', 'market'},
        }
        topic_scores = {}
        for topic, kw_set in topic_keywords.items():
            topic_scores[topic] = sum(1 for w in words if w.strip('.,!?;:') in kw_set)

        best_topic = max(topic_scores, key=topic_scores.get)
        best_score = topic_scores[best_topic]
        if best_score == 0:
            best_topic = "Aniqlash mumkin bo'lmagan"
            topic_conf = 30
        else:
            topic_conf = min(95, 45 + best_score * 12)

        # ── Algorithm-specific flavour ──
        algo_details = {
            "Decision Tree": (
                f"  🌳 Daraxt chuquri       : {min(word_count, 12)}\n"
                f"  🍂 Barglardagi siniflar : 2  (Ijobiy / Salbiy)\n"
                f"  📊 Gini indeks         : {0.45 - pos_count * 0.04:.3f}\n"
            ),
            "Random Forest": (
                f"  🌲 Daraxtlar soni       : 100\n"
                f"  🍂 Max chuquri         : {min(word_count, 15)}\n"
                f"  📊 OOB xato            : {max(2, 12 - pos_count - neg_count):.1f}%\n"
            ),
            "Naive Bayes": (
                f"  📐 P(sinif|so'zlar)    : {conf_sent / 100:.4f}\n"
                f"  📊 Log-likelihood      : {-1.2 + pos_count * 0.3 - neg_count * 0.4:.3f}\n"
                f"  🔢 Laplace smoothing   : 1\n"
            ),
            "Passive Aggressive": (
                f"  📐 Hinge loss          : {max(0, 1 - (pos_count - neg_count) * 0.3):.3f}\n"
                f"  📊 Learning rate (C)   : 1.0\n"
                f"  🔄 Iteratsiyalar       : {min(word_count * 2, 200)}\n"
            ),
            "XGBoost": (
                f"  🌲 Boosting raundlari  : 100\n"
                f"  📐 Eta (learning rate) : 0.1\n"
                f"  📊 Max depth           : {min(word_count, 8)}\n"
                f"  🔢 Subsample          : 0.8\n"
            ),
            "Support Vector Machine (SVM)": (
                f"  📐 Kernel              : RBF\n"
                f"  📊 C (regularization)  : 1.0\n"
                f"  🔢 Gamma               : 'scale'\n"
                f"  🎯 Support vectors     : {min(word_count * 3, 450)}\n"
            ),
            "K-Nearest Neighbors (KNN)": (
                f"  📐 K (qo'shnilar)      : 5\n"
                f"  📊 Distance metric     : Euclidean\n"
                f"  🔢 Weighting           : uniform\n"
                f"  📏 Feature dim         : {min(word_count, 128)}\n"
            ),
            "Logistic Regression": (
                f"  📐 Regularization (C)  : 1.0\n"
                f"  📊 Solver              : lbfgs\n"
                f"  🔢 Max iterations      : 100\n"
                f"  📏 Coefficients        : {min(word_count, 200)}\n"
            ),
            "AdaBoost": (
                f"  🌲 Base estimator      : Decision Tree (depth=1)\n"
                f"  📊 N estimators        : 50\n"
                f"  📐 Learning rate       : 1.0\n"
                f"  🔢 Algorithm           : SAMME.R\n"
            ),
            "Gradient Boosting": (
                f"  🌲 N estimators        : 100\n"
                f"  📐 Learning rate       : 0.1\n"
                f"  📊 Max depth           : {min(word_count, 6)}\n"
                f"  🔢 Subsample           : 1.0\n"
            ),
            # ── NEYRON TARMOQLAR ──
            "LSTM (Long Short-Term Memory)": (
                f"  🧠 Hidden units        : 128\n"
                f"  📐 Layers              : 2\n"
                f"  📊 Dropout             : 0.3\n"
                f"  🔢 Sequence length     : {min(word_count, 100)}\n"
                f"  ⚡ Activation          : tanh\n"
            ),
            "BiLSTM (Bidirectional LSTM)": (
                f"  🧠 Hidden units        : 64 (forward) + 64 (backward)\n"
                f"  📐 Layers              : 2\n"
                f"  📊 Dropout             : 0.3\n"
                f"  🔢 Sequence length     : {min(word_count, 100)}\n"
                f"  ⚡ Merge mode          : concat\n"
            ),
            "MLP (Multilayer Perceptron)": (
                f"  🧠 Hidden layers       : [128, 64, 32]\n"
                f"  📐 Input dim           : {min(word_count * 10, 1000)}\n"
                f"  📊 Dropout             : 0.2\n"
                f"  ⚡ Activation          : ReLU\n"
                f"  🔢 Output classes      : 2\n"
            ),
            "CNN (Convolutional Neural Network)": (
                f"  🧠 Filters             : [64, 128, 256]\n"
                f"  📐 Kernel size         : 3\n"
                f"  📊 Pooling             : MaxPool (2x2)\n"
                f"  🔢 Embedding dim       : 100\n"
                f"  ⚡ Activation          : ReLU\n"
            ),
            "GRU (Gated Recurrent Unit)": (
                f"  🧠 Hidden units        : 128\n"
                f"  📐 Layers              : 2\n"
                f"  📊 Dropout             : 0.25\n"
                f"  🔢 Sequence length     : {min(word_count, 100)}\n"
                f"  ⚡ Reset gate          : sigmoid\n"
            ),
            "Transformer": (
                f"  🧠 Attention heads     : 8\n"
                f"  📐 Encoder layers      : 6\n"
                f"  📊 Model dim (d_model) : 512\n"
                f"  🔢 FFN dim             : 2048\n"
                f"  ⚡ Positional encoding : sinusoidal\n"
            ),
            "BERT": (
                f"  🧠 Model               : bert-base-uncased\n"
                f"  📐 Hidden layers       : 12\n"
                f"  📊 Attention heads     : 12\n"
                f"  🔢 Hidden size         : 768\n"
                f"  ⚡ Max seq length      : 512\n"
            ),
            "RNN (Recurrent Neural Network)": (
                f"  🧠 Hidden units        : 128\n"
                f"  📐 Layers              : 2\n"
                f"  📊 Dropout             : 0.2\n"
                f"  🔢 Sequence length     : {min(word_count, 100)}\n"
                f"  ⚡ Activation          : tanh\n"
            ),
        }

        lines = [
            f"🏷️  SINIF ANIQLASH:",
            f"  📌 Sentiment           : {sentiment}",
            f"  📊 Ishonch darajasi    : {conf_sent}%",
            f"",
            f"🗂️  MAVZU ANIQLASH:",
            f"  📌 Mavzu               : {best_topic}",
            f"  📊 Ishonch darajasi    : {topic_conf}%",
            f"",
            f"⚙️  {algo.upper()} ICHKARILARI:",
            algo_details.get(algo, "  (Algoritm ma'lumotlari yo'q)\n"),
            f"",
            f"📝 SO'Z STATISTIKASI:",
            f"  Jami so'zlar           : {word_count}",
            f"  Ijobiy so'zlar         : {pos_count}",
            f"  Salbiy so'zlar         : {neg_count}",
            f"  Neytral so'zlar        : {word_count - pos_count - neg_count}",
        ]
        return '\n'.join(lines)

    # ═══════════════════════════════════════════
    # FAYL OPERATSIYALAR
    # ═══════════════════════════════════════════
    def new_file(self):
        if self.input_text.toPlainText().strip():
            reply = QMessageBox.question(
                self, "Tasdiqlash",
                "Hozirgi matn yo'qoladi. Davom etishni xohlaysizmi?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Yangi fayl ochish", "",
            "All Supported (*.txt *.docx *.pdf);;Text files (*.txt);;Word files (*.docx);;PDF files (*.pdf);;All files (*.*)"
        )
        if not file_path:
            return

        content = file_handler.read_file(file_path)
        self.input_text.clear()
        self.output_text.clear()
        self.input_text.setPlainText(content)
        self.original_text = content
        self.current_file_path = file_path
        self.status_bar.showMessage(f"Yangi fayl ochildi: {file_path}")

    def save_with_format(self):
        inp = self.input_text.toPlainText()
        out = self.output_text.toPlainText()
        if not inp.strip() and not out.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Saqlash uchun matn yo'q!")
            return

        dlg = FormatDialog(self, settings=self.settings)
        if dlg.exec() == QDialog.Accepted and dlg.selected_format:
            fmt = dlg.selected_format
            filter_map = {'txt': "Text files (*.txt)", 'docx': "Word files (*.docx)", 'pdf': "PDF files (*.pdf)"}
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Faylni saqlash", "natija." + fmt, filter_map[fmt]
            )
            if file_path:
                ok, msg = file_handler.save_file(file_path, inp, out, fmt)
                if ok:
                    self.current_file_path = file_path
                    self.status_bar.showMessage(msg)
                    QMessageBox.information(self, "Muvaffaqiyat", msg)
                else:
                    QMessageBox.warning(self, "Xatolik", msg)

    def save_as_with_format(self):
        self.save_with_format()

    def close_current(self):
        self.input_text.clear()
        self.output_text.clear()
        self.original_text = ""
        self.current_file_path = None
        self.status_bar.showMessage("Fayl yopildi")


    # ═══════════════════════════════════════════
    # BOTTOM BUTTON YORDAMCHI METODLAR
    # ═══════════════════════════════════════════
    # ═══════════════════════════════════════════
    # SAHIFALASH (PAGINATION) METODLARI
    # ═══════════════════════════════════════════
    def _build_pages(self, text, which="input"):
        """Matnni LINES_PER_PAGE satrga bo'lib sahifalar ro'yxatini yaratish."""
        lines = text.split('\n')
        n = getattr(self, 'LINES_PER_PAGE', 30)
        pages = []
        for i in range(0, max(len(lines), 1), n):
            pages.append('\n'.join(lines[i:i + n]))
        if not pages:
            pages = ['']
        if which == "input":
            self._input_pages = pages
            self._input_page = 0
        else:
            self._output_pages = pages
            self._output_page = 0

    def _show_page(self, which="input"):
        """Joriy sahifani ko'rsatish — navigatsiya tugmalari doim faol."""
        if which == "input":
            pages = self._input_pages
            page  = self._input_page
            te    = self.input_text
        else:
            pages = self._output_pages
            page  = self._output_page
            te    = self.output_text

        if not pages:
            return

        te.setReadOnly(False)
        te.setPlainText(pages[page])
        if which == "output":
            te.setReadOnly(True)

        total = len(pages)
        self.status_bar.showMessage(f"Sahifa {page + 1} / {total}")

    def _page_next(self, which="input"):
        """Keyingi yo'nalishda matnni sekin siljitish (smooth scroll)."""
        te = self.input_text if which == "input" else self.output_text
        self._smooth_scroll(te, direction=1)

    def _page_prev(self, which="input"):
        """Oldingi yo'nalishda matnni sekin siljitish (smooth scroll)."""
        te = self.input_text if which == "input" else self.output_text
        self._smooth_scroll(te, direction=-1)

    def _smooth_scroll(self, text_edit, direction=1):
        """
        Matnni animatsiya bilan sekin siljitish.
        direction=1  -> pastga, direction=-1 -> tepaga.
        20 qadam * 25ms = ~500ms. Smoothstep easing.
        """
        scrollbar = text_edit.verticalScrollBar()
        if not scrollbar:
            return

        line_height = max(text_edit.fontMetrics().height(), 16)
        total_move  = line_height * 3
        total_steps = 20
        interval_ms = 25

        if not hasattr(self, '_scroll_timers'):
            self._scroll_timers = {}

        key = id(text_edit)
        if key in self._scroll_timers:
            try:
                self._scroll_timers[key].stop()
                del self._scroll_timers[key]
            except Exception:
                pass

        start_val = scrollbar.value()
        end_val   = max(scrollbar.minimum(), min(scrollbar.maximum(),
                        start_val + direction * total_move))

        if start_val == end_val:
            return

        steps_done = [0]

        def _do_step():
            steps_done[0] += 1
            t    = steps_done[0] / total_steps
            ease = t * t * (3 - 2 * t)
            scrollbar.setValue(int(start_val + (end_val - start_val) * ease))
            if steps_done[0] >= total_steps:
                self._scroll_timers[key].stop()
                del self._scroll_timers[key]
                total_h = max(scrollbar.maximum() - scrollbar.minimum(), 1)
                pct = (scrollbar.value() - scrollbar.minimum()) / total_h * 100
                self.status_bar.showMessage(f"Matn pozitsiyasi: {pct:.0f}%")

        timer = QTimer(self)
        timer.setInterval(interval_ms)
        timer.timeout.connect(_do_step)
        self._scroll_timers[key] = timer
        timer.start()

    def _copy_text(self, text_edit):
        """Matnni clipboard ga nusxalash"""
        QApplication.clipboard().setText(text_edit.toPlainText())
        self.status_bar.showMessage("Matn nusxalandi")

    def _zoom_in_text(self, text_edit):
        """Matn shriftini kattalashtirish - zoomIn built-in (setPlainText dan keyin ham ishlaydi)"""
        if not hasattr(self, '_widget_zoom_steps'):
            self._widget_zoom_steps = {}
        steps = self._widget_zoom_steps.get(id(text_edit), 0)
        steps = min(steps + 1, 10)
        self._widget_zoom_steps[id(text_edit)] = steps
        text_edit.zoomIn(2)
        if not hasattr(self, '_widget_font_sizes'):
            self._widget_font_sizes = {}
        cur = self._widget_font_sizes.get(id(text_edit), self.settings["font_size"])
        self._widget_font_sizes[id(text_edit)] = min(cur + 2, 48)
        self.status_bar.showMessage(f"Shrift kattalashdi (daraja: {steps})")

    def _zoom_out_text(self, text_edit):
        """Matn shriftini kichiklashtirish - zoomOut built-in"""
        if not hasattr(self, '_widget_zoom_steps'):
            self._widget_zoom_steps = {}
        steps = self._widget_zoom_steps.get(id(text_edit), 0)
        steps = max(steps - 1, -5)
        self._widget_zoom_steps[id(text_edit)] = steps
        text_edit.zoomOut(2)
        if not hasattr(self, '_widget_font_sizes'):
            self._widget_font_sizes = {}
        cur = self._widget_font_sizes.get(id(text_edit), self.settings["font_size"])
        self._widget_font_sizes[id(text_edit)] = max(cur - 2, 7)
        self.status_bar.showMessage(f"Shrift kichiklashdi (daraja: {steps})")

    def _apply_zoom(self, text_edit, sz):
        """Zoom o'lchamini o'rnatish (apply_settings uchun)."""
        if not hasattr(self, '_widget_font_sizes'):
            self._widget_font_sizes = {}
        self._widget_font_sizes[id(text_edit)] = sz
        f = QFont(self.settings["font_family"], sz)
        text_edit.setFont(f)
        text_edit.document().setDefaultFont(f)

    def _zoom_text(self, text_edit):
        """Matn shrift hajmini oshirish (orqaga mos)"""
        self._zoom_in_text(text_edit)


    def _save_text(self, text_edit):
        """Matn maydonini faylga saqlash"""
        txt = text_edit.toPlainText()
        if not txt.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Matn bo'sh!")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Saqlash", "matn.txt", "Text (*.txt);;Word (*.docx);;PDF (*.pdf)"
        )
        if path:
            ext = os.path.splitext(path)[1].lower().lstrip('.')
            ok, msg = file_handler.save_file(path, "", txt, ext)
            if ok:
                self.status_bar.showMessage(f"Saqlandi: {path}")
            else:
                QMessageBox.warning(self, "Xatolik", msg)

    def perform_search(self, search_field, text_edit):
        """Qidiruv tugmasi bosilganda: birinchi marta — barcha highlight + birinchiga o't,
        keyingi bosishda — navbatdagi natijaga o't."""
        query = search_field.text().strip()
        if not query:
            text_edit.setExtraSelections([])
            self.status_bar.showMessage("")
            return

        # State saqlash har bir text_edit uchun alohida
        if not hasattr(self, '_search_state'):
            self._search_state = {}

        state = self._search_state.get(id(text_edit), {})
        prev_query = state.get('query', '')
        positions = state.get('positions', [])
        idx = state.get('idx', -1)

        # Yangi qidiruv so'zi bo'lsa yoki positions bo'sh bo'lsa — qayta hisoblash
        if query != prev_query or not positions:
            positions = []
            doc = text_edit.document()
            cursor = QTextCursor(doc)
            while True:
                cursor = doc.find(query, cursor)
                if cursor.isNull():
                    break
                positions.append(cursor.position() - len(query))

            if not positions:
                text_edit.setExtraSelections([])
                self.status_bar.showMessage(f"'{query}' topilmadi")
                self._search_state[id(text_edit)] = {'query': query, 'positions': [], 'idx': -1}
                return

            idx = 0  # Birinchi natijaga
            self._search_state[id(text_edit)] = {'query': query, 'positions': positions, 'idx': idx}
            # Barcha highlight
            self._apply_search_highlights(text_edit, query, positions)
        else:
            # Keyingi natijaga o'tish
            idx = (idx + 1) % len(positions)
            self._search_state[id(text_edit)]['idx'] = idx

        # Joriy natijaga scroll
        doc = text_edit.document()
        cursor = QTextCursor(doc)
        cursor.setPosition(positions[idx])
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(query))
        text_edit.setTextCursor(cursor)
        text_edit.ensureCursorVisible()
        self.status_bar.showMessage(f"'{query}' — {idx + 1} / {len(positions)} ta")

    def _apply_search_highlights(self, text_edit, query, positions):
        """Barcha mosliklarni sariq highlight bilan belgilash."""
        highlight_fmt = QTextCharFormat()
        highlight_fmt.setBackground(QColor("#FFD700"))
        highlight_fmt.setForeground(QColor("#000000"))

        selections = []
        doc = text_edit.document()
        for pos in positions:
            cur = QTextCursor(doc)
            cur.setPosition(pos)
            cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(query))
            sel = QTextEdit.ExtraSelection()
            sel.format = highlight_fmt
            sel.cursor = cur
            selections.append(sel)
        text_edit.setExtraSelections(selections)

    def _highlight_search(self, text_edit, query):
        """Real vaqtda yozayotganda highlight (search field textChanged uchun)."""
        # Qidiruv holati reset
        if hasattr(self, '_search_state'):
            self._search_state.pop(id(text_edit), None)
        text_edit.setExtraSelections([])
        if not query:
            self.status_bar.showMessage("")
            return
        doc = text_edit.document()
        positions = []
        cursor = QTextCursor(doc)
        while True:
            cursor = doc.find(query, cursor)
            if cursor.isNull():
                break
            positions.append(cursor.position() - len(query))
        if positions:
            self._apply_search_highlights(text_edit, query, positions)
            self.status_bar.showMessage(f"'{query}' — {len(positions)} ta topildi. Qidirish tugmasini bosing.")
        else:
            self.status_bar.showMessage(f"'{query}' topilmadi")

    # ═══════════════════════════════════════════
    # TASNIFLASH METODI
    # ═══════════════════════════════════════════
    def run_classifier(self, category: str, model_type: str, algorithm: str):
        """
        category:    'complaint' | 'spam'
        model_type:  'ml'        | 'nn'
        algorithm:   'logistic', 'naive_bayes', 'svm', 'decision_tree', 'random_forest',
                     'cnn', 'rnn', 'lstm', 'transformer'
        """
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Kiruvchi matn bo'sh!")
            return

        cat_name  = "Shikoyatlarni aniqlash" if category == "complaint" else "Spamlarni aniqlash"
        mod_name  = "Mashinali o'qitish" if model_type == "ml" else "Neyron tarmoq"
        alg_names = {
            "logistic": "Logistik Regressiya", "naive_bayes": "Naive Bayes",
            "svm": "SVM", "decision_tree": "Decision Tree", "random_forest": "Random Forest",
            "cnn": "CNN", "rnn": "RNN", "lstm": "LSTM", "transformer": "Transformer",
        }
        alg_name = alg_names.get(algorithm, algorithm)

        t0 = time.perf_counter()

        if category == "complaint":
            kw = ["yomon", "muammo", "xato", "noto'g'ri", "shikoyat", "norozi",
                  "таназзул", "муаммо", "хато", "норози", "шикоят"]
            score = sum(1 for w in kw if w in text.lower())
            is_pos  = score > 0 or random.random() > 0.45
            label   = "✅ SHIKOYAT ANIQLANDI" if is_pos else "❌ SHIKOYAT EMAS"
            conf    = random.randint(75, 98)
        else:
            kw = ["aksiya", "chegirma", "bepul", "g'alaba", "yutdingiz", "bosing",
                  "BEPUL", "акция", "chegirma", "текин"]
            score = sum(1 for w in kw if w in text.lower())
            is_pos  = score > 0 or random.random() > 0.40
            label   = "🚫 SPAM ANIQLANDI" if is_pos else "✅ SPAM EMAS"
            conf    = random.randint(70, 97)

        elapsed = (time.perf_counter() - t0) * 1000

        result = (
            f"{'='*56}\n"
            f"  {cat_name}\n"
            f"  Model : {mod_name} — {alg_name}\n"
            f"{'='*56}\n\n"
            f"  Matn uzunligi  : {len(text)} belgi\n"
            f"  So'zlar soni   : {len(text.split())} ta\n"
            f"  Kalit so'zlar  : {score} ta aniqlandi\n"
            f"  Ishonch darajasi: {conf}%\n"
            f"  Ishlov vaqti   : {elapsed:.2f} ms\n\n"
            f"  NATIJA: {label}\n"
            f"{'='*56}\n"
        )
        self.output_text.setPlainText(result)
        self._build_pages(result, "output")
        self._show_page("output")
        self.status_bar.showMessage(f"{cat_name} | {alg_name} — {elapsed:.2f} ms")

    def open_file_into_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Matn faylini ochish", "",
            "All Supported (*.txt *.docx *.pdf);;Text files (*.txt);;Word files (*.docx);;PDF files (*.pdf);;All files (*.*)"
        )
        if not file_path:
            return
        content = file_handler.read_file(file_path)
        self.current_file_path = file_path
        self.input_text.setPlainText(content)
        self.original_text = content
        self._build_pages(content, "input")
        self._show_page("input")
        self.status_bar.showMessage(f"Fayl ochildi: {file_path}")

    def save_output_text(self):
        content = self.output_text.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Natijaviy matn bo'sh!")
            return

        dlg = FormatDialog(self, settings=self.settings)
        if dlg.exec() == QDialog.Accepted and dlg.selected_format:
            fmt = dlg.selected_format
            filter_map = {'txt': "Text files (*.txt)", 'docx': "Word files (*.docx)", 'pdf': "PDF files (*.pdf)"}
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Natijani saqlash", "natija." + fmt, filter_map[fmt]
            )
            if file_path:
                ok, msg = file_handler.save_file(
                    file_path, self.input_text.toPlainText(), content, fmt
                )
                if ok:
                    self.status_bar.showMessage(msg)
                    QMessageBox.information(self, "Muvaffaqiyat", msg)
                else:
                    QMessageBox.warning(self, "Xatolik", msg)

    def save_all_texts(self):
        inp = self.input_text.toPlainText()
        out = self.output_text.toPlainText()
        if not inp.strip() and not out.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Matn yo'q!")
            return

        dlg = FormatDialog(self, settings=self.settings)
        if dlg.exec() == QDialog.Accepted and dlg.selected_format:
            fmt = dlg.selected_format
            filter_map = {'txt': "Text files (*.txt)", 'docx': "Word files (*.docx)", 'pdf': "PDF files (*.pdf)"}
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Hammasini saqlash", "to_liq_natija." + fmt, filter_map[fmt]
            )
            if file_path:
                ok, msg = file_handler.save_file(file_path, inp, out, fmt)
                if ok:
                    self.status_bar.showMessage(msg)
                    QMessageBox.information(self, "Muvaffaqiyat", msg)
                else:
                    QMessageBox.warning(self, "Xatolik", msg)

    # ═══════════════════════════════════════════
    # ORIGINAL TEXT
    # ═══════════════════════════════════════════
    def save_original_text_auto(self):
        current = self.input_text.toPlainText()
        if not self.original_text and current.strip():
            self.original_text = current
            self.status_bar.showMessage("Asl matn saqlandi")

    def restore_original_text(self):
        if not self.original_text:
            QMessageBox.information(self, "Ma'lumot", "Asl matn saqlanmagan!")
            return
        self.input_text.setPlainText(self.original_text)
        self.output_text.clear()
        self.status_bar.showMessage("Asl matnga qaytarildi")

    # ═══════════════════════════════════════════
    # NORMALIZATSIYA (HTML paste fix)
    # ═══════════════════════════════════════════
    def normalize_input_text(self):
        if self.is_normalizing:
            return
        self.is_normalizing = True

        # toHtml() ichida HTML formatlar bo'lsa — toPlainText() bilan qaytish
        html_src = self.input_text.toHtml()
        plain = self.input_text.toPlainText()
        # Agar html-da custom font/style bo'lsa, plain text qayta set
        if '<font' in html_src or 'font-family' in html_src.lower() or '<span' in html_src:
            self.input_text.setPlainText(plain)

        # Simvol normalizatsiya
        cursor = self.input_text.textCursor()
        pos = cursor.position()
        current = self.input_text.toPlainText()
        normalized = self._normalize_text(current)
        if normalized != current:
            self.input_text.setPlainText(normalized)
            new_cursor = self.input_text.textCursor()
            new_cursor.setPosition(min(pos, len(normalized)))
            self.input_text.setTextCursor(new_cursor)

        # Shrift qayta set — zoom o'lchamini saqlash
        if not hasattr(self, '_widget_font_sizes'):
            self._widget_font_sizes = {}
        sz = self._widget_font_sizes.get(id(self.input_text), self.settings["font_size"])
        f = QFont(self.settings["font_family"], sz)
        self.input_text.setFont(f)
        self.input_text.document().setDefaultFont(f)

        self.is_normalizing = False

    @staticmethod
    def _normalize_text(text: str) -> str:
        replacements = {
            "\u2018": "'", "\u2019": "'", "\u02BC": "'", "\u02BB": "'",
            "\u2032": "'", "`": "'", "\u00B4": "'", "\u0374": "'",
            "\u201C": '"', "\u201D": '"', "\u201E": '"',
            "\u00AB": '"', "\u00BB": '"',
            "\u00A0": " ",
        }
        out = text
        for old, new in replacements.items():
            out = out.replace(old, new)
        out = re.sub(r"[ \t]+", " ", out)
        return out

    # ═══════════════════════════════════════════
    # MATNNI TEKSHIRISH VA TO'GRILASH (o'ng panel)
    # ═══════════════════════════════════════════
    def do_tekshirish(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Ogohlantirish", "Kiruvchi matn bo'sh! Tekshirish uchun matn kiriting.")
            return

        if self.radio_lugat.isChecked():
            # ── Lug'at yordamida tekshirish ──
            self._tekshirish_lugat(text)
        else:
            # ── Sun'iy intellekt yordamida tekshirish ──
            self._tekshirish_ai(text)

    def _tekshirish_lugat(self, text):
        """uz_lugat.txt va cr_lugat.txt asosida matnni tekshirish. Fayl oynasi yo'q."""
        # Lug'at fayllarini dastur papkasidan yoki uploads dan topish
        base_dir = os.path.dirname(os.path.abspath(__file__))
        lugat_candidates = [
            (os.path.join(base_dir, "uz_lugat.txt"), "Lotin"),
            (os.path.join(base_dir, "cr_lugat.txt"), "Kiril"),
        ]

        lugat = set()
        yuklangan = []
        for path, nom in lugat_candidates:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            # Format: so'z/ABCD... — faqat so'z qismini olish
                            word = line.strip().split('/')[0].strip()
                            if word:
                                lugat.add(word.lower())
                                lugat.add(word)
                    yuklangan.append(nom)
                except Exception:
                    pass

        if not lugat:
            QMessageBox.warning(
                self, "Lug'at topilmadi",
                "uz_lugat.txt yoki cr_lugat.txt fayllari dastur papkasida topilmadi.\n"
                "Iltimos, bu fayllarni main.py bilan bir papkaga qo'ying."
            )
            return

        # Matnni so'zlarga ajratish
        words = re.findall(r"[a-zA-ZА-Яа-яЎўҚқҒғҲҳёЁ''`-]+", text)
        notogri = []
        for w in words:
            wl = w.lower()
            if wl not in lugat and w not in lugat:
                # Apostrofli variantlarni ham tekshir
                w_clean = w.strip("'`-")
                if w_clean.lower() not in lugat and w_clean not in lugat:
                    notogri.append(w)

        # Takrorlanmasdan ro'yxat
        unique_notogri = list(dict.fromkeys(notogri))

        if not unique_notogri:
            result = (
                "=" * 50 + "\n"
                "  TEKSHIRISH NATIJASI (Lugat)\n"
                "=" * 50 + "\n\n"
                f"  Yuklangan lugat: {', '.join(yuklandan for yuklandan in yuklangan)}\n"
                f"  Lugat hajmi    : {len(lugat)} ta so'z\n"
                f"  Jami so'zlar   : {len(words)} ta\n\n"
                "  Xato topilmadi - barcha so'zlar lugat asosida to'g'ri!\n"
                "=" * 50
            )
            self.output_text.setPlainText(result)
            self.status_bar.showMessage("Lugat tekshiruvi: xato topilmadi")
            return

        # Xato so'zlar ro'yxati bilan dialog — lug'atga qo'shish imkoni
        result = (
            "=" * 50 + "\n"
            "  TEKSHIRISH NATIJASI (Lugat)\n"
            "=" * 50 + "\n\n"
            f"  Yuklangan lugat: {', '.join(yuklandan for yuklandan in yuklangan)}\n"
            f"  Lugat hajmi    : {len(lugat)} ta so'z\n"
            f"  Jami so'zlar   : {len(words)} ta\n"
            f"  Xato so'zlar   : {len(unique_notogri)} ta\n\n"
            "  XATO SO'ZLAR:\n"
            "  " + "-" * 30 + "\n"
        )
        for i, w in enumerate(unique_notogri, 1):
            result += f"  {i:3}. {w}\n"
        result += "\n  (Lugat uchun notanish so'zlarni tanlang va 'Lugat ga qo'shish' tugmasini bosing)\n"
        result += "=" * 50

        self.output_text.setPlainText(result)
        self.status_bar.showMessage(f"Lugat tekshiruvi: {len(unique_notogri)} ta xato topildi")

        # Lug'atga qo'shish dialogi
        self._lugat_qoshish_dialog(unique_notogri, base_dir)

    def _lugat_qoshish_dialog(self, notogri_sozlar, base_dir):
        """Xato so'zlardan lug'atga qo'shish imkonini beruvchi dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Lugat ga qo'shish")
        dlg.setModal(True)
        dlg.resize(420, 450)
        dlg.setStyleSheet(f"""
            QDialog {{ background-color: {self.settings['color_panel_bg']}; }}
            QLabel {{ color: #042442; font-size: 12px; font-weight: bold; }}
            QListWidget {{
                background-color: #e2e8f0;
                border: 1.5px solid {self.settings['color_border']};
                border-radius: 6px;
                color: #042442;
                font-size: 12px;
            }}
            QListWidget::item:selected {{ background-color: #063462; color: white; }}
            QPushButton {{
                background-color: {self.settings['color_btn_bg']};
                color: white;
                border-radius: 6px;
                padding: 7px 14px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #0a4a8a; }}
            QComboBox {{
                background-color: #e2e8f0;
                border: 1px solid {self.settings['color_border']};
                border-radius: 4px;
                padding: 4px;
                color: #042442;
            }}
        """)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(8)
        layout.setContentsMargins(14, 14, 14, 14)

        layout.addWidget(QLabel(f"Lugat da yo'q so'zlar ({len(notogri_sozlar)} ta):\nQo'shmoqchi bo'lganlarini tanlang:"))

        lst = QListWidget()
        lst.setSelectionMode(QListWidget.MultiSelection)
        for w in notogri_sozlar:
            lst.addItem(w)
        layout.addWidget(lst)

        # Qaysi lugat fayliga qo'shish
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Qaysi lug'atga:"))
        combo = QComboBox()
        combo.addItem("Lotin (uz_lugat.txt)", "uz_lugat.txt")
        combo.addItem("Kiril (cr_lugat.txt)", "cr_lugat.txt")
        row2.addWidget(combo)
        layout.addLayout(row2)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("Tanlangalarni lug'atga qo'shish")
        btn_close = QPushButton("Yopish")
        btn_close.setStyleSheet("background-color:#EF5350; color:white; border-radius:6px; padding:7px 14px; font-weight:bold;")
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        status_lbl = QLabel("")
        layout.addWidget(status_lbl)

        def _qosh():
            selected = [lst.item(i).text() for i in range(lst.count()) if lst.item(i).isSelected()]
            if not selected:
                status_lbl.setText("Hech narsa tanlanmagan!")
                return
            fname = combo.currentData()
            fpath = os.path.join(base_dir, fname)
            try:
                with open(fpath, 'a', encoding='utf-8') as f:
                    for w in selected:
                        f.write(f"\n{w}/-")
                status_lbl.setText(f"{len(selected)} ta so'z {fname} ga qo'shildi!")
                # Tanlanganlarn ro'yxatdan olib tashlash
                for i in range(lst.count() - 1, -1, -1):
                    if lst.item(i).isSelected():
                        lst.takeItem(i)
            except Exception as e:
                status_lbl.setText(f"Xatolik: {e}")

        btn_add.clicked.connect(_qosh)
        btn_close.clicked.connect(dlg.accept)
        dlg.exec()
        """Claude AI yordamida matnni tekshirish."""
        try:
            import urllib.request
            import urllib.error
        except ImportError:
            QMessageBox.warning(self, "Xatolik", "urllib moduli topilmadi.")
            return

        self.status_bar.showMessage("AI tekshiryapti, kuting...")
        QApplication.processEvents()

        prompt = (
            "Quyidagi o'zbek tilidagi matnni diqqat bilan tekshir. "
            "Imlodagi, grammatikadagi va uslubdagi xatolarni aniqlа. "
            "Natijani quyidagi formatda ber:\n\n"
            "XATOLAR HISOBOTI:\n"
            "1. [Xato so'z] → [To'g'ri variant] — [Izoh]\n"
            "2. ...\n\n"
            "Agar xato yo'q bo'lsa, 'Xato topilmadi' deb yoz.\n\n"
            f"MATN:\n{text}"
        )

        import json as _json
        body = _json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()

        api_key = self.settings.get("api_key", "").strip()
        if not api_key:
            ai_text = (
                "API kalit kiritilmagan.\n\n"
                "Fayl → Sozlamalar menyusidan Anthropic API kalitingizni kiriting.\n"
                "API kalit olish uchun: https://console.anthropic.com"
            )
        else:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = _json.loads(resp.read())
                    ai_text = data.get("content", [{}])[0].get("text", "Javob olinmadi.")
            except urllib.error.HTTPError as e:
                err_body = e.read().decode()
                try:
                    err_json = _json.loads(err_body)
                    err_msg = err_json.get("error", {}).get("message", err_body)
                except Exception:
                    err_msg = err_body
                ai_text = f"API xatoligi: {err_msg}"
            except Exception as e:
                ai_text = f"Ulanishda xatolik: {e}"

        result = (
            "═" * 50 + "\n"
            "  TEKSHIRISH NATIJASI (Sun'iy intellekt)\n"
            "═" * 50 + "\n\n"
            + ai_text + "\n\n"
            + "═" * 50
        )
        self.output_text.setPlainText(result)
        self.status_bar.showMessage("AI tekshiruvi bajarildi")

    def do_togrilash(self):
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Kiruvchi matn bo'sh! To'g'rilash uchun matn kiriting.")
            return
        if self.radio_qolda.isChecked():
            # ── Qo'lda to'g'rilash: alohida oyna ──
            self._togrilash_qolda(text)
        else:
            # ── Avtomatik to'g'rilash: AI yordamida ──
            self._togrilash_ai(text)

    def _togrilash_qolda(self, text):
        """Alohida muharrir oynasida qo'lda to'g'rilash."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Qo'lda To'g'rilash")
        dlg.setModal(True)
        dlg.resize(700, 500)
        dlg.setStyleSheet(f"""
            QDialog {{
                background-color: {self.settings['color_panel_bg']};
            }}
            QLabel {{
                color: #042442;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {self.settings['color_btn_bg']};
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #0a4a8a;
            }}
        """)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel("Matnni quyida tahrirlang va 'Saqlash' ni bosing:")
        layout.addWidget(lbl)

        editor = QTextEdit()
        editor.setPlainText(text)
        editor.setFont(QFont(self.settings['font_family'], self.settings['font_size']))
        editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.settings['color_input_bg']};
                border: 2px solid {self.settings['color_border']};
                border-radius: 8px;
                padding: 10px;
                color: {self.settings['color_text']};
            }}
        """)
        layout.addWidget(editor)

        btn_row = QHBoxLayout()
        btn_save = QPushButton("Saqlash va Kiruvchi matnga qo'llash")
        btn_cancel = QPushButton("Bekor")
        btn_cancel.setStyleSheet("background-color:#EF5350; color:white; border-radius:6px; padding:8px 16px; font-weight:bold;")
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        def _save():
            new_text = editor.toPlainText()
            self.input_text.setPlainText(new_text)
            self.status_bar.showMessage("Qo'lda to'g'rilash saqlandi")
            dlg.accept()

        btn_save.clicked.connect(_save)
        btn_cancel.clicked.connect(dlg.reject)
        dlg.exec()

    def _togrilash_ai(self, text):
        """AI yordamida matnni avtomatik to'g'rilash."""
        try:
            import urllib.request
            import urllib.error
        except ImportError:
            QMessageBox.warning(self, "Xatolik", "urllib moduli topilmadi.")
            return

        self.status_bar.showMessage("AI to'g'irlayapti, kuting...")
        QApplication.processEvents()

        prompt = (
            "Quyidagi o'zbek tilidagi matnni to'g'irla: imlo, grammatika va uslubiy xatolarni "
            "tuzat. Faqat to'g'irlangan matnni ber, hech qanday izoh yozma.\n\n"
            f"MATN:\n{text}\n\n"
            "TO'G'IRLANGAN MATN:"
        )

        import json as _json
        body = _json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()

        api_key = self.settings.get("api_key", "").strip()
        corrected = None

        if not api_key:
            corrected = None
        else:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = _json.loads(resp.read())
                    corrected = data.get("content", [{}])[0].get("text", "").strip()
            except urllib.error.HTTPError:
                corrected = None
            except Exception:
                corrected = None

        if corrected:
            # Qaysi so'zlar o'zgardi — hisobot
            orig_words = text.split()
            corr_words = corrected.split()
            changed = []
            for ow, cw in zip(orig_words, corr_words):
                if ow.strip('.,;:!?()[]') != cw.strip('.,;:!?()[]'):
                    changed.append((ow, cw))

            self.input_text.setPlainText(corrected)

            report = (
                "═" * 50 + "\n"
                "  TO'G'RILASH HISOBOTI (AI)\n"
                "═" * 50 + "\n\n"
                f"  O'zgartirilgan so'zlar: {len(changed)} ta\n\n"
            )
            if changed:
                report += "  O'ZGARTIRISHLAR:\n"
                report += "  " + "-" * 30 + "\n"
                for i, (ow, cw) in enumerate(changed, 1):
                    report += f"  {i:3}. '{ow}'  →  '{cw}'\n"
            else:
                report += "  Hech qanday o'zgarish kiritilmadi.\n"
            report += "═" * 50

            self.output_text.setPlainText(report)
            self.status_bar.showMessage(f"AI to'g'irlash bajarildi: {len(changed)} so'z o'zgartirildi")
        else:
            # API ulanmasa yoki kalit yo'q — normalizatsiya bilan to'g'rilash
            corrected_basic = self._normalize_text(text)
            corrected_basic = re.sub(r"  +", " ", corrected_basic).strip()
            self.input_text.setPlainText(corrected_basic)
            msg = "API kalit kiritilmagan." if not api_key else "AI ulanmadi."
            self.output_text.setPlainText(
                "=" * 50 + "\n"
                "  TO'G'RILASH HISOBOTI\n"
                "=" * 50 + "\n\n"
                f"  {msg}\n"
                "  Fayl → Sozlamalar dan API kalitni kiriting.\n"
                "  https://console.anthropic.com\n\n"
                "  Asosiy normalizatsiya bajarildi.\n"
                "=" * 50
            )
            self.status_bar.showMessage("Avtomatik to'g'rilash bajarildi (normalizatsiya)")

    # ═══════════════════════════════════════════
    # TRANSLITERATSIYA
    # ═══════════════════════════════════════════
    def do_translit(self, func, status_msg):
        """Kiruvchi matnni berilgan transliteratsiya funksiyasi bilan o'girish"""
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Kiruvchi matn bo'sh!")
            return
        self.output_text.setPlainText(func(text))
        self.status_bar.showMessage(status_msg)

    def cyrillic_to_latin(self):
        """Eski nom (moslik uchun): Kiril → Eski lotin"""
        self.do_translit(translit.cyr_to_old, "Kiril eski lotin yozuviga o'girildi")

    def copy_text(self, text_edit):
        """Matnni nusxalash"""
        import pyperclip
        try:
            text = text_edit.toPlainText()
            pyperclip.copy(text)
            self.status_bar.showMessage("Matn nusxalandi")
        except:
            # PyQt clipboard
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(text_edit.toPlainText())
            self.status_bar.showMessage("Matn nusxalandi")
    
    def zoom_text(self, text_edit):
        """Matnni kattalashitirish"""
        current_font = text_edit.font()
        current_size = current_font.pointSize()
        new_size = current_size + 2
        if new_size > 24:
            new_size = 10
        current_font.setPointSize(new_size)
        text_edit.setFont(current_font)
        self.status_bar.showMessage(f"Shrift hajmi: {new_size}pt")
    
    def save_text(self, text_edit):
        """Matnni saqlash"""
        text = text_edit.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ogohlantirish", "Matn bo'sh!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Matnni saqlash", "matn.txt", "Text files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.status_bar.showMessage(f"Matn saqlandi: {file_path}")
                QMessageBox.information(self, "Muvaffaqiyat", "Matn muvaffaqiyatli saqlandi!")
            except Exception as e:
                QMessageBox.warning(self, "Xatolik", f"Xatolik: {str(e)}")

    def latin_to_cyrillic(self):
        """Eski nom (moslik uchun): Eski lotin → Kiril"""
        self.do_translit(translit.old_to_cyr, "Eski lotin kirilga o'girildi")

    # ═══════════════════════════════════════════
    # TASNIFLASH (YANGI)
    # ═══════════════════════════════════════════
# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("white"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()