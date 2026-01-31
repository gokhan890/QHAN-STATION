import streamlit as st
import pandas as pd
import random
import io

# ==========================================
# HANCA DİL MOTORU v5.3 (ÜNLÜ ÇAKIŞMASI FİNAL ÇÖZÜM)
# ==========================================
class HancaLanguageEngine:
    def __init__(self):
        # --- SES AYARLARI ---
        self.vowels_thick = ['A', 'I', 'O', 'U', 'Å']
        self.vowels_thin  = ['E', 'İ', 'Ö', 'Ü', 'Ä']
        self.common_hard = ['K', 'P', 'T', 'S', 'Ş', 'F', 'H', 'Ç']
        self.common_soft = ['R', 'L', 'M', 'N', 'V', 'Y', 'Z', 'B', 'D', 'G', 'J']
        self.rare_hard = ['Q', 'X', 'TS', 'PF']
        self.rare_soft = ['W', 'Ŋ', 'Γ', 'DZ', 'Ğ']
        self.all_vowels = self.vowels_thick + self.vowels_thin

        # --- MASTER SÖZLÜK (HATALAR TEMİZLENDİ) ---
        # Kural: Asla iki sesli yan yana gelmeyecek. (xuax -> xwax)
        self.master_dict = {
            # BEN
            "ben": "vo", "beni": "voq", "bana": "voqa", "bende": "vota", 
            "benden": "votar", "benim": "vom", "bence": "votse",
            # SEN
            "sen": "ze", "seni": "zeq", "sana": "zeqa", "sende": "zeta", 
            "senden": "zetar", "senin": "zen", "sence": "zetse",
            # O
            "o": "xu", "onu": "xuq", "ona": "xuqa", "onda": "xuta", 
            "ondan": "xutar", "onun": "xun", 
            "onlar": "xwax", # DÜZELTİLDİ: xuax -> xwax (u-a çakışması bitti)
            "onların": "xwaxon", # DÜZELTİLDİ: xuaxon -> xwaxon
            # BİZ
            "biz": "vox", "bizi": "voxuq", "bize": "voxqa", "bizde": "voxta", "bizim": "voxom",
            # SİZ
            "siz": "zex", "sizi": "zexuq", "size": "zexqa", "sizde": "zexta", "sizin": "zexen",
            # İŞARET & SORU
            "bu": "vu", "bunu": "vuq", "buna": "vuqa",
            "şu": "zu", "şunu": "zuq", "şuna": "zuqa",
            "ne": "qo", "neyi": "qoq", "neye": "qoqa", "niye": "qoqa"
        }

        # --- EK HARİTASI (UZUNLUK ÖNCELİKLİ) ---
        self.suffix_map = [
            # 1. Çoğul Şahıs İyelikleri
            ({'larımız', 'leriniz'}, {'thick': 'axvox', 'thin': 'exvex'}), 
            ({'larınız', 'leriniz'}, {'thick': 'axzox', 'thin': 'exzex'}),
            ({'ları', 'leri'}, {'thick': 'xax', 'thin': 'xex'}), 

            # 2. Tekil Şahıs İyelikleri
            ({'ımız', 'imiz', 'umuz', 'ümüz', 'mız', 'miz', 'muz', 'müz'}, {'thick': 'vox', 'thin': 'vex'}), 
            ({'ınız', 'iniz', 'unuz', 'ünüz', 'nız', 'niz', 'nuz', 'nüz'}, {'thick': 'zox', 'thin': 'zex'}), 
            ({'ım', 'im', 'um', 'üm', 'm'}, {'thick': 'om', 'thin': 'em'}),   
            ({'ın', 'in', 'un', 'ün', 'n'}, {'thick': 'on', 'thin': 'en'}),   
            
            # 3. İyelik (Onun)
            ({'sı', 'si', 'su', 'sü'}, {'thick': 'un', 'thin': 'ün'}),
            ({'ı', 'i', 'u', 'ü'}, {'thick': 'un', 'thin': 'ün'}), 

            # 4. Standart Çoğul
            ({'lar', 'ler'}, {'thick': 'ax', 'thin': 'ex'}),

            # 5. Hal Ekleri
            ({'dan', 'den', 'tan', 'ten'}, {'thick': 'tar', 'thin': 'ter'}), 
            ({'da', 'de', 'ta', 'te'}, {'thick': 'ta', 'thin': 'te'}),       
            ({'nın', 'nin', 'nun', 'nün'}, {'thick': 'yin', 'thin': 'yen'}), 
            ({'yı', 'yi', 'yu', 'yü'}, {'thick': 'uq', 'thin': 'üq'}),       
            ({'ya', 'ye', 'a', 'e'}, {'thick': 'qa', 'thin': 'qe'}),                     
            ({'ca', 'ce', 'ça', 'çe'}, {'thick': 'tse', 'thin': 'tsa'}),

            # 6. Fiil Ekleri
            ({'ma', 'me'}, {'thick': 'nix', 'thin': 'nex'}),
            ({'yor'}, {'thick': 'zo', 'thin': 'ze'}),           
            ({'acak', 'ecek'}, {'thick': 'var', 'thin': 'ver'}), 
            ({'mış', 'miş', 'muş', 'müş'}, {'thick': 'riv', 'thin': 'rev'}), 
            ({'dı', 'di', 'du', 'dü', 'tı', 'ti', 'tu', 'tü'}, {'thick': 'da', 'thin': 'de'}), 
            ({'ar', 'er', 'ır', 'ir', 'ur', 'ür', 'r'}, {'thick': 'gen', 'thin': 'gan'}), 

            ({'malı', 'meli'}, {'thick': 'laz', 'thin': 'lez'}), 
            ({'sa', 'se'}, {'thick': 'so', 'thin': 'se'}),       

            # 7. Yapım Ekleri
            ({'cı', 'ci', 'cu', 'cü', 'çı', 'çi'}, {'thick': 'or', 'thin': 'er'}), 
            ({'sız', 'siz', 'suz', 'süz'}, {'thick': 'non', 'thin': 'nen'}),       
            ({'lı', 'li', 'lu', 'lü'}, {'thick': 'lu', 'thin': 'lü'}),             
            ({'lık', 'lik', 'luk', 'lük'}, {'thick': 'sis', 'thin': 'sys'}),       
            ({'mak', 'mek'}, {'thick': 'mot', 'thin': 'met'}),                     

            # 8. Diğerleri
            ({'dır', 'dir', 'dur', 'dür', 'tır', 'tir'}, {'thick': 'dur', 'thin': 'dür'}),
            ({'mı', 'mi', 'mu', 'mü'}, {'thick': 'ku', 'thin': 'kü'})
        ]

    def normalize_input(self, text):
        return text.replace('I', 'ı').replace('İ', 'i').lower().strip()

    def is_vowel(self, char):
        return char in self.all_vowels

    def get_consonant(self, group_type):
        is_rare = random.random() < 0.10 
        if group_type == 'HARD':
            return random.choice(self.rare_hard if is_rare else self.common_hard)
        else:
            return random.choice(self.rare_soft if is_rare else self.common_soft)

    def generate_root_word(self, input_root):
        clean_root = self.normalize_input(input_root)
        if clean_root in self.master_dict:
            return self.master_dict[clean_root]

        random.seed(clean_root)
        base_len = len(input_root) + random.choice([-1, 0, 1])
        if base_len < 3: base_len = 3
        if base_len > 10: base_len = 10
        
        target_len = base_len
        harmony_mode = random.choice(['THICK', 'THIN'])
        active_vowels = self.vowels_thick if harmony_mode == 'THICK' else self.vowels_thin
        
        chars = []
        is_next_vowel = random.choice([True, False])
        
        if is_next_vowel:
            chars.append(random.choice(active_vowels))
            is_next_vowel = False
        else:
            chars.append(self.get_consonant(random.choice(['HARD', 'SOFT'])))
            is_next_vowel = True

        while len(chars) < target_len:
            last = chars[-1]
            if self.is_vowel(last):
                chars.append(self.get_consonant(random.choice(['HARD', 'SOFT'])))
            else:
                prev = chars[-2] if len(chars) > 1 else "A"
                if not self.is_vowel(prev) and random.random() < 0.95: 
                     chars.append(random.choice(active_vowels))
                elif random.random() < 0.85:
                    chars.append(random.choice(active_vowels))
                else:
                    source_type = 'SOFT' if last in (self.common_hard + self.rare_hard) else 'HARD'
                    chars.append(self.get_consonant(source_type))
        
        if len(chars) > 1:
             if not self.is_vowel(chars[-1]) and not self.is_vowel(chars[-2]):
                 chars.pop()
             elif self.is_vowel(chars[-1]) and self.is_vowel(chars[-2]): 
                 chars.pop()

        return "".join(chars).lower()

    def analyze_and_translate(self, word):
        word_clean = self.normalize_input(word)
        if not word_clean: return ""
        if word_clean in self.master_dict:
            return self.master_dict[word_clean]
        
        detected_suffixes = []
        current_stem = word_clean
        
        max_loop = 4 
        for _ in range(max_loop):
            match_found = False
            if current_stem in self.master_dict: break

            for tr_suffixes, hanca_suffixes in self.suffix_map:
                sorted_suffixes = sorted(list(tr_suffixes), key=len, reverse=True)
                
                for suffix in sorted_suffixes:
                    if current_stem.endswith(suffix):
                        potential_stem = current_stem[:-len(suffix)]
                        if len(potential_stem) < 2 and potential_stem not in self.master_dict:
                            continue
                        current_stem = potential_stem 
                        detected_suffixes.insert(0, hanca_suffixes)
                        match_found = True
                        break 
                if match_found: break
            if not match_found: break

        hanca_root = self.generate_root_word(current_stem)
        
        last_vowel_is_thick = True
        for char in reversed(hanca_root):
            if char.upper() in self.vowels_thick:
                last_vowel_is_thick = True
                break
            elif char.upper() in self.vowels_thin:
                last_vowel_is_thick = False
                break
        
        final_word = hanca_root
        for suffix_options in detected_suffixes:
            chosen_suffix = suffix_options['thick'] if last_vowel_is_thick else suffix_options['thin']
            
            # --- KRİTİK DÜZELTME: ÜNLÜ YUTMA (VOWEL DROP) ---
            # Kelime ünlüyle bitiyor VE Ek ünlüyle başlıyorsa -> Ekin ünlüsünü YUT.
            if self.is_vowel(final_word[-1].upper()) and self.is_vowel(chosen_suffix[0].upper()):
                # final: Zora, suffix: ax -> Zorax (a düşer)
                final_word += chosen_suffix[1:] 
            else:
                final_word += chosen_suffix

        return final_word

    def translate_sentence(self, text, is_proper=False):
        if not text: return ""
        if is_proper:
            return " ".join([w.upper() if len(w)<2 else w[0].upper()+w[1:-1].lower()+w[-1].upper() for w in text.split()])
        
        words = text.split()
        hanca_words = []
        for w in words:
            clean_w = ''.join(e for e in w if e.isalnum())
            punctuation = ''.join(e for e in w if not e.isalnum())
            
            if clean_w:
                translated = self.analyze_and_translate(clean_w)
                hanca_words.append(translated + punctuation)
            else:
                hanca_words.append(w)
        return " ".join(hanca_words)

# ==========================================
# ARAYÜZ
# ==========================================
st.set_page_config(page_title="QHAN GENERATOR v5.3", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .main {background-color: #0E1117;}
    h1 {color: #00FF00 !important; font-family: 'Courier New', monospace;}
    .stTextArea textarea {font-family: 'Courier New', monospace; font-size: 16px; color: #e6e6e6;}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ QHAN GROUP | Hanca Dil Motoru v5.3")
st.markdown("**Sürüm Notları:** SIFIR ÇİFT ÜNLÜ | Onlar -> Xwax | Akıllı Ünlü Yutma (Zora + ax -> Zorax)")
st.markdown("---")

engine = HancaLanguageEngine()

tab1, tab2 = st.tabs(["📝 Hızlı Çeviri (Manuel)", "📂 Toplu Çeviri (Excel/CSV)"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Girdi (Türkçe)")
        text_input = st.text_area("Metin Girişi:", height=350, placeholder="Onlar\nOnların\nArabalar\nEvim")
        
        if st.button("Çeviriyi Başlat", type="primary"):
            if text_input:
                lines = text_input.strip().split('\n')
                st.session_state['manual_results'] = [engine.translate_sentence(l.strip(), False) for l in lines if l.strip()]

    with col2:
        st.subheader("Çıktı (Hanca)")
        if 'manual_results' in st.session_state:
            result_text = "\n".join(st.session_state['manual_results'])
            st.text_area("Sonuçlar:", value=result_text, height=350)

with tab2:
    uploaded_file = st.file_uploader("Kelime Listesini Yükle", type=['xlsx', 'csv', 'txt'])
    
    if uploaded_file:
        if st.button("DOSYAYI İŞLE VE ÇEVİR"):
            with st.spinner('Çeviri yapılıyor...'):
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file, header=None)
                    elif uploaded_file.name.endswith('.xlsx'):
                        df = pd.read_excel(uploaded_file, header=None)
                    else:
                        df = pd.read_csv(uploaded_file, header=None, delimiter="\n")
                    
                    words = df[0].astype(str).tolist()
                    hanca_words = [engine.translate_sentence(w, False) for w in words]
                    
                    result_df = pd.DataFrame({'TURKCE': words, 'HANCA': hanca_words})
                    
                    st.success(f"✅ Tamamlandı. {len(words)} satır.")
                    st.dataframe(result_df.head(10))
                    
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        result_df.to_excel(writer, index=False)
                    
                    st.download_button(label="📥 İNDİR", data=buffer, file_name="HANCA_V5_3.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except Exception as e:
                    st.error(f"Hata: {e}")