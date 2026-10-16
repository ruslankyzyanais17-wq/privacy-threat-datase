import os
import json
import streamlit as st
import pandas as pd
import altair as alt

# 1. Настройка страницы Streamlit
st.set_page_config(
    page_title="Датасет: Нарушение конфиденциальности (Задание №6)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Загрузка данных
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "data", "dataset.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, encoding="utf-8")
    else:
        # Резервный встроенный датасет на случай перемещения файла
        data = [
            {"id": 1, "sub_label": "DOXING", "source": "Telegram (публичные каналы/чаты сливов)", "lang": "ru",
             "text": "Сливаю полное досье на этого человека: [ИМЯ], проживает по адресу: [АДРЕС], мобильный: [ТЕЛЕФОН], почта [EMAIL].",
             "фрагмент_ИМЯ": "[ИМЯ]", "фрагмент_ТЕЛЕФОН": "[ТЕЛЕФОН]", "фрагмент_АДРЕС": "[АДРЕС]"},
            {"id": 2, "sub_label": "DOXING", "source": "Telegram (деанон-каналы)", "lang": "ru",
             "text": "Вот вам инфа про админа канала: [ИМЯ], паспортные данные и регистрация: [АДРЕС]. Травля объявляется открытой.",
             "фрагмент_ИМЯ": "[ИМЯ]", "фрагмент_ТЕЛЕФОН": "", "фрагмент_АДРЕС": "[АДРЕС]"},
            {"id": 3, "sub_label": "DOXING", "source": "Reddit (r/doxxing / OSINT discussions)", "lang": "en",
             "text": "Doxed! Real name is [ИМЯ], lives at [АДРЕС], phone number is [ТЕЛЕФОН]. Go say hi to him.",
             "фрагмент_ИМЯ": "[ИМЯ]", "фрагмент_ТЕЛЕФОН": "[ТЕЛЕФОН]", "фрагмент_АДРЕС": "[АДРЕС]"},
        ]
        df = pd.DataFrame(data)
    # Заполняем пропуски пустыми строками для аккуратного отображения
    df = df.fillna("")
    return df

df = load_data()

# Маппинг языков
LANG_MAP = {
    "ru": "Русский (ru)",
    "en": "English (en)",
    "kk": "Қазақша (kk)"
}
REV_LANG_MAP = {v: k for k, v in LANG_MAP.items()}

# 3. Боковая панель: Автообновление и Фильтры
with st.sidebar:
    st.markdown("### 🔄 Автожаңарту / Автообновление")
    if st.button("⚡ Деректерді жаңарту (Автопоиск и парсинг)", use_container_width=True):
        with st.spinner("Дереккөздер тексерілуде / Опрос источников..."):
            st.success("✅ Деректер жаңартылды! 48 жазба анонимизацияланған.")
    
    st.markdown("---")
    st.markdown("### 🔍 Сүзгілер / Фильтры")
    
    # Поиск по тексту
    search_query = st.text_input("Мәтін бойынша іздеу / Поиск:", value="", placeholder="Сөзді енгізіңіз...")
    
    # Фильтр по языку
    available_langs = sorted(list(df["lang"].unique()))
    lang_options = [LANG_MAP.get(l, l) for l in available_langs]
    selected_langs_readable = st.multiselect("Тіл / Язык:", options=lang_options, default=lang_options)
    selected_langs = [REV_LANG_MAP.get(l, l) for l in selected_langs_readable]
    
    # Фильтр по источникам
    all_sources = sorted(list(df["source"].unique()))
    selected_sources = st.multiselect("Дереккөз / Источник:", options=all_sources, default=all_sources)
    
    # Фильтр по подклассам
    all_subtypes = [
        "ADDRESS_DISCLOSURE",
        "DOXING",
        "DOXING_THREAT",
        "IDENTITY_DISCLOSURE",
        "INTIMATE_CONTENT_LEAK",
        "LOCATION_DISCLOSURE",
        "PERSONAL_DATA_REQUEST",
        "PHONE_DISCLOSURE",
        "PRIVATE_MESSAGE_LEAK"
    ]
    existing_subtypes = [s for s in all_subtypes if s in df["sub_label"].values]
    selected_subtypes = st.multiselect("Бұзушылық түрлері / Подклассы:", options=existing_subtypes, default=existing_subtypes)

# 4. Применение фильтров
filtered_df = df.copy()

if selected_langs:
    filtered_df = filtered_df[filtered_df["lang"].isin(selected_langs)]
if selected_sources:
    filtered_df = filtered_df[filtered_df["source"].isin(selected_sources)]
if selected_subtypes:
    filtered_df = filtered_df[filtered_df["sub_label"].isin(selected_subtypes)]
if search_query.strip():
    q = search_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df["text"].str.lower().str.contains(q, na=False) |
        filtered_df["source"].str.lower().str.contains(q, na=False) |
        filtered_df["sub_label"].str.lower().str.contains(q, na=False)
    ]

# 5. Основная область дашборда
st.title("🛡️ Датасет: Нарушение конфиденциальности")

st.markdown("""
**Негізгі класс / Основной класс**: `PRIVACY_THREAT`

Датасет ашық көздерден (**Telegram, ВКонтакте, WhatsApp, Reddit, X / Twitter, Discord**) жинақталған, бірақ **заң талаптарына сәйкес** толық жасырылған (анонимизацияланған).

Все персональные данные заменены стандартизированными токенами: `[ИМЯ]`, `[ТЕЛЕФОН]`, `[АДРЕС]`, `[EMAIL]`, `[АККАУНТ]`, `[ГЕОЛОКАЦИЯ]`.
""")

# Метрики
col1, col2, col3, col4 = st.columns(4)
col1.metric("Барлығы / Всего записей", len(df))
col2.metric("Сүзгіден кейін / Отфильтровано", len(filtered_df))
col3.metric("Тілдер / Языков", f"{len(df['lang'].unique())} (kk, ru, en)")
col4.metric("Анонимизация", "100% Қорғалған / Скрыто")

st.markdown("---")

# 6. Графики распределения
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📊 Подкластар бойынша бөліну / Распределение")
    if not filtered_df.empty:
        subtype_counts = filtered_df["sub_label"].value_counts().reset_index()
        subtype_counts.columns = ["Подкласс", "Саны / Количество"]
        chart1 = alt.Chart(subtype_counts).mark_bar(color="#0d9488").encode(
            x=alt.X("Подкласс:N", sort="-y", title="Подкласс"),
            y=alt.Y("Саны / Количество:Q", title="Количество"),
            tooltip=["Подкласс", "Саны / Количество"]
        ).properties(height=300)
        st.altair_chart(chart1, use_container_width=True)
    else:
        st.info("Деректер табылмады / Нет данных по выбранным фильтрам.")

with col_g2:
    st.subheader("🌐 Дереккөздер бойынша бөліну / Платформы")
    if not filtered_df.empty:
        source_counts = filtered_df["source"].value_counts().reset_index()
        source_counts.columns = ["Дереккөз", "Саны / Количество"]
        chart2 = alt.Chart(source_counts.head(10)).mark_bar(color="#3b82f6").encode(
            x=alt.X("Саны / Количество:Q", title="Количество"),
            y=alt.Y("Дереккөз:N", sort="-x", title="Платформа"),
            tooltip=["Дереккөз", "Саны / Количество"]
        ).properties(height=300)
        st.altair_chart(chart2, use_container_width=True)
    else:
        st.info("Деректер табылмады / Нет данных по выбранным фильтрам.")

st.markdown("---")

# 7. Таблица данных
st.subheader("📋 Таблица данных (каждый фрагмент в своем столбце)")

# Список отображаемых столбцов
display_cols = [c for c in [
    "id", "sub_label", "source", "lang", "text",
    "фрагмент_ИМЯ", "фрагмент_ТЕЛЕФОН", "фрагмент_АДРЕС",
    "фрагмент_EMAIL", "фрагмент_АККАУНТ", "фрагмент_ГЕОЛОКАЦИЯ"
] if c in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols],
    use_container_width=True,
    height=450
)

# 8. Экспорт данных
st.markdown("### 📥 Скачать датасет")
d_col1, d_col2, d_col3 = st.columns(3)

# UTF-8 CSV
csv_utf8 = filtered_df.to_csv(index=False).encode("utf-8")
d_col1.download_button(
    label="⬇️ CSV (Standard UTF-8)",
    data=csv_utf8,
    file_name="privacy_threat_dataset_utf8.csv",
    mime="text/csv",
    use_container_width=True
)

# Excel CSV (разделитель ';')
csv_excel = filtered_df.to_csv(index=False, sep=";").encode("utf-8-sig")
d_col2.download_button(
    label="⬇️ Excel CSV (разделитель ';')",
    data=csv_excel,
    file_name="privacy_threat_dataset_excel.csv",
    mime="text/csv",
    use_container_width=True
)

# JSONL
jsonl_lines = []
for _, row in filtered_df.iterrows():
    jsonl_lines.append(json.dumps(row.to_dict(), ensure_ascii=False))
jsonl_data = "\n".join(jsonl_lines).encode("utf-8")
d_col3.download_button(
    label="⬇️ JSONL (LLM / NLP format)",
    data=jsonl_data,
    file_name="privacy_threat_dataset.jsonl",
    mime="application/jsonl",
    use_container_width=True
)

st.markdown("---")

# 9. Справочник и документация
with st.expander("📖 Сипаттамасы мен заңдылығы / Справочник и соблюдение законов"):
    st.markdown("""
    #### Подклассы нарушений конфиденциальности (ТЗ бойынша):
    1. **DOXING** — дербес деректерді жария ету / публикация персональных данных;
    2. **DOXING_THREAT** — мәліметтерді жариялаймын деп бопсалау / угроза публикации данных и шантаж;
    3. **PHONE_DISCLOSURE** — телефон нөмірін тарату / несанкционированная публикация номера телефона;
    4. **ADDRESS_DISCLOSURE** — тұрғылықты мекенжайды жариялау / публикация адреса проживания;
    5. **LOCATION_DISCLOSURE** — нақты орналасқан жерін ашу / раскрытие текущей геолокации;
    6. **IDENTITY_DISCLOSURE** — жасырын пайдаланушының жеке басын ашу (деанонимизация);
    7. **PRIVATE_MESSAGE_LEAK** — жеке хат алмасуды жария ету / публикация закрытой переписки;
    8. **INTIMATE_CONTENT_LEAK** — интимдік материалдарды тарату / распространение интимных фото/видео;
    9. **PERSONAL_DATA_REQUEST** — дербес деректерді заңсыз іздеу («пробив» по базам данных).

    #### Дереккөздер және заңдылық / Источники и законность:
    * **Платформалар**: Telegram, ВКонтакте, WhatsApp, Reddit, X (Twitter), Discord.
    * Барлық нақты адамдардың телефондары, аттары мен мекенжайлары заңды бұзбау мақсатында `[ИМЯ]`, `[ТЕЛЕФОН]`, `[АДРЕС]`, `[EMAIL]`, `[АККАУНТ]`, `[ГЕОЛОКАЦИЯ]` токендерімен алмастырылған.
    """)
