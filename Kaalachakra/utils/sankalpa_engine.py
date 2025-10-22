# -*- coding: utf-8 -*-
# utils/sankalpa_engine.py

from datetime import datetime

# ---------- Transliteration helpers ----------
def dev_digits(s: str) -> str:
    """Convert Western digits in a string to Devanagari digits."""
    return str(s).translate(str.maketrans("0123456789", "०१२३४५६७८९"))

def weekday_iast(dt: datetime) -> str:
    """IAST-style weekday phrase like 'Ravi vāsare'."""
    names = [
        "Soma vāsare",
        "Maṅgala vāsare",
        "Budha vāsare",
        "Guru vāsare",
        "Śukra vāsare",
        "Śani vāsare",
        "Ravi vāsare",
    ]
    return names[dt.weekday()]

# ---------- Zodiac utils ----------
RASHI = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
]

def rashi_from_longitude(lon_deg: float) -> str:
    """Return rāśi name from sidereal longitude."""
    idx = int((lon_deg % 360) // 30)
    return RASHI[idx]

def ayana_from_sun_sign(sun_lon_deg: float) -> str:
    """Return Dakṣiṇāyane or Uttarāyane."""
    sign = int((sun_lon_deg % 360) // 30)
    return "Uttarāyane" if sign in [9, 10, 11, 0, 1, 2] else "Dakṣiṇāyane"

# ---------- Month → Ṛtu map ----------
RITU_BY_LUNAR_MONTH = {
    "Chaitra": "Vasanta ṛtau",
    "Vaishakha": "Vasanta ṛtau",
    "Jyeshtha": "Grīṣma ṛtau",
    "Ashadha": "Grīṣma ṛtau",
    "Shravana": "Varṣā ṛtau",
    "Bhadrapada": "Varṣā ṛtau",
    "Ashwin": "Śarad ṛtau",
    "Kartika": "Śarad ṛtau",
    "Margashirsha": "Hemanta ṛtau",
    "Pausha": "Hemanta ṛtau",
    "Magha": "Śiśira ṛtau",
    "Phalguna": "Śiśira ṛtau",
}

# ---------- Basic Sanskritization ----------
PURPOSE_MAP = {
    "obstacle": "vighna-nāśanārthe",
    "obstacles": "vighna-nāśanārthe",
    "peace": "śānty-artham",
    "health": "ārogya-siddhyartham",
    "prosper": "samṛddhyartham",
    "prosperity": "samṛddhyartham",
    "enemy": "śatru-nāśanārthe",
    "wealth": "dhana-lābhārtham",
    "bhairava": "Śrī Kālabhairava-prītyartham",
    "durga": "Śrī Durgā-prītyartham",
    "devi": "Śrī Devī-prītyartham",
    "shiva": "Śrī Śiva-prītyartham",
}

OFFERING_MAP = {
    "recitation": "pāṭhaṃ kariṣye",
    "chant": "japaṃ kariṣye",
    "havan": "havanam kariṣye",
    "homa": "homam kariṣye",
    "flowers": "puṣpāñjaliṃ samarpayāmi",
    "naivedya": "naivedyaṃ samarpayāmi",
    "lamp": "dīpam dīpayāmi",
}

def sanskritize_free(text: str, mapping: dict, default_suffix: str = "") -> str:
    if not text:
        return default_suffix.strip()
    low = text.lower()
    for k, v in mapping.items():
        if k in low:
            return v
    return (text.strip() + (" " + default_suffix if default_suffix else "")).strip()

# ---------- MAIN GENERATOR ----------
def generate_sankalpa(
    *,
    country: str,
    state: str,
    city: str,
    paksha_iast: str,
    tithi_iast: str,
    weekday_dt: datetime,
    nakshatra_iast: str,
    yoga_iast: str,
    karana_iast: str,
    lunar_month_iast: str,
    sun_lon_sidereal: float,
    moon_lon_sidereal: float,
    jupiter_lon_sidereal: float,
    name_iast: str,
    gotra_iast: str,
    purpose_free: str,
    offering_free: str,
    gender: str,
    when_dt: datetime
) -> str:
    """Return full Sankalpa text (IAST-style)."""

    vara_phrase = weekday_iast(weekday_dt)
    ayana = ayana_from_sun_sign(sun_lon_sidereal)
    ritu = RITU_BY_LUNAR_MONTH.get(lunar_month_iast, "— ṛtau")

    # Rāśis
    chandra_rashi = rashi_from_longitude(moon_lon_sidereal)
    surya_rashi = rashi_from_longitude(sun_lon_sidereal)
    deva_guru_rashi = rashi_from_longitude(jupiter_lon_sidereal)

    # Date/time
    date_str = dev_digits(when_dt.strftime("%d-%m-%Y"))
    time_str = dev_digits(when_dt.strftime("%I:%M %p"))

    # Gendered Sanskrit phrase
    gotra_phrase = "Gotrotpannasya" if gender.lower().startswith("m") else "Gotrotpannāyāḥ"

    # Sanskritize user intent
    purpose_san = sanskritize_free(purpose_free, PURPOSE_MAP, "hetōḥ")
    offering_san = sanskritize_free(offering_free, OFFERING_MAP)

    # Full Drik-style Sankalpa
    sankalpa_text = f"""ॐ विष्णुर्विष्णुर्विष्णुः
Shrimadbhagavato Mahapurushasya Vishnorājñayā pravartamānasya
Adyaitasya Brahmaṇo’ahni, Dvitīye Parārdhe,
Śrī Śvetavarāha Kalpe, Vaivasvata Manvantare,
Kaliyuge,
Kali Prathamacharane vartamāne,

Bhūrloke,
{country}, Kṣetre,
{state} Maṇḍalāntaragate,
{city} nāmnī nagare,

{ayana}, {ritu},
{lunar_month_iast} māse,
{paksha_iast} pakṣe,
{tithi_iast} tithau,
{vara_phrase},
{nakshatra_iast} nakṣatre,
{yoga_iast} yoge,
{karana_iast} karaṇe,
{chandra_rashi} rāśisthite Chandre,
{surya_rashi} rāśisthite Śrī Sūrye,
{deva_guru_rashi} rāśisthite Deva-gurau,

Śeṣeshu graheshu yathā-yathā rāśi-sthānastheshu satsu,
Evam graha-guṇa-viśeṣaṇa-viśiṣṭāyām śubha-puṇya-tithau,

Aham {gotra_iast} {gotra_phrase} {name_iast} nāma,
{purpose_san},
{offering_san}।

Iti Sankalpah."""
    return sankalpa_text