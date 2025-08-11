import streamlit as st
import random
import pandas as pd
import altair as alt

# Özel CSS
st.markdown("""
<style>
    .main { background-color: #f5f5f5; padding: 20px; }
    .stButton>button { background-color: #1f77b4; color: white; border-radius: 8px; }
    .stButton>button:hover { background-color: #ff7f0e; }
    .crisis-card { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .metric-positive { color: #2ecc71; font-weight: bold; }
    .metric-negative { color: #e74c3c; font-weight: bold; }
    .sidebar .stProgress .st-bo { background-color: #d3d3d3; }
    .sidebar .stProgress .st-bo div { background-color: #1f77b4; }
    h1 { color: #2c3e50; }
    .st-expander { background-color: #ecf0f1; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Streamlit session state başlat
if 'screen' not in st.session_state:
    st.session_state.screen = 'start_game'
    st.session_state.selected_scenario = None
    st.session_state.metrics = {
        'security': 40,
        'freedom': 70,
        'public_trust': 50,
        'resilience': 30,
        'fatigue': 10
    }
    st.session_state.decision = {
        'action': None,
        'scope': 'targeted',
        'duration': 'short',
        'safeguards': []
    }
    st.session_state.results = None
    st.session_state.budget = 100
    st.session_state.human_resources = 50
    st.session_state.crisis_history = []
    st.session_state.current_crisis_index = 0
    st.session_state.crisis_sequence = []

# Senaryolar tanımları
scenarios = {
    'pandemic': {
        'title': 'Pandemi Krizi',
        'icon': '🏥',
        'story': """
            **Durum Raporu: Acil**  
            Ada ülkesinde yeni bir varyant salgını patlak verdi. R(t) 1.5, hastaneler %80 dolu, yoğun bakım üniteleri sınırda.  
            Sosyal medyada "bitkisel tedavi mucizesi" gibi sahte öneriler viral, aşı karşıtlığı %30 arttı.  
            İletişim ağları tıkanık, panik stokçuluğu marketleri vurdu.  
            **Görev**: CIO olarak, bilgi akışını düzenleyin, yanlış bilgiyi kontrol edin ve halk sağlığını korurken özgürlükleri dengeleyin.
        """,
        'advisors': [
            {'name': 'Tuğgeneral Ayhan (Güvenlik)', 'text': 'Hız kritik! Genel karantina ve sosyal medya içerik kaldırma hemen uygulanmalı. Trol çiftlikleriyle sahte anlatıları bastırırız. **Risk**: Meşruiyet kaybı, ama kaosu önler.'},
            {'name': 'Av. Elif (Hukuk/Ombudsman)', 'text': 'Geniş kısıtlamalar mahremiyeti ve ifade özgürlüğünü çökertir. Hedefli izleme ve şeffaflık şart. **Risk**: Yavaş hareket, ama meşruiyet korur.'},
            {'name': 'Dr. Mert (Siyasi Danışman)', 'text': 'Halk panikte, şeffaf iletişim güven artırır. Prebunking ve fact-check kampanyalarıyla anlatıyı yönlendirin. **Risk**: Etki zaman alır.'},
            {'name': 'Zeynep, CTO (Teknik)', 'text': 'Decentralized izleme ve platformlarla MoU en verimli yol. Kendi acil platformumuzu devreye alalım, ama bağımsız yönetim şart. **Risk**: Teknik karmaşa.'}
        ],
        'action_cards': [
            {
                'id': 'A',
                'name': 'Merkezi İzleme + Geniş Kaldırma + Karantina',
                'cost': 50,
                'hr_cost': 20,
                'speed': 'fast',
                'security_effect': 40,
                'freedom_cost': 30,
                'side_effect_risk': 0.4,
                'safeguard_reduction': 0.5,
                'tooltip': 'Hızlı ama özgürlük maliyeti yüksek. Meşruiyet riski var.'
            },
            {
                'id': 'B',
                'name': 'Hedefli İzleme + Platform MoU + Yerel Kısıtlama',
                'cost': 30,
                'hr_cost': 15,
                'speed': 'medium',
                'security_effect': 30,
                'freedom_cost': 15,
                'side_effect_risk': 0.2,
                'safeguard_reduction': 0.7,
                'tooltip': 'Dengeli bir seçenek, güvencelerle daha etkili.'
            },
            {
                'id': 'C',
                'name': 'Prebunking + Okuryazarlık + Fact-Check + Uzman Paneli',
                'cost': 20,
                'hr_cost': 10,
                'speed': 'slow',
                'security_effect': 20,
                'freedom_cost': 5,
                'side_effect_risk': 0.1,
                'safeguard_reduction': 0.8,
                'tooltip': 'Yavaş ama sürdürülebilir, özgürlük dostu.'
            }
        ],
        'immediate_text': "Seçiminiz devreye girdi: {}. Hastane doluluğu %20 düştü, ancak bazı vatandaşlar 'gizli izleme' iddialarıyla sosyal medyada tepki gösterdi. Medya, kararınızı tartışıyor.",
        'delayed_text': """
            **Olay Günlüğü: Bir Hafta Sonra**  
            Yanlış bilgi yayılımı %40 azaldı, ancak bir yanlış kaldırma davası açıldı.  
            Uluslararası sağlık örgütleri kararınızı 'orantılı' buldu, ama halkın bir kısmı şeffaflık talep ediyor.  
            **Not**: Güvenceler, özgürlük kaybını azalttı mı? Uzun vadeli etkiler dayanıklılığı nasıl etkiler?
        """
    },
    'forest_fire': {
        'title': 'Orman Yangınları Krizi',
        'icon': '🔥',
        'story': """
            **Durum Raporu: Kritik**  
            Ada ülkesinin güneyindeki ormanlar alevler içinde, rüzgâr yönü değişiyor. Sahte tahliye haritaları sosyal medyada yayılıyor, iletişim ağları aşırı yükte.  
            Halk panikte, yanlış yönlendirmeler tahliyeyi zorlaştırıyor.  
            **Görev**: CIO olarak, acil iletişim kanallarını açın, yanlış bilgiyi durdurun ve can güvenliğini özgürlüklerle dengeleyin.
        """,
        'advisors': [
            {'name': 'Tuğgeneral Ayhan (Güvenlik)', 'text': 'Bölge genelinde sosyal medya kısıtlaması şart! Trol çiftlikleriyle doğru tahliye rotalarını duyururuz. **Risk**: Özgürlük kaybı, ama hayat kurtarır.'},
            {'name': 'Av. Elif (Hukuk/Ombudsman)', 'text': 'Geniş kısıtlamalar ifade özgürlüğünü zedeler. Hedefli iletişim ve şeffaflık raporu gerekir. **Risk**: Yavaş etki, ama meşruiyet korur.'},
            {'name': 'Dr. Mert (Siyasi Danışman)', 'text': 'Halkı sakin tutmak için medya okuryazarlığı kampanyası başlatın. Doğrulanmış haritalar güven artırır. **Risk**: Zaman alır.'},
            {'name': 'Zeynep, CTO (Teknik)', 'text': 'Cell-broadcast ve platformlarla MoU ile tahliye bilgisini hızlandırırız. **Risk**: Teknik koordinasyon zorluğu.'}
        ],
        'action_cards': [
            {
                'id': 'A',
                'name': 'Bölge Geniş Kısıtlama + Trol Karşı-Anlatı',
                'cost': 40,
                'hr_cost': 25,
                'speed': 'fast',
                'security_effect': 35,
                'freedom_cost': 25,
                'side_effect_risk': 0.35,
                'safeguard_reduction': 0.6,
                'tooltip': 'Hızlı ama ifade özgürlüğünü riske atar.'
            },
            {
                'id': 'B',
                'name': 'Cell-Broadcast + Zero-Rating Acil Siteler + Platform MoU',
                'cost': 25,
                'hr_cost': 15,
                'speed': 'medium',
                'security_effect': 30,
                'freedom_cost': 10,
                'side_effect_risk': 0.15,
                'safeguard_reduction': 0.75,
                'tooltip': 'Orta hızda, özgürlük dostu bir seçenek.'
            },
            {
                'id': 'C',
                'name': 'Bağımsız Medya Sahadan Canlı + Fact-Check Hızlı Şerit',
                'cost': 15,
                'hr_cost': 10,
                'speed': 'slow',
                'security_effect': 25,
                'freedom_cost': 5,
                'side_effect_risk': 0.1,
                'safeguard_reduction': 0.85,
                'tooltip': 'Yavaş, düşük riskli ve dayanıklılığı artırır.'
            }
        ],
        'immediate_text': "Seçiminiz devreye girdi: {}. Tahliye işlemleri hızlandı, ancak bazı bölgelerde internet kesintileri şikayetlere yol açtı. Yerel medya, kararınızı sorguluyor.",
        'delayed_text': """
            **Olay Günlüğü: Birkaç Gün Sonra**  
            Yangın kontrol altına alındı, sahte haritaların etkisi %50 azaldı.  
            Ancak, bazı vatandaşlar iletişim kısıtlamalarından şikayetçi. Uluslararası yardım ekipleri kararınızı 'etkili' buldu.  
            **Not**: Şeffaflık, halkın güvenini nasıl etkiledi? Dayanıklılık gelecek krizlerde ne kadar önemli?
        """
    },
    'earthquake': {
        'title': 'Deprem Krizi',
        'icon': '🌍',
        'story': """
            **Durum Raporu: Acil**  
            Ada ülkesinde 7.2 büyüklüğünde bir deprem vurdu. Baz istasyonlarının %40’ı devre dışı, “yağma” söylentileri sosyal medyada yayılıyor, yardım koordinasyonu aksıyor.  
            Halk korku içinde, yanlış bilgiler arama-kurtarma çalışmalarını zorlaştırıyor.  
            **Görev**: CIO olarak, iletişim ağlarını restore edin, yanlış bilgiyi kontrol edin ve can güvenliğini özgürlüklerle dengeleyin.
        """,
        'advisors': [
            {'name': 'Tuğgeneral Ayhan (Güvenlik)', 'text': 'Ülke çapı içerik yavaşlatma ve geniş gözetim hemen uygulanmalı! **Risk**: Özgürlük kaybı, ama kaosu önler.'},
            {'name': 'Av. Elif (Hukuk/Ombudsman)', 'text': 'Hedefli trafik önceliği ve şeffaflık raporu şart. Geniş gözetim mahremiyeti zedeler. **Risk**: Yavaş etki.'},
            {'name': 'Dr. Mert (Siyasi Danışman)', 'text': 'Halkın güvenini kazanmak için fact-check şeridi ve açık veri panosu kullanın. **Risk**: Organizasyon zaman alır.'},
            {'name': 'Zeynep, CTO (Teknik)', 'text': 'Cell-broadcast ve platformlarla MoU ile yardım koordinasyonunu hızlandırırız. **Risk**: Teknik altyapı sınırlı.'}
        ],
        'action_cards': [
            {
                'id': 'A',
                'name': 'Ülke Çapı İçerik Yavaşlatma + Geniş Gözetim',
                'cost': 45,
                'hr_cost': 30,
                'speed': 'fast',
                'security_effect': 45,
                'freedom_cost': 35,
                'side_effect_risk': 0.45,
                'safeguard_reduction': 0.5,
                'tooltip': 'Hızlı ama yüksek özgürlük maliyeti.'
            },
            {
                'id': 'B',
                'name': 'Hedefli Trafik Önceliği + Platform MoU + Doğrulanmış Yardım Noktaları',
                'cost': 35,
                'hr_cost': 20,
                'speed': 'medium',
                'security_effect': 35,
                'freedom_cost': 15,
                'side_effect_risk': 0.25,
                'safeguard_reduction': 0.7,
                'tooltip': 'Dengeli, güvencelerle daha etkili.'
            },
            {
                'id': 'C',
                'name': 'Bağımsız Medya Hasar Doğrulama + Açık Veri Panosu',
                'cost': 25,
                'hr_cost': 15,
                'speed': 'slow',
                'security_effect': 30,
                'freedom_cost': 10,
                'side_effect_risk': 0.15,
                'safeguard_reduction': 0.8,
                'tooltip': 'Yavaş ama özgürlük dostu ve dayanıklı.'
            }
        ],
        'immediate_text': "Seçiminiz devreye girdi: {}. Arama-kurtarma ekipleri koordinasyonu %30 iyileşti, ancak bazı kullanıcılar internet erişim sorunu bildirdi. Medya, kararınızı tartışıyor.",
        'delayed_text': """
            **Olay Günlüğü: Birkaç Gün Sonra**  
            Yağma söylentileri %60 azaldı, yardım dağıtımı verimli hale geldi.  
            Ancak, bazı vatandaşlar gözetimden rahatsız. Uluslararası kurtarma ekipleri kararınızı 'etkili' buldu.  
            **Not**: Güvenceler meşruiyeti nasıl etkiledi? Dayanıklılık gelecekte ne kadar kritik?
        """
    }
}

# Etki hesaplama fonksiyonu
def calculate_effects(action, scope, duration, safeguards, scenario):
    threat_severity = 80
    random_factor = random.uniform(0.1, 0.3)
    scope_multiplier = 0.7 if scope == 'targeted' else 1.3
    duration_multiplier = {'short': 0.5, 'medium': 1, 'long': 1.5}[duration]
    safeguard_count = len(safeguards)
    safeguard_quality = safeguard_count * 0.2

    new_budget = st.session_state.budget - action['cost']
    new_hr = st.session_state.human_resources - action['hr_cost']
    if new_budget < 0 or new_hr < 0:
        return None

    security_change = (threat_severity * action['security_effect'] / 100) - (action['side_effect_risk'] * random_factor * 20)
    freedom_cost = action['freedom_cost'] * scope_multiplier * duration_multiplier * (1 - safeguard_quality * action['safeguard_reduction'])
    public_trust_change = (10 if 'transparency' in safeguards else 0) - (freedom_cost * 0.5)
    resilience_change = action['security_effect'] * safeguard_quality / 2 if action['speed'] == 'slow' else 5
    fatigue_change = duration_multiplier * (5 if scope == 'targeted' else 10)

    return {
        'security': min(100, max(0, st.session_state.metrics['security'] + security_change)),
        'freedom': min(100, max(0, st.session_state.metrics['freedom'] - freedom_cost)),
        'public_trust': min(100, max(0, st.session_state.metrics['public_trust'] + public_trust_change)),
        'resilience': min(100, max(0, st.session_state.metrics['resilience'] + resilience_change)),
        'fatigue': min(100, max(0, st.session_state.metrics['fatigue'] + fatigue_change)),
        'counter_factual': 'B veya C ile aynı güvenliğe daha düşük özgürlük maliyetiyle ulaşabilirdiniz.' if action['id'] == 'A' else 'Bu, orantılı bir seçimdi; güvenceler fark yarattı.',
        'budget': new_budget,
        'human_resources': new_hr
    }

# Gösterge durum çubukları
def display_metrics():
    st.sidebar.subheader("Durum Panosu")
    metrics = [
        ('Bütçe', st.session_state.budget, 100, '#1f77b4'),
        ('İnsan Kaynağı', st.session_state.human_resources, 50, '#1f77b4'),
        ('Güvenlik', st.session_state.metrics['security'], 100, '#2ecc71' if st.session_state.metrics['security'] > 50 else '#e74c3c'),
        ('Özgürlük', st.session_state.metrics['freedom'], 100, '#2ecc71' if st.session_state.metrics['freedom'] > 50 else '#e74c3c'),
        ('Kamu Güveni', st.session_state.metrics['public_trust'], 100, '#2ecc71' if st.session_state.metrics['public_trust'] > 50 else '#e74c3c'),
        ('Dayanıklılık', st.session_state.metrics['resilience'], 100, '#2ecc71' if st.session_state.metrics['resilience'] > 50 else '#e74c3c'),
        ('Uyum Yorgunluğu', st.session_state.metrics['fatigue'], 100, '#e74c3c' if st.session_state.metrics['fatigue'] > 50 else '#2ecc71')
    ]
    for name, value, max_value, color in metrics:
        st.sidebar.markdown(f"**{name}: {value:.1f}/{max_value}**")
        st.sidebar.progress(min(max(value / max_value, 0), 1))

# Yardım ekranı
def display_help():
    with st.expander("Yardım: Oyun Rehberi"):
        st.markdown("""
            **Nasıl Oynanır?**  
            - **Amaç**: Krizleri yönetirken güvenlik ve özgürlük arasında denge kurun.  
            - **Metrikler**: Güvenlik, Özgürlük, Kamu Güveni, Dayanıklılık ve Uyum Yorgunluğu’nu izleyin.  
            - **Kararlar**: Aksiyonları seçin, kapsam/süre/güvenceleri ayarlayın.  
            - **Güvenceler**: Şeffaflık, itiraz mekanizması ve otomatik sona erdirme, özgürlük kaybını azaltır.  
            - **Riskler**: Geniş kapsam veya uzun süre, özgürlük ve meşruiyeti zedeler. Uyum yorgunluğu 50’yi aşarsa meşruiyet krizi riski artar.  
            **İpucu**: Hedefli ve güvenceli önlemler, uzun vadede daha sürdürülebilir!
        """)

# Oyun başlangıç ekranı
def start_game_screen():
    st.title("CIO Kriz Yönetimi Oyunu")
    with st.container():
        st.markdown("""
            <div class="crisis-card">
                <h2>Hoş Geldiniz!</h2>
                <p>Bu oyunda, rastgele gelen krizleri yöneteceksiniz. Her kriz, bir önceki kararlarınızın sonuçlarını miras alacak. Üç krizlik bir mücadele sizi bekliyor!</p>
            </div>
        """, unsafe_allow_html=True)
    if st.button("Oyunu Başlat"):
        crisis_keys = list(scenarios.keys())
        random.shuffle(crisis_keys)
        st.session_state.crisis_sequence = crisis_keys[:3]
        st.session_state.current_crisis_index = 0
        st.session_state.crisis_history = [st.session_state.metrics.copy()]
        st.session_state.selected_scenario = st.session_state.crisis_sequence[0]
        st.session_state.screen = 'story'
    display_help()

# Hikaye ekranı
def story_screen():
    scenario = scenarios[st.session_state.selected_scenario]
    st.title(f"{scenario['icon']} Kriz {st.session_state.current_crisis_index + 1}: {scenario['title']}")
    with st.container():
        st.markdown(f"""
            <div class="crisis-card">
                <h3>{scenario['title']}</h3>
                {scenario['story']}
            </div>
        """, unsafe_allow_html=True)
    st.info("**Rehber**: Kararlarınız can güvenliğini artırabilir, ancak özgürlükleri ve halkın güvenini etkileyebilir. Dengeyi bulmaya hazır mısınız?")
    display_metrics()
    if st.button("İlerle"):
        st.session_state.screen = 'advisors'
    display_help()

# Danışman ekranı
def advisors_screen():
    scenario = scenarios[st.session_state.selected_scenario]
    st.title("Danışman Görüşleri")
    with st.container():
        for advisor in scenario['advisors']:
            with st.expander(advisor['name']):
                st.markdown(advisor['text'])
    st.info("**Rehber**: Her danışmanın önerisi farklı bir strateji sunuyor. Önyargılarına dikkat edin ve uzun vadeli etkileri düşünün!")
    display_metrics()
    if st.button("Karar Ver"):
        st.session_state.screen = 'decision'
    display_help()

# Karar ekranı
def decision_screen():
    scenario = scenarios[st.session_state.selected_scenario]
    action_cards = scenario['action_cards']
    
    st.title("Karar Paneli")
    display_metrics()
    with st.container():
        st.markdown(f"""
            <div class="crisis-card">
                <h3>Kaynaklar</h3>
                <p><strong>Mevcut Bütçe</strong>: {st.session_state.budget}/100 | <strong>İnsan Kaynağı</strong>: {st.session_state.human_resources}/50</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.subheader("Aksiyon Seç")
    action_id = st.radio("Seçenek:", [card['id'] for card in action_cards], format_func=lambda x: f"{next(card['name'] for card in action_cards if card['id'] == x)} (Bütçe: {next(card['cost'] for card in action_cards if card['id'] == x)}, HR: {next(card['hr_cost'] for card in action_cards if card['id'] == x)}, {next(card['tooltip'] for card in action_cards if card['id'] == x)})")
    
    st.subheader("Kapsam")
    scope_display = st.selectbox("Seç:", ["Hedefli", "Genel"], key="scope")
    scope = 'targeted' if scope_display == "Hedefli" else 'general'
    
    st.subheader("Süre")
    duration_display = st.selectbox("Seç:", ["Kısa", "Orta", "Uzun"], key="duration")
    duration = {'Kısa': 'short', 'Orta': 'medium', 'Uzun': 'long'}[duration_display]
    
    st.subheader("Güvenceler")
    safeguards = []
    if st.checkbox("Şeffaflık Raporu (Kamu güvenini artırır, özgürlük kaybını azaltır)"): safeguards.append("transparency")
    if st.checkbox("İtiraz Mekanizması (Hatalı kararları düzeltme şansı sunar)"): safeguards.append("appeal")
    if st.checkbox("Otomatik Sona Erdirme (Normalleşme kaymasını önler)"): safeguards.append("sunset")
    
    if st.button("Uygula", disabled=not action_id):
        selected_action = next(card for card in action_cards if card['id'] == action_id)
        results = calculate_effects(selected_action, scope, duration, safeguards, st.session_state.selected_scenario)
        if results is None:
            st.error(f"Bütçe ({st.session_state.budget}/{selected_action['cost']}) veya insan kaynağı ({st.session_state.human_resources}/{selected_action['hr_cost']}) yetersiz! Daha düşük maliyetli bir aksiyon seçin.")
        else:
            st.session_state.decision = {
                'action': action_id,
                'scope': scope,
                'duration': duration,
                'safeguards': safeguards
            }
            st.session_state.results = results
            st.session_state.budget = results['budget']
            st.session_state.human_resources = results['human_resources']
            st.session_state.screen = 'immediate'
    display_help()

# Anında etki ekranı
def immediate_screen():
    scenario = scenarios[st.session_state.selected_scenario]
    action_name = next(card['name'] for card in scenario['action_cards'] if card['id'] == st.session_state.decision['action'])
    st.title("Anında Etki")
    with st.container():
        st.markdown(f"""
            <div class="crisis-card">
                <h3>Olay Günlüğü</h3>
                {scenario['immediate_text'].format(action_name)}
                <h4>Durum Güncellemesi</h4>
                <ul>
                    <li><strong>Güvenlik</strong>: <span class="{'metric-positive' if st.session_state.results['security'] > st.session_state.metrics['security'] else 'metric-negative'}">{st.session_state.results['security']:.1f}</span> – Krizin acil etkileri hafifledi.</li>
                    <li><strong>Özgürlük</strong>: <span class="{'metric-positive' if st.session_state.results['freedom'] > st.session_state.metrics['freedom'] else 'metric-negative'}">{st.session_state.results['freedom']:.1f}</span> – Kapsam ve süre özgürlükleri etkiledi.</li>
                    <li><strong>Kamu Güveni</strong>: <span class="{'metric-positive' if st.session_state.results['public_trust'] > st.session_state.metrics['public_trust'] else 'metric-negative'}">{st.session_state.results['public_trust']:.1f}</span> – Şeffaflık tepkileri şekillendirdi.</li>
                    <li><strong>Bütçe</strong>: {st.session_state.budget} – Harcamalar kaynakları sınırladı.</li>
                    <li><strong>İnsan Kaynağı</strong>: {st.session_state.human_resources} – Ekipler yoğun çalıştı.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    display_metrics()
    if st.button("Bir Hafta Sonra"):
        st.session_state.screen = 'delayed'
    display_help()

# Gecikmeli etki ekranı
def delayed_screen():
    scenario = scenarios[st.session_state.selected_scenario]
    delayed_results = {
        **st.session_state.results,
        'security': min(100, st.session_state.results['security'] + (10 if st.session_state.decision['action'] == 'C' else 5)),
        'resilience': min(100, st.session_state.results['resilience'] + (10 if st.session_state.decision['action'] == 'C' else 5)),
        'public_trust': min(100, st.session_state.results['public_trust'] - (3 if random.random() > 0.7 else 0))
    }
    st.session_state.results = delayed_results
    
    st.title("Gecikmeli Etkiler")
    with st.container():
        st.markdown(f"""
            <div class="crisis-card">
                <h3>Olay Günlüğü</h3>
                {scenario['delayed_text']}
                <h4>Uzun Vadeli Etkiler</h4>
                <ul>
                    <li><strong>Güvenlik</strong>: <span class="{'metric-positive' if delayed_results['security'] > st.session_state.results['security'] else 'metric-negative'}">{delayed_results['security']:.1f}</span> – Kriz kontrol altına alındı.</li>
                    <li><strong>Özgürlük</strong>: <span class="{'metric-positive' if delayed_results['freedom'] > st.session_state.results['freedom'] else 'metric-negative'}">{delayed_results['freedom']:.1f}</span> – Kısıtlamalar etkisini gösterdi.</li>
                    <li><strong>Kamu Güveni</strong>: <span class="{'metric-positive' if delayed_results['public_trust'] > st.session_state.results['public_trust'] else 'metric-negative'}">{delayed_results['public_trust']:.1f}</span> – Yanlış pozitifler güveni etkiledi.</li>
                    <li><strong>Dayanıklılık</strong>: <span class="{'metric-positive' if delayed_results['resilience'] > st.session_state.results['resilience'] else 'metric-negative'}">{delayed_results['resilience']:.1f}</span> – Eğitim gelecek krizlere hazırladı.</li>
                    <li><strong>Uyum Yorgunluğu</strong>: <span class="{'metric-positive' if delayed_results['fatigue'] < st.session_state.results['fatigue'] else 'metric-negative'}">{delayed_results['fatigue']:.1f}</span> – Uzun süreli önlemler tepkiyi zorlaştırabilir.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    st.info("**Rehber**: Dayanıklılık, gelecek krizlerde otomatik güvenlik artışı sağlar. Uyum yorgunluğu 50’yi aşarsa, meşruiyet krizi riski artar.")
    display_metrics()
    if st.button("Raporu Gör"):
        st.session_state.screen = 'report'
    display_help()

# Rapor ekranı
def report_screen():
    if not st.session_state.crisis_history or st.session_state.crisis_history[-1] != st.session_state.results:
        st.session_state.crisis_history.append(st.session_state.results.copy())

    st.title("Tur Sonu Raporu")
    with st.container():
        st.markdown(f"""
            <div class="crisis-card">
                <h3>Sonuç Tablosu</h3>
        """, unsafe_allow_html=True)
        df = pd.DataFrame([
            {'Gösterge': 'Güvenlik', 'Başlangıç': st.session_state.crisis_history[-2]['security'] if len(st.session_state.crisis_history) > 1 else 40, 'Son': st.session_state.results['security'], 'Neden': 'Seçilen aksiyonun kriz kontrol gücü ve yan etkiler.'},
            {'Gösterge': 'Özgürlük', 'Başlangıç': st.session_state.crisis_history[-2]['freedom'] if len(st.session_state.crisis_history) > 1 else 70, 'Son': st.session_state.results['freedom'], 'Neden': 'Kapsam, süre ve güvence eksikliği etkisi.'},
            {'Gösterge': 'Kamu Güveni', 'Başlangıç': st.session_state.crisis_history[-2]['public_trust'] if len(st.session_state.crisis_history) > 1 else 50, 'Son': st.session_state.results['public_trust'], 'Neden': 'Şeffaflık ve yanlış pozitiflerin etkisi.'},
            {'Gösterge': 'Dayanıklılık', 'Başlangıç': st.session_state.crisis_history[-2]['resilience'] if len(st.session_state.crisis_history) > 1 else 30, 'Son': st.session_state.results['resilience'], 'Neden': 'Eğitim ve uzun vadeli stratejiler.'},
            {'Gösterge': 'Uyum Yorgunluğu', 'Başlangıç': st.session_state.crisis_history[-2]['fatigue'] if len(st.session_state.crisis_history) > 1 else 10, 'Son': st.session_state.results['fatigue'], 'Neden': 'Uzun süreli veya geniş kapsamlı önlemler.'}
        ])
        st.table(df)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("Karşı-Olgu Analizi")
    with st.container():
        st.markdown(f"""
            <div class="crisis-card">
                <p>{st.session_state.results['counter_factual']}</p>
                <h4>Detaylı Analiz</h4>
                <ul>
                    <li><strong>Güvenlik</strong>: {st.session_state.results['security']:.1f} – Hızlı önlemler (A) kısa vadede etkili, ancak B veya C aynı sonucu daha az maliyetle sağlayabilirdi.</li>
                    <li><strong>Özgürlük</strong>: {st.session_state.results['freedom']:.1f} – Geniş kapsam veya uzun süre, ifade ve mahremiyeti etkiledi; güvenceler {len(st.session_state.decision['safeguards']) * 20}% kayıp kurtardı.</li>
                    <li><strong>Kamu Güveni</strong>: {st.session_state.results['public_trust']:.1f} – Şeffaflık eksikliği veya yan etkiler güveni sarstı mı?</li>
                    <li><strong>Dayanıklılık</strong>: {st.session_state.results['resilience']:.1f} – Yavaş ama sürdürülebilir yollar (C), gelecek krizlere hazırlığı artırdı.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    st.subheader("Gerçek Dünya Bağlantısı")
    with st.container():
        st.markdown("""
            <div class="crisis-card">
                <p>Kararlarınız, gerçek dünyada GDPR, BM İnsan Hakları İlkeleri veya OECD şeffaflık standartlarıyla nasıl ilişkilendirilir?</p>
                <ul>
                    <li><strong>Güvenceler</strong>: Şeffaflık raporları (ör. Google Transparency Report) halk güvenini artırır.</li>
                    <li><strong>Hedefli Önlemler</strong>: AB Veri Koruma Kuralları, orantılılık ilkesini vurgular.</li>
                    <li><strong>Normalleşme Kayması</strong>: Acil yetkilerin kalıcılaşması (ör. pandemi sonrası gözetim) özgürlükleri tehdit eder.</li>
                </ul>
                <p><strong>Öğrenme</strong>: Gerekli ve orantılı önlemler, hem güvenliği hem özgürlüğü korur.</p>
            </div>
        """, unsafe_allow_html=True)
    
    display_metrics()
    if st.button("Sonraki Krizi Başlat"):
        st.session_state.current_crisis_index += 1
        if st.session_state.current_crisis_index < len(st.session_state.crisis_sequence):
            st.session_state.selected_scenario = st.session_state.crisis_sequence[st.session_state.current_crisis_index]
            st.session_state.metrics = st.session_state.results.copy()
            st.session_state.screen = 'story'
        else:
            st.session_state.screen = 'game_end'
    display_help()

# Oyun sonu ekranı
def game_end_screen():
    if not st.session_state.crisis_history or st.session_state.crisis_history[-1] != st.session_state.results:
        st.session_state.crisis_history.append(st.session_state.results.copy())

    st.title("Oyun Sonu: Krizler Tarihi")
    with st.container():
        st.markdown("""
            <div class="crisis-card">
                <h3>Liderlik Performansınız</h3>
                <p>Tüm krizleri yönettiniz! Aşağıda, kararlarınızın zaman içindeki etkisini gösteren grafik ve liderlik skoru var.</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Liderlik skoru
    leadership_score = (st.session_state.results['security'] + st.session_state.results['freedom'] + st.session_state.results['public_trust']) / 3
    st.markdown(f"""
        <div class="crisis-card">
            <h4>Liderlik Skoru: {leadership_score:.1f}/100</h4>
            <p>{'Mükemmel! Güvenlik, özgürlük ve kamu güvenini dengede tuttunuz.' if leadership_score > 80 else 'İyi iş, ama bazı alanlarda daha az maliyetli yollar mümkündü.' if leadership_score > 60 else 'Zorlu bir yolculuktu. Daha fazla güvence ve hedefli önlem deneyin.'}</p>
        </div>
    """, unsafe_allow_html=True)

    # Line chart
    history_df = pd.DataFrame(st.session_state.crisis_history)
    history_df['Kriz'] = [f"Kriz {i+1}: {scenarios[st.session_state.crisis_sequence[i]]['title']}" if i < len(st.session_state.crisis_sequence) else "Başlangıç" for i in range(len(history_df))]
    history_df = history_df.melt(id_vars=['Kriz'], var_name='Gösterge', value_name='Değer')
    history_df = history_df[history_df['Gösterge'].isin(['security', 'freedom', 'public_trust', 'resilience', 'fatigue'])]
    history_df['Gösterge'] = history_df['Gösterge'].replace({
        'security': 'Güvenlik',
        'freedom': 'Özgürlük',
        'public_trust': 'Kamu Güveni',
        'resilience': 'Dayanıklılık',
        'fatigue': 'Uyum Yorgunluğu'
    })
    
    line_chart = alt.Chart(history_df).mark_line(point=True).encode(
        x=alt.X('Kriz:O', sort=None),
        y='Değer:Q',
        color='Gösterge:N',
        tooltip=['Kriz', 'Gösterge', 'Değer']
    ).properties(
        width=800,
        height=400,
        title='Krizler Boyunca Metrik Değişimleri'
    ).interactive()
    
    st.altair_chart(line_chart)
    
    display_metrics()
    if st.button("Yeni Oyun Başlat"):
        st.session_state.screen = 'start_game'
        st.session_state.crisis_history = []
        st.session_state.current_crisis_index = 0
        st.session_state.crisis_sequence = []
        st.session_state.metrics = {
            'security': 40,
            'freedom': 70,
            'public_trust': 50,
            'resilience': 30,
            'fatigue': 10
        }
        st.session_state.budget = 100
        st.session_state.human_resources = 50
    display_help()

# Ana uygulama akışı
display_metrics()
if st.session_state.screen == 'start_game':
    start_game_screen()
elif st.session_state.screen == 'story':
    story_screen()
elif st.session_state.screen == 'advisors':
    advisors_screen()
elif st.session_state.screen == 'decision':
    decision_screen()
elif st.session_state.screen == 'immediate':
    immediate_screen()
elif st.session_state.screen == 'delayed':
    delayed_screen()
elif st.session_state.screen == 'report':
    report_screen()
elif st.session_state.screen == 'game_end':
    game_end_screen()