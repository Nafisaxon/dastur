"""
O'zbek yozuvlari transliteratsiyasi
===================================
Uch yozuv tizimi:
  * Kiril
  * Eski lotin  (1995): Sh, Ch, Oʻ, Gʻ, Ng, tutuq belgisi ʼ
  * Yangi lotin (2026-yil 21-oktabr qonuni): Ş, Ç, Ö, Ğ, tutuq belgisi ʼ

Ommaviy funksiyalar:
  cyr_to_old, old_to_cyr, cyr_to_new, new_to_cyr, old_to_new, new_to_old
"""

import re
import unicodedata

# Apostrofning turli ko'rinishlari (kirishda hammasi taniladi)
APOS_CHARS = "'ʻʼ`‘’′"
APOS = "[" + re.escape(APOS_CHARS) + "]"

# Chiqishda rasmiy belgilar
OK_TURN = "\u02BB"   # ʻ  — oʻ, gʻ uchun
TUTUQ = "\u02BC"     # ʼ  — tutuq belgisi (maʼno)

LAT_LETTER = "A-Za-zŞşÇçÖöĞğ"


# ─────────────────────────────────────────────
# Umumiy yordamchilar
# ─────────────────────────────────────────────
def _case(src, out, prev_ch="", next_ch=""):
    """
    src (asl belgi) katta harf bo'lsa, out ni katta qilish.
    Ko'p belgili natija (sh, ch, o' ...) qo'shni harf ham katta bo'lsa
    to'liq KATTA (SH), aks holda faqat birinchi harf katta (Sh) bo'ladi.
    """
    if not src.isupper():
        return out
    if len(out) > 1 and (prev_ch.isupper() or next_ch.isupper()):
        return out.upper()
    return out[0].upper() + out[1:]


# ─────────────────────────────────────────────
# KIRIL → ESKI LOTIN
# ─────────────────────────────────────────────
_CYR_OLD = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'j', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': TUTUQ, 'ы': 'i', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'ў': 'o' + OK_TURN, 'қ': 'q', 'ғ': 'g' + OK_TURN, 'ҳ': 'h',
}
_CYR_VOWELS = set('аеёиоуўэюяыАЕЁИОУЎЭЮЯЫ')


def cyr_to_old(text: str) -> str:
    """Kiril → eski lotin (Sh, Ch, Oʻ, Gʻ)."""
    out = []
    n = len(text)
    for i, ch in enumerate(text):
        low = ch.lower()
        if low not in _CYR_OLD:
            out.append(ch)
            continue

        lat = _CYR_OLD[low]
        if low == 'е':
            # so'z boshida yoki unli/ъ/ь dan keyin: ye
            prev = text[i - 1] if i > 0 else ''
            if (not prev.isalpha()) or prev in _CYR_VOWELS or prev in 'ъьЪЬ':
                lat = 'ye'
        if not lat:
            continue

        prev_ch = text[i - 1] if i > 0 else ''
        next_ch = text[i + 1] if i + 1 < n else ''
        out.append(_case(ch, lat, prev_ch, next_ch))
    return ''.join(out)


# ─────────────────────────────────────────────
# ESKI LOTIN → KIRIL
# ─────────────────────────────────────────────
_OLD_CYR_SINGLE = {
    'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'ҳ',
    'i': 'и', 'j': 'ж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о',
    'p': 'п', 'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'v': 'в',
    'x': 'х', 'y': 'й', 'z': 'з',
}
_OLD_CYR_MULTI = {
    "o'": 'ў', "g'": 'ғ',
    'sh': 'ш', 'ch': 'ч', 'yo': 'ё', 'yu': 'ю', 'ya': 'я',
    'ye': 'е',  # faqat so'z boshida (pastda)
}

_OLD2CYR_RE = re.compile(
    r"(?P<ogs>[OoGg]" + APOS + r")"
    r"|(?P<tut>(?<=[A-Za-z])" + APOS + r"(?=[A-Za-z]))"
    r"|(?P<ye>(?<![A-Za-z" + re.escape(APOS_CHARS) + r"])[Yy][Ee])"
    r"|(?P<e0>(?<![A-Za-z" + re.escape(APOS_CHARS) + r"])[Ee])"
    r"|(?P<dig>[Ss][Hh]|[Cc][Hh]|[Yy][OoUuAa])"
    r"|(?P<one>[A-Za-z])"
)


def old_to_cyr(text: str) -> str:
    """
    Eski lotin → kiril.
    Eslatma: "ts" ni ц ga aylantirmaydi (ketsa, otsa kabi so'zlarda t+s bo'lgani uchun),
    "ishchi" kabi so'zlardagi sh+ch ham to'g'ri (ишчи) chiqadi.
    """
    text = unicodedata.normalize('NFC', text)

    def repl(m):
        s = m.group(0)
        g = m.lastgroup
        low = s.lower()
        if g == 'ogs':
            cyr = _OLD_CYR_MULTI[low[0] + "'"]
        elif g == 'tut':
            return 'ъ'
        elif g == 'ye':
            cyr = 'е'
        elif g == 'e0':
            cyr = 'э'
        elif g == 'dig':
            cyr = _OLD_CYR_MULTI[low]
        else:
            cyr = _OLD_CYR_SINGLE.get(low)
            if cyr is None:
                return s
        return cyr.upper() if s[0].isupper() else cyr

    return _OLD2CYR_RE.sub(repl, text)


# ─────────────────────────────────────────────
# ESKI LOTIN ↔ YANGI LOTIN
# ─────────────────────────────────────────────
_OLD2NEW_RE = re.compile(
    r"(?P<og>[OoGg]" + APOS + r")"
    r"|(?P<sc>[Ss][Hh]|[Cc][Hh])"
)
_OLD2NEW_MAP = {"sh": 'ş', "ch": 'ç', "o'": 'ö', "g'": 'ğ'}


def old_to_new(text: str) -> str:
    """
    Eski lotin → yangi lotin:  Sh→Ş, Ch→Ç, Oʻ→Ö, Gʻ→Ğ.
    Ng o'zgarishsiz qoladi (alohida harf sifatida chiqarilgan),
    tutuq belgisi (maʼno) saqlanadi.
    """
    text = unicodedata.normalize('NFC', text)
    n = len(text)

    def repl(m):
        s = m.group(0)
        key = s.lower()
        if m.lastgroup == 'og':
            key = key[0] + "'"
        new = _OLD2NEW_MAP[key]
        prev_ch = text[m.start() - 1] if m.start() > 0 else ''
        next_ch = text[m.end()] if m.end() < n else ''
        if s[0].isupper():
            # SH / CH — butun so'z katta bo'lsa ham bitta harf: Ş, Ç
            return new.upper()
        return new

    return _OLD2NEW_RE.sub(repl, text)


_NEW_OLD_MAP = {
    'ş': 'sh', 'ç': 'ch', 'ö': 'o' + OK_TURN, 'ğ': 'g' + OK_TURN,
}


def new_to_old(text: str) -> str:
    """Yangi lotin → eski lotin:  Ş→Sh, Ç→Ch, Ö→Oʻ, Ğ→Gʻ."""
    text = unicodedata.normalize('NFC', text)
    n = len(text)
    out = []
    for i, ch in enumerate(text):
        low = ch.lower()
        if low in _NEW_OLD_MAP:
            prev_ch = text[i - 1] if i > 0 else ''
            next_ch = text[i + 1] if i + 1 < n else ''
            out.append(_case(ch, _NEW_OLD_MAP[low], prev_ch, next_ch))
        else:
            out.append(ch)
    return ''.join(out)


# ─────────────────────────────────────────────
# KIRIL ↔ YANGI LOTIN (eski lotin orqali)
# ─────────────────────────────────────────────
def cyr_to_new(text: str) -> str:
    """Kiril → yangi lotin."""
    return old_to_new(cyr_to_old(text))


def new_to_cyr(text: str) -> str:
    """Yangi lotin → kiril."""
    return old_to_cyr(new_to_old(text))


if __name__ == "__main__":
    samples = [
        "Шаҳар, чой, Ўзбекистон, ғалаба, маъно, ёш, ишчи, Ер, поезд, ШАҲАР, ЎЗБЕК",
    ]
    for s in samples:
        old = cyr_to_old(s)
        new = cyr_to_new(s)
        print("Kiril      :", s)
        print("Eski lotin :", old)
        print("Yangi lotin:", new)
        print("Eski→Kiril :", old_to_cyr(old))
        print("Yangi→Kiril:", new_to_cyr(new))
        print("Yangi→Eski :", new_to_old(new))
