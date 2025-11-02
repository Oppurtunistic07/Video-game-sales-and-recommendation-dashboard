import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ---------- Load Dataset ----------
@st.cache_data
def load_data():
    url = "https://gist.githubusercontent.com/designernatan/27da044c6dc823f7ac7fe3a01f4513ed/raw/vgsales.csv"
    df = pd.read_csv(url)
    df.dropna(subset=['Year', 'Publisher'], inplace=True)
    df['Year'] = df['Year'].astype(int)
    return df

df = load_data()

# ---------- App Title ----------
st.title("🎮 Video Game Sales Dashboard")
st.markdown("Analyze video game sales with interactive visualizations and discover similar games.")

# ---------- Sidebar Filters ----------
st.sidebar.header("📂 Filter Data")
genre = st.sidebar.selectbox("Select Genre", ["All"] + sorted(df['Genre'].unique().tolist()))
platform = st.sidebar.selectbox("Select Platform", ["All"] + sorted(df['Platform'].unique().tolist()))
publisher = st.sidebar.selectbox("Select Publisher", ["All"] + sorted(df['Publisher'].unique().tolist()))
year_range = st.sidebar.slider("Select Year Range", int(df['Year'].min()), int(df['Year'].max()), (int(df['Year'].min()), int(df['Year'].max())))

# Apply filters
filtered_df = df[
    (df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])
]

if genre != "All":
    filtered_df = filtered_df[filtered_df['Genre'] == genre]
if platform != "All":
    filtered_df = filtered_df[filtered_df['Platform'] == platform]
if publisher != "All":
    filtered_df = filtered_df[filtered_df['Publisher'] == publisher]

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🏆 Publishers", "🎮 Recommendations"])

# ---------- Tab 1: Overview ----------
with tab1:
    st.subheader("Genre Popularity (Pie Chart)")
    genre_sales = filtered_df.groupby("Genre")["Global_Sales"].sum().reset_index()
    if not genre_sales.empty:
        fig, ax = plt.subplots()
        ax.pie(genre_sales["Global_Sales"], labels=genre_sales["Genre"], autopct='%1.1f%%')
        st.pyplot(fig)
    else:
        st.write("No data available for selected filters.")

    st.subheader("Platform Popularity (Bar Chart)")
    platform_sales = filtered_df.groupby("Platform")["Global_Sales"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=platform_sales.values, y=platform_sales.index, ax=ax, palette="viridis")
    ax.set_xlabel("Global Sales (in millions)")
    st.pyplot(fig)

# ---------- Tab 2: Trends ----------
with tab2:
    st.subheader("📈 Sales Trend Over Time")
    trend = filtered_df.groupby("Year")["Global_Sales"].sum().reset_index()
    if not trend.empty:
        fig, ax = plt.subplots()
        sns.lineplot(x="Year", y="Global_Sales", data=trend, marker="o", ax=ax)
        ax.set_ylabel("Global Sales (in millions)")
        st.pyplot(fig)
    else:
        st.write("No trend data available for selected filters.")

    st.subheader("📊 Regional Sales Correlation (Heatmap)")
    corr = df[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# ---------- Tab 3: Publishers ----------
with tab3:
    st.subheader("🏆 Top Publishers by Global Sales")
    publisher_sales = filtered_df.groupby("Publisher")["Global_Sales"].sum().sort_values(ascending=False).head(10)
    if not publisher_sales.empty:
        fig, ax = plt.subplots()
        sns.barplot(x=publisher_sales.values, y=publisher_sales.index, ax=ax, palette="mako")
        ax.set_xlabel("Global Sales (in millions)")
        st.pyplot(fig)
    else:
        st.write("No publisher data available for selected filters.")

# ---------- Tab 4: Recommendations ----------
with tab4:
    st.subheader("🎮 Game Recommendation Engine")

    top_games = filtered_df.sort_values('Global_Sales', ascending=False).head(20)
    if not top_games.empty:
        selected_game = st.selectbox("Choose a game to get recommendations:", top_games['Name'])

        # Original recommendation logic (same genre + platform, sorted by sales)
        def recommend_games(df, selected_game, top_n=5):
            try:
                selected_row = df[df['Name'] == selected_game].iloc[0]
                genre = selected_row['Genre']
                platform = selected_row['Platform']

                recs = df[
                    (df['Genre'] == genre) &
                    (df['Platform'] == platform) &
                    (df['Name'] != selected_game)
                ].sort_values("Global_Sales", ascending=False).head(top_n)

                return recs[['Name', 'Platform', 'Year', 'Global_Sales']]
            except:
                return pd.DataFrame(columns=["Name", "Platform", "Year", "Global_Sales"])

        recommendations = recommend_games(df, selected_game)
        st.dataframe(recommendations.reset_index(drop=True), use_container_width=True)
    else:
        st.write("Not enough games available in selected filters for recommendations.")

# ---------- Footer ----------
st.markdown("---")
st.markdown("📊 Built using **Streamlit** | Dataset: [Kaggle VG Sales](https://www.kaggle.com/datasets/gregorut/videogame-sales-with-ratings)")
