# mahacap.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from datetime import datetime

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Maharashtra CAP Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ---------------------------
# Admin Password
# ---------------------------
ADMIN_PASSWORD = "123"

# ---------------------------
# Data Files
# ---------------------------
DATA_FILE = "cities_data.csv"
CAP_DATA_FILE = "cap_raw_data.csv"

# ---------------------------
# Cities & Districts
# ---------------------------
cities_districts = {
    "Mumbai": "Mumbai",
    "Kalyan-Dombivli": "Thane",
    "Mira-Bhayandar": "Thane",
    "Navi Mumbai": "Thane",
    "Bhiwandi-Nizampur": "Thane",
    "Ulhasnagar": "Thane",
    "Ambernath Council": "Thane",
    "Vasai-Virar": "Palghar",
    "Thane": "Thane",
    "Badlapur Council": "Thane",
    "Pune": "Pune",
    "Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad",
    "Malegaon": "Nashik",
    "Nashik": "Nashik",
    "Nandurbar Council": "Nandurbar",
    "Bhusawal Council": "Jalgaon",
    "Jalgaon": "Jalgaon",
    "Dhule": "Dhule",
    "Ahilyanagar": "Ahilyanagar",
    "Chh. Sambhajinagar": "Chh. Sambhajianagar",
    "Jalna": "Jalna",
    "Beed Council": "Beed",
    "Satara Council": "Satara",
    "Sangli-Miraj-Kupwad": "Sangli",
    "Kolhapur": "Kolhapur",
    "Ichalkaranji": "Kolhapur",
    "Solapur": "Solapur",
    "Barshi Council": "Solapur",
    "Nanded-Waghala": "Nanded",
    "Yawatmal Council": "Yawatmal",
    "Dharashiv Council": "Dharashiv",
    "Latur": "Latur",
    "Udgir Council": "Latur",
    "Akola": "Akola",
    "Parbhani Council": "Parbhani",
    "Amravati": "Amravati",
    "Achalpur Council": "Amravati",
    "Wardha Council": "Wardha",
    "Hinganghat Council": "Wardha",
    "Nagpur": "Nagpur",
    "Chandrapur": "Chandrapur",
    "Gondia Council": "Gondia"
}

# ---------------------------
# Session State
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# ---------------------------
# Load Data
# ---------------------------
def load_csv(file_path, default_cols):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except:
            return pd.DataFrame(columns=default_cols)
    else:
        return pd.DataFrame(columns=default_cols)

meta_cols = [
    "City Name", "District", "Population", "ULB Category", "CAP Status",
    "GHG Emissions", "Environment Department Exist", "Department Name",
    "Head Name", "Department Email"
]
cap_cols = []

st.session_state.data = load_csv(DATA_FILE, meta_cols)
st.session_state.cap_data = load_csv(CAP_DATA_FILE, cap_cols)

# Remove Raigad Council (case-insensitive)
st.session_state.data = st.session_state.data[
    ~st.session_state.data["City Name"].str.contains("Raigad Council", case=False, na=False)
]
def reset_all_data():
    # Clear session state
    st.session_state.clear()
    
    # Optionally, reset CSV files
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    if os.path.exists(CAP_DATA_FILE):
        os.remove(CAP_DATA_FILE)
    
    st.success("All data has been reset successfully!")
    st.rerun()  # Refresh the app

# ---------------------------
# Helper Functions
# ---------------------------
def format_indian_number(num):
    try:
        num = int(num)
        s = str(num)[::-1]
        lst = []
        lst.append(s[:3])
        s = s[3:]
        while s:
            lst.append(s[:2])
            s = s[2:]
        return ','.join(lst)[::-1]
    except:
        return str(num)

def format_population(num):
    try:
        if pd.isna(num) or num == "":
            return "—"
        return format_indian_number(num)
    except:
        return str(num)

def safe_get(row, col, default="—"):
    try:
        val = row.get(col, default)
        return default if pd.isna(val) else val
    except:
        return default

# ---------------------------
# Dark / Professional SaaS CSS
# ---------------------------
st.markdown("""
<style>
/* ------------------- Main App ------------------- */
[data-testid="stAppViewContainer"] {
    background-color: #1E1E2F;  /* Deep dark background */
    color: #E6E6E6;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* ------------------- Sidebar ------------------- */
[data-testid="stSidebar"] {
    background-color: #2B2B3B; 
    color: #E6E6E6;
    padding-top: 20px;
    font-size: 18px;
    font-weight: 500;
}
[data-testid="stSidebar"] img {
    margin-bottom: 25px;
    border-radius: 6px;
}
[data-testid="stSidebar"] hr {
    border: 0.5px solid #3A3A4A;
    margin: 20px 0;
}
.sidebar-footer {
    color: #B0BEC5;
    font-size: 13px;
    text-align: center;
    margin-top: 30px;
}

/* ------------------- Buttons ------------------- */
.stButton>button {
    background-color: #3A8B34; /* Primary green */
    color: #FFFFFF; 
    border-radius: 8px; 
    height: 45px;
    font-size: 18px;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s ease-in-out;
}
.stButton>button:hover {
    background-color: #2E6B29;
}

/* Active/selected sidebar buttons */
.stButton>button[data-active="true"] {
    background-color: #42A5F5; 
    color: #FFFFFF;
}

/* ------------------- Metrics / Cards ------------------- */
[data-testid="stMetricValue"] {
    color: #54c750; 
    font-weight: 700;
    font-size: 26px;
}
.stCard {
    background-color: #2B2B3B;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 12px;
    transition: all 0.2s ease-in-out;
}
.stCard:hover {
    background-color: #353548;
}
.stCard h4 {
    margin: 0;
    font-weight: 500;
    color: #E6E6E6;
    font-size: 16px;
}
.stCard h2 {
    margin: 6px 0 0 0;
    font-weight: 700;
    color: #54c750;
    font-size: 28px;
}

/* ------------------- Inputs & Forms ------------------- */
input, textarea, select {
    background-color: #2B2B3B; 
    color: #E6E6E6; 
    border: 1px solid #54c750;
    border-radius: 6px;
    padding: 6px 10px;
}
.stExpander>div>div>div>div {
    background-color: #2B2B3B; 
    color: #E6E6E6;
}

/* ------------------- Tables ------------------- */
.stDataFrame, .stTable {
    color: #E6E6E6;
    background-color: #1E1E2F;
    border-radius: 8px;
}

/* ------------------- Links ------------------- */
a {
    color: #42A5F5;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}

/* ------------------- Headers ------------------- */
h2, h3, h4 {
    color: #CFD8DC;
    font-weight: 600;
}

/* ------------------- Scrollbar ------------------- */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #1E1E2F;
}
::-webkit-scrollbar-thumb {
    background-color: #42A5F5;
    border-radius: 6px;
}

/* ------------------- Dark theme consistency for charts ------------------- */
[data-testid="stPlotlyChart"] {
    background-color: #1E1E2F !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Admin Login
# ---------------------------
def admin_login():
    with st.form("login_form", clear_on_submit=False):
        pw = st.text_input("Enter Admin Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if pw == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Admin login successful")
                st.session_state.menu = "Home"
            else:
                st.error("Incorrect password")

# ---------------------------
# Sidebar
# ---------------------------
st.markdown("""
<style>
/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #1B1F23;
    color: #ECEFF1;
    padding-top: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Sidebar logo */
[data-testid="stSidebar"] img {
    margin-bottom: 25px;
    border-radius: 8px;
}

/* Sidebar buttons */
[data-testid="stSidebar"] button {
    background: linear-gradient(90deg, #2A2E33 0%, #2A2E33 100%);
    color: #ECEFF1;
    width: 100%;
    height: 55px;
    margin-bottom: 12px;
    border-radius: 6px;
    font-size: 20px;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease-in-out;
    text-align: left;
    padding-left: 25px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    position: relative;
    overflow: hidden;
}

/* Hover effect with subtle gradient */
[data-testid="stSidebar"] button:hover {
    background: linear-gradient(90deg, #3A3F46 0%, #2F343C 100%);
    transform: translateX(3px);
    cursor: pointer;
}

/* Active button sliding indicator */
[data-testid="stSidebar"] button[data-active="true"]::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 5px;
    height: 100%;
    background-color: #42A5F5;
    border-radius: 6px 0 0 6px;
    transition: all 0.3s ease-in-out;
}

/* Active button gradient */
[data-testid="stSidebar"] button[data-active="true"] {
    background: linear-gradient(90deg, #3A3F46 0%, #343A42 100%);
    color: #FFFFFF;
    font-weight: 700;
}

/* Separator lines */
[data-testid="stSidebar"] hr {
    border: 0.5px solid #546E7A;
    margin: 20px 0;
}

/* Sidebar footer */
.sidebar-footer {
    color: #B0BEC5;
    font-size: 13px;
    text-align: center;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar Logo
# ---------------------------
st.sidebar.image(
    "https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

# ---------------------------
# Sidebar Menu Buttons
# ---------------------------
menu_items = [("Home", "Home"), ("City Information", "City Information"), ("Admin", "Admin")]
if st.session_state.authenticated:
    menu_items.append(("Generate CAP", "Generate CAP"))

for label, page_name in menu_items:
    is_active = st.session_state.menu == page_name
    if st.sidebar.button(label, key=label):
        st.session_state.menu = page_name
        is_active = True
    st.markdown(f"""
    <script>
    const btn = window.parent.document.querySelector('button[key="{label}"]');
    if (btn) {{
        btn.setAttribute('data-active', {'true' if is_active else 'false'});
    }}
    </script>
    """, unsafe_allow_html=True)

# ---------------------------
# Sidebar Footer
# ---------------------------
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-footer'>EinTrust | © 2025</div>", unsafe_allow_html=True)

# ---------------------------
# Current Menu
# ---------------------------
menu = st.session_state.menu


# ---------------------------
# Home Page: Maharashtra Dashboard
# ---------------------------
if menu == "Home":
    st.header("Maharashtra's Net Zero Journey")
    st.markdown("Climate Action Plan Dashboard")

    # ✅ Always use the session_state data (keeps Admin updates live)
    if "data" not in st.session_state:
        st.session_state.data = pd.read_csv(DATA_FILE)
    df = st.session_state.data.copy()

    # ---------- Utility: Render Card ----------
    def render_card(col, label, value, is_input=False, bg_color="#34495E"):
        """
        Reusable card renderer for uniform styling.
        - is_input: True for inputted values (highlighted in white, bold, larger font).
        """
        if is_input:
            value_html = f"<b style='color:#FFFFFF;font-size:20px;'>{value}</b>"
        else:
            value_html = f"<span style='font-size:15px;color:#FFFFFF;'>{value}</span>"

        card_html = f"""
        <div style='
            background-color:{bg_color};
            color:#ECEFF1;
            padding:14px 10px;
            border-radius:12px;
            text-align:center;
            min-height:70px;
            margin-bottom:12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        '
        onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 10px rgba(0,0,0,0.5)';"
        onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.4)';"
        >
            {label}<br>{value_html}
        </div>
        """
        col.markdown(card_html, unsafe_allow_html=True)

    # ---------- Utility: Dark Layout for Charts ----------
    def dark_layout(fig, title=None):
        fig.update_layout(
            plot_bgcolor="#111111",
            paper_bgcolor="#111111",
            font=dict(color="white"),
            title=dict(text=title, font=dict(size=20, color="white")) if title else None,
            xaxis=dict(showgrid=False, color="white"),
            yaxis=dict(showgrid=False, color="white")
        )
        return fig

    # =====================
    # CAP Status Summary Cards with Gradient
    # =====================
    if not df.empty and "CAP Status" in df.columns:
        c1, c2, c3, c4 = st.columns(4)
        status_counts = {
            "Total Cities": len(df),
            "Not Started": df[df["CAP Status"].str.lower() == "not started"].shape[0],
            "In Progress": df[df["CAP Status"].str.lower() == "in progress"].shape[0],
            "Completed": df[df["CAP Status"].str.lower() == "completed"].shape[0]
        }

        card_colors = {
            "Total Cities": ["#4B8BF4", "#2C6BE0"],
            "Not Started": ["#FF6B6B", "#FF3B3B"],
            "In Progress": ["#FFA500", "#FF8C00"],
            "Completed": ["#28A745", "#1E7E34"]
        }

        for col, (title, val) in zip([c1, c2, c3, c4], status_counts.items()):
            color1, color2 = card_colors[title]
            col.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, {color1}, {color2});
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    color: white;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                ">
                    <h5>{title}</h5>
                    <h2>{format_indian_number(val)}</h2>
                </div>
                """, unsafe_allow_html=True
            )

    st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

    # =====================
    # Maharashtra Summary Metrics
    # =====================
    if "Maharashtra" in df["City Name"].values:
        maha_row = df[df["City Name"] == "Maharashtra"].iloc[0]
        population = maha_row.get("Population", 0)
        ghg_total = maha_row.get("GHG Emissions", 0)
        cap_status = maha_row.get("CAP Status", "—")
        cap_link = maha_row.get("CAP Link", "")
        vulnerability_score = maha_row.get("Vulnerability Score", 0)
        est_ghg = round(population * (ghg_total/population if population else 0), 2)

        st.subheader("Maharashtra Overview")

        # Row 1
        cols = st.columns(4)
        render_card(cols[0], "CAP Status", cap_status, is_input=True,
                    bg_color={"completed":"#28A745","in progress":"#FFA500","not started":"#FF3B3B"}.get(str(cap_status).lower(), "#34495E"))
        render_card(cols[1], "Link", f"<a href='{cap_link}' target='_blank' style='color:#ECEFF1;text-decoration:underline;'>View CAP</a>" if cap_link else "—")
        render_card(cols[2], "GHG Emissions (tCO2e)", format_indian_number(ghg_total), is_input=True)
        render_card(cols[3], "Estimated GHG by Population", format_indian_number(est_ghg), is_input=True)

        # Row 2
        cols = st.columns(2)
        render_card(cols[0], "Vulnerability Assessment Score", round(vulnerability_score,2), is_input=True)
        render_card(cols[1], "Population", format_indian_number(population), is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # =====================
        # Environmental Metrics
        # =====================
        st.subheader("Environmental Metrics")
        env_cols = ["Renewable Energy (MWh)", "Urban Green Area (ha)", "Municipal Solid Waste (tons)",
                    "Waste Landfilled (%)", "Waste Composted (%)", "Wastewater Treated (m3)"]
        for i in range(0, len(env_cols), 3):
            cols = st.columns(3)
            for col, name in zip(cols, env_cols[i:i+3]):
                val = maha_row.get(name, 0)
                display_val = f"{int(val)}%" if "%" in name else format_indian_number(val)
                render_card(col, name, display_val, is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # =====================
        # Social Metrics
        # =====================
        st.subheader("Social Metrics")
        males = maha_row.get("Males", 0)
        females = maha_row.get("Females", 0)
        total_pop = males + females
        children_m = maha_row.get("Children Male", 0)
        children_f = maha_row.get("Children Female", 0)
        total_children = children_m + children_f
        literacy_m = maha_row.get("Male Literacy (%)", 0)
        literacy_f = maha_row.get("Female Literacy (%)", 0)
        literacy_avg = round((literacy_m + literacy_f)/2, 2)

        social_metrics = [
            ("Male Population", format_indian_number(males)),
            ("Female Population", format_indian_number(females)),
            ("Total Population", format_indian_number(total_pop)),
            ("Children (0–6 Male)", format_indian_number(children_m)),
            ("Children (0–6 Female)", format_indian_number(children_f)),
            ("Total Children (0–6)", format_indian_number(total_children)),
            ("Male Literacy (%)", f"{literacy_m}%"),
            ("Female Literacy (%)", f"{literacy_f}%"),
            ("Average Literacy (%)", f"{literacy_avg}%"),
            ("Migrant Population (%)", f"{maha_row.get('Migrant (%)',0)}%"),
            ("Slum Population (%)", f"{maha_row.get('Slum (%)',0)}%"),
            ("BPL Households (%)", f"{maha_row.get('BPL Households (%)',0)}%"),
            ("Urbanization Rate (%)", f"{maha_row.get('Urbanization Rate (%)',0)}%")
        ]

        for i in range(0, len(social_metrics), 3):
            cols = st.columns(3)
            for col, (label, val) in zip(cols, social_metrics[i:i+3]):
                render_card(col, label, val, is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # =====================
        # Contact Information
        # =====================
        st.subheader("Contact Information")
        contacts = [
            ("Department Exist", maha_row.get("Department Exist","—")),
            ("Department Name", maha_row.get("Department Name","—")),
            ("Email", maha_row.get("Email","—")),
            ("Contact Number", maha_row.get("Contact Number","—")),
            ("Website", maha_row.get("Website","—"))
        ]
        for i in range(0, len(contacts), 2):
            cols = st.columns(2)
            for col, (label, val) in zip(cols, contacts[i:i+2]):
                render_card(col, label, val)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # =====================
        # Charts (Dark Mode)
        # =====================
        import plotly.express as px
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        df["Per Capita GHG"] = df.apply(lambda x: (x["GHG Emissions"]/x["Population"]) if x["Population"] else 0, axis=1)
        df["Estimated GHG"] = df["Population"] * df["Per Capita GHG"]

        # Chart 1
        fig_ghg = px.bar(df, x="City Name", y="GHG Emissions",
                         text=df["GHG Emissions"].apply(lambda x: format_indian_number(round(x,0))),
                         color="GHG Emissions", color_continuous_scale="Blues")
        fig_ghg.update_traces(marker_line_width=0, textposition="outside")
        st.plotly_chart(dark_layout(fig_ghg, "City-wise Total GHG Emissions"), use_container_width=True)

        # Chart 2
        fig_est = px.bar(df, x="City Name", y="Estimated GHG",
                         text=df["Estimated GHG"].apply(lambda x: format_indian_number(round(x,0))),
                         color="Estimated GHG", color_continuous_scale="Oranges")
        fig_est.update_traces(marker_line_width=0, textposition="outside")
        st.plotly_chart(dark_layout(fig_est, "Estimated GHG Emissions by Population"), use_container_width=True)

        # Chart 3
        evs_cols = ["GHG Emissions","Municipal Solid Waste (tons)","Wastewater Treated (m3)"]
        for c in evs_cols:
            if c not in df.columns: df[c] = 0
        max_env = {c: df[c].max() or 1 for c in evs_cols}
        df["EVS"] = (df["GHG Emissions"]/max_env["GHG Emissions"]*0.5 +
                     df["Municipal Solid Waste (tons)"]/max_env["Municipal Solid Waste (tons)"]*0.25 +
                     df["Wastewater Treated (m3)"]/max_env["Wastewater Treated (m3)"]*0.25) * 100
        social_factors = {"Population":0.3,"Households":0.2,"Urbanization Rate (%)":0.2,"Literacy Rate (%)":0.15,"Poverty Rate (%)":0.15}
        for c in social_factors:
            if c not in df.columns: df[c]=0
            else: df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        max_social = {c: df[c].max() or 1 for c in social_factors}
        df["SVS"] = ((df["Population"]/max_social["Population"])*0.3 +
                     (df["Households"]/max_social["Households"])*0.2 +
                     (df["Urbanization Rate (%)"]/max_social["Urbanization Rate (%)"])*0.2 +
                     (1 - df["Literacy Rate (%)"]/max_social["Literacy Rate (%)"])*0.15 +
                     (df["Poverty Rate (%)"]/max_social["Poverty Rate (%)"])*0.15) * 100
        vuln_df = df[["City Name","EVS","SVS"]].melt(id_vars="City Name", var_name="Score Type", value_name="Score")
        fig_vuln = px.bar(vuln_df, x="City Name", y="Score", color="Score Type", barmode="group",
                          text=vuln_df["Score"].apply(lambda x: f"{round(x,1)}"),
                          color_discrete_map={"EVS":"#1f77b4","SVS":"#ff7f0e"})
        fig_vuln.update_traces(textposition="outside")
        st.plotly_chart(dark_layout(fig_vuln, "City Vulnerability Scores (Environmental vs Social)"), use_container_width=True)

        
# ---------------------------
# City Information Page
# ---------------------------
elif menu == "City Information":
    st.markdown("<h2 style='margin-bottom:15px;'>City Information Dashboard</h2>", unsafe_allow_html=True)

    # Always pull latest saved data
    df_meta = st.session_state.get("data", pd.DataFrame()).copy()

    # Dropdown list should reflect available data
    available_cities = sorted(set(df_meta["City Name"])) if not df_meta.empty else list(cities_districts.keys())
    city = st.selectbox("Select City", available_cities)

    if not df_meta.empty and city in df_meta["City Name"].values:
        row = df_meta[df_meta["City Name"] == city].iloc[0].fillna("—")  # fallback for NaN
        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- Card Rendering ----------
        def render_card(col, label, value, is_input=False, bg_color="#34495E"):
            value_html = f"<b style='font-size:18px;'>{value}</b>" if is_input else f"<span style='font-size:15px;'>{value}</span>"
            card_html = f"""
            <div style='
                background-color:{bg_color};
                color:#ECEFF1;
                padding:14px 10px;
                border-radius:10px;
                font-size:15px;
                text-align:center;
                min-height:70px;
                margin-bottom:10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.4);
                transition: transform 0.2s, box-shadow 0.2s;
            ' onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 10px rgba(0,0,0,0.5)';"
              onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.4)';">
                {label}<br>{value_html}
            </div>
            """
            col.markdown(card_html, unsafe_allow_html=True)

        # ---------- BASIC INFORMATION ----------
        st.markdown("<h4>Basic Information</h4>", unsafe_allow_html=True)
        population = int(row.get("Population", 0) or 0)
        area = float(row.get("Area (sq.km)", row.get("Geographical Area (sq. km)", 0)) or 0)
        density = int(round(population / area)) if area > 0 else "—"

        est_year = row.get("Est. Year", "—")
        try:
            est_year = int(float(est_year)) if est_year not in ("—", "") else "—"
        except:
            pass

        cap_status = row.get("CAP Status", "—")
        cap_link = row.get("CAP Link", "")
        cap_colors = {"completed": "#66BB6A", "in progress": "#FFA726", "not started": "#EF5350"}
        cap_color = cap_colors.get(str(cap_status).lower(), "#34495E")

        basic_metrics = [
            ("District", row.get("District", "—")),
            ("ULB Category", row.get("ULB Category", "—")),
            ("Population", format_indian_number(population)),
            ("Area (sq.km)", format_indian_number(area)),
            ("Density (/sq.km)", format_indian_number(density) if density != "—" else "—"),
            ("Est. Year", est_year),
            ("CAP Status", cap_status),
        ]

        non_input_labels = {"District", "ULB Category"}
        for i in range(0, len(basic_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, basic_metrics[i:i+3]):
                bg = cap_color if label == "CAP Status" else "#34495E"
                render_card(col, label, value, is_input=(label not in non_input_labels), bg_color=bg)

        if cap_link:
            st.markdown(
                f"""
                <div style='background-color:#34495E; color:#ECEFF1; padding:12px;
                border-radius:10px; font-size:14px; text-align:center; margin-top:6px;
                box-shadow:0 4px 6px rgba(0,0,0,0.4);'>
                <a href='{cap_link}' target='_blank' style='color:#ECEFF1; text-decoration:underline;'>
                View CAP Document</a></div>
                """, unsafe_allow_html=True
            )

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- ENVIRONMENTAL INFORMATION ----------
        st.markdown("<h4>Environmental Information</h4>", unsafe_allow_html=True)
        ghg_total = float(row.get("GHG Emissions", 0) or 0)
        per_capita_ghg = int(round(ghg_total / population)) if population > 0 else 0

        env_metrics = [
            ("GHG Emissions (tCO2e)", format_indian_number(ghg_total)),
            ("Per Capita Emissions (tCO2e)", format_indian_number(per_capita_ghg)),
            ("Renewable Energy (MWh)", format_indian_number(row.get("Renewable Energy (MWh)", 0) or 0)),
            ("Urban Green Area (ha)", format_indian_number(row.get("Urban Green Area (ha)", 0) or 0)),
            ("Solid Waste (tons)", format_indian_number(row.get("Municipal Solid Waste (tons)", 0) or 0)),
            ("Wastewater Treated (m³)", format_indian_number(row.get("Wastewater Treated (m3)", 0) or 0)),
            ("Waste Landfilled (%)", f"{int(round(row.get('Waste Landfilled (%)',0)))}%"),
            ("Waste Composted (%)", f"{int(round(row.get('Waste Composted (%)',0)))}%"),
        ]
        for i in range(0, len(env_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, env_metrics[i:i+3]):
                render_card(col, label, value, is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- SOCIAL INFORMATION ----------
        st.markdown("<h4>Social Information</h4>", unsafe_allow_html=True)
        males = int(row.get("Males", 0) or 0)
        females = int(row.get("Females", 0) or 0)
        total_pop = males + females
        children_m = int(row.get("Children Male", 0) or 0)
        children_f = int(row.get("Children Female", 0) or 0)
        total_children = children_m + children_f
        literacy_m = float(row.get("Male Literacy (%)", 0) or 0)
        literacy_f = float(row.get("Female Literacy (%)", 0) or 0)
        literacy_total = int(round((literacy_m + literacy_f) / 2)) if (literacy_m or literacy_f) else 0

        social_metrics = [
            ("Male Population", format_indian_number(males)),
            ("Female Population", format_indian_number(females)),
            ("Total Population", format_indian_number(total_pop)),
            ("Children (0–6 Male)", format_indian_number(children_m)),
            ("Children (0–6 Female)", format_indian_number(children_f)),
            ("Total Children", format_indian_number(total_children)),
            ("Male Literacy (%)", f"{int(round(literacy_m))}%"),
            ("Female Literacy (%)", f"{int(round(literacy_f))}%"),
            ("Overall Literacy (%)", f"{int(round(literacy_total))}%"),
            ("Slum Population (%)", f"{int(round(row.get('Slum (%)',0)))}%"),
            ("Migrant Population (%)", f"{int(round(row.get('Migrant (%)',0)))}%"),
            ("BPL Households (%)", f"{int(round(row.get('BPL Households (%)',0)))}%"),
        ]
        for i in range(0, len(social_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, social_metrics[i:i+3]):
                render_card(col, label, value, is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- CONTACT INFORMATION ----------
        st.markdown("<h4>Contact Information</h4>", unsafe_allow_html=True)
        contact_metrics = [
            ("Department Exist", row.get("Department Exist","—")),
            ("Department Name", row.get("Department Name","—")),
            ("Email", row.get("Email","—")),
            ("Contact Number", row.get("Contact Number","—")),
            ("Website", row.get("Website","—")),
        ]
        for i in range(0, len(contact_metrics), 2):
            cols = st.columns(2)
            for col, (label, value) in zip(cols, contact_metrics[i:i+2]):
                render_card(col, label, value, is_input=False)

# ---------------------------
# Admin Panel Page
# ---------------------------
elif menu == "Admin":
    st.header("Admin Board")

    if not st.session_state.get("authenticated", False):
        admin_login()
    else:
        st.subheader("Update City / Maharashtra State Data")

        # ---------- Load existing data ----------
        df_meta = st.session_state.data.copy()

        # ---------- Helper function to get safe default ----------
        def safe_default(val, dtype):
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return dtype(0) if dtype in [int, float] else ''
            return dtype(val)

        # ---------- City selection ----------
        city = st.selectbox(
            "Select City",
            ["Maharashtra"] + list(cities_districts.keys()),
            key="selected_city"
        )

        # Get existing city data or empty dict
        existing_row = df_meta[df_meta["City Name"] == city]
        existing_data = existing_row.iloc[0].to_dict() if not existing_row.empty else {}

        # ---------- Admin Form ----------
        with st.form("admin_form", clear_on_submit=False):
            tabs = st.tabs(["Basic", "Environmental", "Social", "Contact"])

            # ---------- Basic Info ----------
            with tabs[0]:
                st.markdown("### Basic Information")
                population = st.number_input("Population (2011 Census)", min_value=0, step=1000, value=safe_default(existing_data.get("Population"), int))
                area = st.number_input("Geographical Area (sq. km)", min_value=0.0, step=0.1, value=safe_default(existing_data.get("Area (sq.km)"), float))
                ulb_category = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council", "Nagar Panchayat", "State"], index=["Municipal Corporation", "Municipal Council", "Nagar Panchayat", "State"].index(existing_data.get("ULB Category", "Municipal Corporation")))
                est_year = st.number_input("Year of Establishment of ULB", min_value=0, max_value=2100, step=1, value=safe_default(existing_data.get("Est. Year"), int))
                cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"], index=["Not Started", "In Progress", "Completed"].index(existing_data.get("CAP Status", "Not Started")))
                cap_link = st.text_input("CAP Link", value=safe_default(existing_data.get("CAP Link"), str))

            # ---------- Environmental Info ----------
            with tabs[1]:
                st.markdown("### Environmental Information")
                ghg_val = st.number_input("Total GHG Emissions (tCO2e)", min_value=0.0, step=100.0, value=safe_default(existing_data.get("GHG Emissions"), float))
                renewable_energy = st.number_input("Renewable Energy Generated (MWh/year)", min_value=0, step=10, value=safe_default(existing_data.get("Renewable Energy (MWh)"), int))
                green_area = st.number_input("Urban Green Area (ha)", min_value=0, step=1, value=safe_default(existing_data.get("Urban Green Area (ha)"), int))
                solid_waste = st.number_input("Municipal Solid Waste (tons/year)", min_value=0, step=10, value=safe_default(existing_data.get("Municipal Solid Waste (tons)"), int))
                waste_landfilled = st.number_input("Waste Landfilled (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Waste Landfilled (%)"), float))
                waste_composted = st.number_input("Waste Composted (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Waste Composted (%)"), float))
                wastewater = st.number_input("Wastewater Treated (m³/year)", min_value=0, step=1000, value=safe_default(existing_data.get("Wastewater Treated (m3)"), int))

            # ---------- Social Info ----------
            with tabs[2]:
                st.markdown("### Social Information")
                males = st.number_input("Male Population", min_value=0, step=100, value=safe_default(existing_data.get("Males"), int))
                females = st.number_input("Female Population", min_value=0, step=100, value=safe_default(existing_data.get("Females"), int))
                children_m = st.number_input("Children (0–6 Male)", min_value=0, step=10, value=safe_default(existing_data.get("Children Male"), int))
                children_f = st.number_input("Children (0–6 Female)", min_value=0, step=10, value=safe_default(existing_data.get("Children Female"), int))
                literacy = st.number_input("Overall Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Literacy (%)"), float))
                literacy_m = st.number_input("Male Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Male Literacy (%)"), float))
                literacy_f = st.number_input("Female Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Female Literacy (%)"), float))
                bpl = st.number_input("BPL Households (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("BPL Households (%)"), float))
                migrant = st.number_input("Migrant Population (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Migrant (%)"), float))
                slum = st.number_input("Slum Population (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Slum (%)"), float))
                urban_rate = st.number_input("Urbanization Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Urbanization Rate (%)"), float))
                households = st.number_input("Total Households", min_value=0, step=100, value=safe_default(existing_data.get("Households"), int))

            # ---------- Contact Info ----------
            with tabs[3]:
                st.markdown("### Contact Information")
                dept_exist = st.selectbox("Environment Department Exist?", ["Yes", "No"], index=["Yes", "No"].index(existing_data.get("Department Exist", "No")))
                dept_name = st.text_input("Department Name", value=safe_default(existing_data.get("Department Name"), str))
                dept_email = st.text_input("Department Email", value=safe_default(existing_data.get("Email"), str))
                contact_number = st.text_input("Contact Number", value=safe_default(existing_data.get("Contact Number"), str))
                official_website = st.text_input("Official Website", value=safe_default(existing_data.get("Website"), str))

            # ---------- Submit Button ----------
            submit_admin = st.form_submit_button("Save / Update")

            if submit_admin:
                import datetime
                new_row = {
                    "City Name": city,
                    "District": cities_districts.get(city, "Maharashtra") if city != "Maharashtra" else "State",
                    "Population": population,
                    "Area (sq.km)": area,
                    "ULB Category": ulb_category,
                    "CAP Status": cap_status,
                    "CAP Link": cap_link,
                    "Est. Year": est_year,
                    "GHG Emissions": ghg_val,
                    "Renewable Energy (MWh)": renewable_energy,
                    "Urban Green Area (ha)": green_area,
                    "Municipal Solid Waste (tons)": solid_waste,
                    "Waste Landfilled (%)": waste_landfilled,
                    "Waste Composted (%)": waste_composted,
                    "Wastewater Treated (m3)": wastewater,
                    "Males": males,
                    "Females": females,
                    "Children Male": children_m,
                    "Children Female": children_f,
                    "Literacy (%)": literacy,
                    "Male Literacy (%)": literacy_m,
                    "Female Literacy (%)": literacy_f,
                    "Migrant (%)": migrant,
                    "Slum (%)": slum,
                    "BPL Households (%)": bpl,
                    "Urbanization Rate (%)": urban_rate,
                    "Households": households,
                    "Department Exist": dept_exist,
                    "Department Name": dept_name,
                    "Email": dept_email,
                    "Contact Number": contact_number,
                    "Website": official_website,
                    "Last Updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                if not existing_data:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
                else:
                    df_meta.loc[df_meta["City Name"] == city, new_row.keys()] = pd.DataFrame([new_row]).values

                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE, index=False)
                st.success(f"{city} data updated successfully!")
                

# ---------------------------
# CAP Generation Page – Tab Style
# ---------------------------
import streamlit as st
import pandas as pd
import locale
from datetime import datetime

# ---------------------------
# Locale for Indian Number Format
# ---------------------------
try:
    locale.setlocale(locale.LC_ALL, 'en_IN')
except:
    pass

CAP_DATA_FILE = 'cap_detailed_data.csv'

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if st.session_state.get('authenticated'):
    st.header('CAP Generation: Comprehensive Data Collection')
    st.markdown('Provide detailed city-level data. More inputs = more accurate GHG inventory.')

    def indian_number(x):
        try:
            return locale.format_string('%d', int(x), grouping=True)
        except:
            return x

    def safe_val(val, dtype=int):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return dtype(0) if dtype in [int, float] else ''
        return dtype(val)

    with st.form('cap_generation_form', clear_on_submit=False):
        tabs = st.tabs([
            '1. Basic Info','2. Energy & Green Buildings','3. Green Cover & Biodiversity',
            '4. Sustainable Mobility','5. Water Resource Management','6. Waste Management',
            '7. Climate & Environmental Data','8. Vulnerability & Risk Assessment',
            '9. Disaster Mgmt & Risk Reduction','10. MRV','11. Climate Budget & Finance','12. Upload & Notes'
        ])

        # ---------------------------
        # Tab 1: Basic Info
        # ---------------------------
        with tabs[0]:
            st.subheader('City & Population')
            city = st.text_input('City Name')
            population_current = st.number_input('Current Population', min_value=0, step=1000, format='%d')
            population_2030 = st.number_input('Projected Population 2030', min_value=0, step=1000, format='%d')
            population_2050 = st.number_input('Projected Population 2050', min_value=0, step=1000, format='%d')

            st.subheader('Geography & Administrative')
            total_area_km2 = st.number_input('Total Area (km²)', min_value=0.0, step=0.1, format='%.2f')
            population_density = st.number_input('Population Density (per km²)', min_value=0.0, step=1.0, format='%.2f')
            num_wards = st.number_input('Number of Wards', min_value=0, step=1, format='%d')
            admin_boundary_file = st.file_uploader('Upload Ward shapefile/KML/GeoJSON', type=['zip','kml','geojson'])

            st.subheader('Environment / Climate Department')
            has_climate_cell = st.radio('Dedicated Environment/Climate/Disaster Mgmt Department?', ['No','Yes'])
            climate_cell_details = st.text_area('Staff list, roles, qualifications, budget')

            st.subheader('Policies & Plans')
            policies_list = ['Development Plan','Smart City Mission','AMRUT','SAPCC','City CAP','Other']
            policies_selected = st.multiselect('Select climate-relevant policies/plans', policies_list)
            policy_status = st.selectbox('Implementation Status', ['Not Started','In Progress','Completed'])

            st.subheader('Socio-economic Profile')
            perc_slum_population = st.number_input('Population in Slums (%)', min_value=0.0, max_value=100.0, step=0.1)
            avg_income = st.number_input('Average Income (₹)', min_value=0, step=1000, format='%d')
            literacy_rate = st.number_input('Literacy Rate (%)', min_value=0.0, max_value=100.0, step=0.1)

        # ---------------------------
        # Tab 2: Energy & Green Buildings
        # ---------------------------
        with tabs[1]:
            st.subheader('Electricity Consumption (MWh/year)')
            sectors = ['Residential','Commercial','Industrial','Municipal','Streetlighting']
            electricity_consumption = {s: st.number_input(f'{s} Electricity', min_value=0, step=10, format='%d') for s in sectors}

            st.subheader('Energy Mix (%)')
            energy_mix_grid = st.number_input('Grid (coal/gas)', min_value=0.0, max_value=100.0, step=0.1)
            energy_mix_renewables = st.number_input('Renewables (solar/wind/biomass)', min_value=0.0, max_value=100.0, step=0.1)
            energy_mix_captive = st.number_input('Captive generation', min_value=0.0, max_value=100.0, step=0.1)

            st.subheader('Installed Renewable Capacity (MW)')
            renewable_types = ['Rooftop Solar','Ground-mounted Solar','Wind','Biomass']
            renewable_capacity = {r: st.number_input(f'{r} Capacity', min_value=0.0, step=0.1) for r in renewable_types}

            st.subheader('Municipal Buildings & Streetlights')
            num_municipal_buildings = st.number_input('Number of Municipal Buildings', min_value=0, step=1)
            streetlight_led_percent = st.number_input('Streetlights retrofitted (%)', min_value=0.0, max_value=100.0, step=0.1)
            green_building_certifications = st.multiselect('Building Certifications', ['ECBC','IGBC','GRIHA','LEED','None'])

            st.subheader('Energy Efficiency Programs')
            programs_list = ['Audits','Retrofits','LED streetlights','Efficient Pumps']
            programs_active = st.multiselect('Active programs', programs_list)

        # ---------------------------
        # Tab 3: Green Cover & Biodiversity
        # ---------------------------
        with tabs[2]:
            st.subheader('Green Cover')
            total_green_area_ha = st.number_input('Total Green Cover Area (ha)', min_value=0, step=1)
            green_cover_percent = st.number_input('Green Cover (%)', min_value=0.0, max_value=100.0, step=0.1)
            num_parks = st.number_input('Number of Parks/Playgrounds/Gardens', min_value=0, step=1)
            parks_details_file = st.file_uploader('Upload Parks/Gardens Inventory', type=['csv','xlsx','pdf'])


            st.subheader('Water Bodies & Biodiversity')
            wetlands_rivers_lakes = st.text_area('List wetlands, rivers, lakes with ecological status & threats')
            tree_plantation_data = st.text_area('Tree plantation data: number, species, survival rate, maintenance')
            nbs_implemented = st.text_area('Nature-based solutions implemented/planned')


        # ---------------------------
        # Tab 4: Sustainable Mobility
        # ---------------------------
        with tabs[3]:
            st.subheader('Registered Vehicles')
            vehicle_types = ['2W','3W','4W','Buses','Trucks']
            fuel_types = ['Petrol','Diesel','CNG','EV']
            vehicles_data = {v: {f: st.number_input(f'{v} ({f})', min_value=0, step=1, format='%d') for f in fuel_types} for v in vehicle_types}


            st.subheader('Public Transport')
            daily_ridership = st.number_input('Daily Public Transport Ridership', min_value=0, step=1000, format='%d')
            public_transport_modes = st.multiselect('Public Transport Modes', ['Bus','Metro','Shared Mobility','Tram','BRT'])


            st.subheader('Non-Motorized Transport & EVs')
            footpaths_km = st.number_input('Footpath Length (km)', min_value=0.0, step=0.1)
            cycle_tracks_km = st.number_input('Cycle Tracks Length (km)', min_value=0.0, step=0.1)
            pedestrian_zones_km = st.number_input('Pedestrian Zones (km)', min_value=0.0, step=0.1)
            ev_adoption = st.number_input('EV Adoption (Number of EVs)', min_value=0, step=1, format='%d')
            ev_charging_stations = st.number_input('EV Charging Stations', min_value=0, step=1)
        
        # ---------------------------
        # Tab 5: Water Resource Management
        # ---------------------------
        with tabs[4]:
            st.subheader('Water Supply & Usage')
            sources = ['Surface Water','Groundwater','Bulk Purchase']
            water_supply_mld = {s: st.number_input(f'{s} Supply (MLD)', min_value=0, step=1) for s in sources}
            per_capita_supply = st.number_input('Per Capita Supply (LPCD)', min_value=0, step=1)
            nrw_percent = st.number_input('Non-Revenue Water (%)', min_value=0.0, max_value=100.0, step=0.1)
            leak_points_file = st.file_uploader('Upload Leak Points / Metering Coverage', type=['pdf','xlsx','csv'])

            st.subheader('Wastewater & Flood Management')
            wastewater_mld = st.number_input('Wastewater Generation (MLD)', min_value=0, step=1)
            stp_capacity_mld = st.number_input('STP Capacity (MLD)', min_value=0, step=1)
            percent_treated = st.number_input('% Wastewater Treated', min_value=0.0, max_value=100.0, step=0.1)
            percent_reused = st.number_input('% Reused', min_value=0.0, max_value=100.0, step=0.1)
            stormwater_maps = st.file_uploader('Upload Stormwater Maps / Flood Records', type=['pdf','xlsx','csv'])
            groundwater_data = st.text_area('Groundwater Levels, Over-extraction Areas, Recharge Initiatives')

        # ---------------------------
        # Tab 6: Waste Management
        # ---------------------------
        with tabs[5]:
            st.subheader('Solid Waste Management')
            msw_mt_day = st.number_input('Municipal Solid Waste (MT/day)', min_value=0, step=1)
            swm_composition = st.text_area('Composition (% Organic, Recyclable, Inert, Hazardous)')
            perc_household_segregation = st.number_input('Household Segregation (%)', min_value=0.0, max_value=100.0, step=0.1)
            treatment_facilities = st.text_area('Treatment Facilities: Composting, Biomethanation, Incineration, Recycling, Landfill')
            cdw_info = st.text_area('C&D Waste: Generation, Processing Capacity, % Recycled')
            biomedical_info = st.text_area('Biomedical/Hazardous Waste: Generation, Collection, Treatment, Compliance')

        # ---------------------------
        # Tab 7: Climate & Environmental Data
        # ---------------------------
        with tabs[6]:
            st.subheader('Historical Climate Data')
            temperature_data_file = st.file_uploader('Upload 30-year Temperature Data', type=['csv','xlsx','pdf'])
            rainfall_data_file = st.file_uploader('Upload 30-year Rainfall Data', type=['csv','xlsx','pdf'])
            extreme_events_file = st.file_uploader('Upload Historical Extreme Events (Floods/Droughts/Storms)', type=['csv','xlsx','pdf'])

            st.subheader('Air Quality & Heat Data')
            air_quality_file = st.file_uploader('Upload Air Quality Data (PM2.5, PM10, NOx, SOx, O3, CO)', type=['csv','xlsx','pdf'])
            uhi_data_file = st.file_uploader('Urban Heat Island Data (Maps/Heatwave Frequency)', type=['pdf','xlsx','csv'])

        # ---------------------------
        # Tab 8: Vulnerability & Risk Assessment
        # ---------------------------
        with tabs[7]:
            st.subheader('Exposure & Vulnerable Population')
            hazard_wards_file = st.file_uploader('Upload Wards Exposure Maps (Flood/Drought/Heat/Landslide)', type=['pdf','xlsx','geojson'])
            vulnerable_population_file = st.file_uploader('Upload Vulnerable Population Distribution (Slums, Elderly, Women, Migrants, Disabled)', type=['csv','xlsx','pdf'])

            st.subheader('Critical Infrastructure Vulnerability')
            critical_infra_file = st.file_uploader('Hospitals, Power Plants, Water Plants, Schools Vulnerability Data', type=['csv','xlsx','pdf'])
            backup_redundancy_info = st.text_area('Backup/Redundancy Details of Critical Infrastructure')

        # ---------------------------
        # Tab 9: Disaster Management & Risk Reduction
        # ---------------------------
        with tabs[8]:
            st.subheader('Disaster Plans & Early Warning')
            disaster_plan_file = st.file_uploader('Upload Disaster Management Plan & Hazard Maps', type=['pdf','xlsx','kml'])
            early_warning_systems = st.text_area('Early Warning Systems & Monitoring Details')

            st.subheader('Emergency Shelters & Response')
            emergency_shelters_file = st.file_uploader('Upload Shelter Capacity & Accessibility Data', type=['csv','xlsx','pdf'])
            emergency_response_info = st.text_area('Ambulances, Relief Stock, Evacuation Routes, Drills Conducted')

        # ---------------------------
        # Tab 10: Monitoring, Reporting & Verification (MRV)
        # ---------------------------
        with tabs[9]:
            st.subheader('GHG Inventory')
            baseline_year = st.number_input('Baseline Inventory Year', min_value=2000, max_value=datetime.now().year, step=1)
            methodology = st.text_area('Methodology & Emission Factors Used')
            sectoral_coverage = st.text_area('Sectoral Coverage')

            st.subheader('KPIs & MRV System')
            kpis = st.text_area('KPIs for Monitoring (Emissions, Energy Intensity, Green Cover, Climate Deaths, % Floodplain Population)')
            mrv_details = st.text_area('Responsible Agency, Data Frequency, Verification, Public Reporting Mechanisms')

        # ---------------------------
        # Tab 11: Climate Budget & Finance
        # ---------------------------
        with tabs[10]:
            st.subheader('Budget & Allocation')
            past_budget_file = st.file_uploader('Upload Past 3–5 Years Municipal Budgets', type=['csv','xlsx','pdf'])
            climate_allocation_percent = st.number_input('Climate Allocation (%)', min_value=0.0, max_value=100.0, step=0.1)

            st.subheader('CAP Implementation Costs & Funding')
            short_term_cost = st.number_input('Short-term Implementation Cost (₹)', min_value=0, step=1000, format='%d')
            medium_term_cost = st.number_input('Medium-term Implementation Cost (₹)', min_value=0, step=1000, format='%d')
            long_term_cost = st.number_input('Long-term Implementation Cost (₹)', min_value=0, step=1000, format='%d')

            funding_sources = st.multiselect('Funding Sources', ['Own Revenue','State/National Schemes','CSR','MDB Loans','GCF','Carbon Credits','Green Bonds','Other'])
            funding_gap_info = st.text_area('Funding Gap Analysis')
            climate_finance_mrv = st.text_area('MRV for Climate Finance (Tagging, Expenditure Tracking, Audits, Reporting)')
        # ---------------------------
        # Tab 12: Upload & Notes
        # ---------------------------
        with tabs[11]:
            st.markdown('### Attach Supporting Documents')
            supporting_file = st.file_uploader('Upload files (maps, reports, energy bills, surveys)', type=['pdf','xlsx','csv','zip','kml','geojson'])
            notes = st.text_area('Additional Notes / Clarifications', value='', height=120)

        # ---------------------------
        # Submit Button
        # ---------------------------
        submit_cap = st.form_submit_button('Submit CAP Data')

        if submit_cap:
            if not city or population_current <= 0:
                st.error('Please provide minimum required fields: City and Current Population.')
            else:
                raw_data = {
                    'City': city, 'Population_Current': population_current, 'Population_2030': population_2030, 'Population_2050': population_2050,
                    'Total_Area_km2': total_area_km2, 'Population_Density': population_density, 'Number_Wards': num_wards,
                    'Admin_Boundary_File': admin_boundary_file.name if admin_boundary_file else None,
                    'Has_Climate_Cell': has_climate_cell, 'Climate_Cell_Details': climate_cell_details,
                    'Policies_Selected': ','.join(policies_selected), 'Policy_Status': policy_status,
                    'Perc_Slum_Population': perc_slum_population, 'Avg_Income': avg_income, 'Literacy_Rate': literacy_rate,
                    'Electricity_Consumption': electricity_consumption, 'Energy_Mix_Grid': energy_mix_grid,
                    'Energy_Mix_Renewables': energy_mix_renewables, 'Energy_Mix_Captive': energy_mix_captive,
                    'Renewable_Capacity': renewable_capacity, 'Num_Municipal_Buildings': num_municipal_buildings,
                    'Streetlight_LED_%': streetlight_led_percent, 'Green_Building_Certifications': ','.join(green_building_certifications),
                    'Programs_Active': ','.join(programs_active), 'Supporting_File': supporting_file.name if supporting_file else None,
                    'Notes': notes, 'Submission_Date': datetime.now()
                }

                df_cap = st.session_state.get('cap_detailed', pd.DataFrame())
                if df_cap.empty:
                    df_cap = pd.DataFrame(columns=list(raw_data.keys()))
                df_cap = pd.concat([df_cap, pd.DataFrame([raw_data])], ignore_index=True)
                st.session_state.cap_detailed = df_cap

                try:
                    df_cap.to_csv(CAP_DATA_FILE, index=False)
                except Exception as e:
                    st.warning(f'Could not save CAP file: {e}')

                st.success(f'CAP data for {city} submitted successfully! Redirecting to GHG Inventory...')
                st.session_state.menu = 'GHG Inventory'
                st.rerun()

else:
    st.warning('Please log in as admin to access this page.')
