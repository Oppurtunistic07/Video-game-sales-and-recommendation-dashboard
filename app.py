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
st.markdown("Analyze video game sales and discover similar games with built-in recommendations.")

# ---------- Tabs ----------
tab1, tab2 = st.tabs(["📊 General Analytics", "🎮 Recommendation Engine"])

# ---------- TAB 1: General Analytics ----------
with tab1:
    # Search bar
    st.subheader("🔎 Search for a Game")
    search_input = st.text_input("Enter game name")
    if search_input:
        search_result = df[df['Name'].str.contains(search_input, case=False, na=False)]
        st.dataframe(search_result[['Name', 'Genre', 'Platform', 'Year', 'Global_Sales']].reset_index(drop=True))

    st.header("📊 General Analysis and Visualizations")

    # Sidebar Filters
    st.sidebar.header("📂 Filter Data")
    genre = st.sidebar.selectbox("Select Genre", sorted(df['Genre'].unique()))
    platform = st.sidebar.selectbox("Select Platform", sorted(df['Platform'].unique()))

    filtered = df[(df['Genre'] == genre) & (df['Platform'] == platform)]

    st.subheader(f"📈 Top 10 {genre} Games on {platform}")
    top_games = filtered.sort_values('Global_Sales', ascending=False).head(10)

    fig, ax = plt.subplots()
    sns.barplot(x='Global_Sales', y='Name', data=top_games, ax=ax, palette="viridis")
    ax.set_xlabel("Global Sales (in millions)")
    ax.set_ylabel("Game Name")
    st.pyplot(fig)

    # Correlation Heatmap
    st.subheader("🧠 Correlation Heatmap (Sales Features)")
    numeric_cols = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']
    corr = df[numeric_cols].corr()

    fig2, ax2 = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax2)
    st.pyplot(fig2)



    # Top 10 platforms



# ---------- TAB 2: Recommendation Engine ----------
with tab2:
    st.header("🎮 Game Recommendation Engine")

    # Game Selection
    st.subheader("Choose a game to get recommendations:")
    selected_game = st.selectbox("Game:", df['Name'].dropna().unique())


    # Recommendation Logic
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
    st.subheader("📌 Recommended Games:")
    st.dataframe(recommendations.reset_index(drop=True), use_container_width=True)

# ---------- Optional Footer ----------
st.markdown("---")
st.markdown(
    "📊 Built using [Streamlit](https://streamlit.io/) | Dataset: [Kaggle VG Sales](https://www.kaggle.com/datasets/gregorut/videogame-sales-with-ratings)")
