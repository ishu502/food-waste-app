import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Food Waste Management", page_icon="🍽️", layout="wide")

# =========================
# Data Loading
# =========================
@st.cache_data
def load_data():
    providers = pd.read_csv("providers_data.csv")        # Provider_ID,Name,Type,Address,City,Contact
    receivers = pd.read_csv("receivers_data.csv")        # Receiver_ID,Name,Type,City,Contact
    food_listings = pd.read_csv("food_listings_data.csv")# Food_ID,Food_Name,Quantity,Expiry_Date,Provider_ID,Provider_Type,Location,Food_Type,Meal_Type
    claims = pd.read_csv("claims_data.csv")              # Claim_ID,Food_ID,Receiver_ID,Status,Timestamp

    # Normalize/parse dates that exist
    if "Expiry_Date" in food_listings.columns:
        food_listings["Expiry_Date"] = pd.to_datetime(food_listings["Expiry_Date"], errors="coerce")
    if "Timestamp" in claims.columns:
        claims["Timestamp"] = pd.to_datetime(claims["Timestamp"], errors="coerce")

    # Coerce numerics where helpful
    if "Quantity" in food_listings.columns:
        food_listings["Quantity"] = pd.to_numeric(food_listings["Quantity"], errors="coerce")

    return providers, receivers, food_listings, claims


providers, receivers, food_listings, claims = load_data()

# =========================
# Helpers
# =========================
def vc_df(series, name_col="value", count_col="count"):
    """value_counts to tidy DataFrame with predictable column names."""
    out = series.value_counts(dropna=False).reset_index(name=count_col)
    out.rename(columns={"index": name_col}, inplace=True)
    return out

def safe_selectbox(label, options, default="All"):
    opts = ["All"] + sorted([o for o in options if pd.notna(o)])
    return st.selectbox(label, opts, index=opts.index(default) if default in opts else 0)

# =========================
# Overview
# =========================
def page_overview(providers, receivers, food_listings, claims):
    st.title("🌍 Food Waste Management Dashboard — Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏢 Providers", len(providers) if not providers.empty else 0)
    c2.metric("🤝 Receivers", len(receivers) if not receivers.empty else 0)
    c3.metric("🍱 Food Listings", len(food_listings) if not food_listings.empty else 0)
    c4.metric("📦 Claims", len(claims) if not claims.empty else 0)

    st.divider()

    colL, colR = st.columns(2)

    # Providers & Receivers per City
    with colL:
        st.subheader("🏙️ Providers & Receivers by City")
        prov_city = vc_df(providers["City"], "City", "Providers") if "City" in providers.columns else pd.DataFrame()
        recv_city = vc_df(receivers["City"], "City", "Receivers") if "City" in receivers.columns else pd.DataFrame()
        if not prov_city.empty or not recv_city.empty:
            merged_city = prov_city.merge(recv_city, on="City", how="outer").fillna(0)
            fig = px.bar(merged_city.melt(id_vars="City", var_name="Category", value_name="Count"),
                         x="City", y="Count", color="Category", barmode="group",
                         title="Providers & Receivers by City")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("City data not available in providers/receivers.")

    # Claims over Time
    with colR:
        st.subheader("⏳ Claims Over Time")
        if "Timestamp" in claims.columns and not claims["Timestamp"].isna().all():
            fig = px.histogram(claims, x="Timestamp", nbins=30, title="Claims Over Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Timestamp column in claims or all values are missing.")

    st.divider()

    # Top Food Types by Quantity
    st.subheader("🍽️ Top Food Types by Total Quantity")
    if {"Food_Type", "Quantity"}.issubset(food_listings.columns):
        qty_by_type = food_listings.groupby("Food_Type", dropna=False)["Quantity"].sum().reset_index()
        qty_by_type = qty_by_type.sort_values("Quantity", ascending=False)
        fig = px.bar(qty_by_type, x="Food_Type", y="Quantity", title="Total Quantity by Food Type")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Food_Type and/or Quantity not available in food listings.")

# =========================
# Providers
# =========================
def page_providers(df):
    st.title("🏢 Providers")

    with st.expander("🔎 Filters", expanded=True):
        type_sel = st.multiselect("Filter by Provider Type",
                                  options=sorted(df["Type"].dropna().unique()) if "Type" in df.columns else [],
                                  default=sorted(df["Type"].dropna().unique()) if "Type" in df.columns else [])
        city_sel = st.multiselect("Filter by City",
                                  options=sorted(df["City"].dropna().unique()) if "City" in df.columns else [],
                                  default=sorted(df["City"].dropna().unique()) if "City" in df.columns else [])
        name_search = st.text_input("Search by name (contains)")

    f = df.copy()
    if "Type" in f.columns and type_sel:
        f = f[f["Type"].isin(type_sel)]
    if "City" in f.columns and city_sel:
        f = f[f["City"].isin(city_sel)]
    if "Name" in f.columns and name_search:
        f = f[f["Name"].str.contains(name_search, case=False, na=False)]

    st.dataframe(f, use_container_width=True, height=380)

    st.subheader("📊 Insights")
    g1, g2 = st.columns(2)
    with g1:
        if "Type" in f.columns and not f.empty:
            tdf = vc_df(f["Type"], "Type", "count")
            fig = px.bar(tdf, x="Type", y="count", title="Providers by Type")
            st.plotly_chart(fig, use_container_width=True)
    with g2:
        if "City" in f.columns and not f.empty:
            cdf = vc_df(f["City"], "City", "count")
            fig = px.bar(cdf, x="City", y="count", title="Providers by City")
            st.plotly_chart(fig, use_container_width=True)

# =========================
# Receivers
# =========================
def page_receivers(df):
    st.title("🤝 Receivers")

    with st.expander("🔎 Filters", expanded=True):
        type_sel = st.multiselect("Filter by Receiver Type",
                                  options=sorted(df["Type"].dropna().unique()) if "Type" in df.columns else [],
                                  default=sorted(df["Type"].dropna().unique()) if "Type" in df.columns else [])
        city_sel = st.multiselect("Filter by City",
                                  options=sorted(df["City"].dropna().unique()) if "City" in df.columns else [],
                                  default=sorted(df["City"].dropna().unique()) if "City" in df.columns else [])
        name_search = st.text_input("Search by name (contains)")

    f = df.copy()
    if "Type" in f.columns and type_sel:
        f = f[f["Type"].isin(type_sel)]
    if "City" in f.columns and city_sel:
        f = f[f["City"].isin(city_sel)]
    if "Name" in f.columns and name_search:
        f = f[f["Name"].str.contains(name_search, case=False, na=False)]

    st.dataframe(f, use_container_width=True, height=380)

    st.subheader("📊 Insights")
    g1, g2 = st.columns(2)
    with g1:
        if "Type" in f.columns and not f.empty:
            tdf = vc_df(f["Type"], "Type", "count")
            fig = px.pie(tdf, names="Type", values="count", title="Receiver Type Distribution")
            st.plotly_chart(fig, use_container_width=True)
    with g2:
        if "City" in f.columns and not f.empty:
            cdf = vc_df(f["City"], "City", "count")
            fig = px.bar(cdf, x="City", y="count", title="Receivers by City")
            st.plotly_chart(fig, use_container_width=True)

# =========================
# Food Listings
# =========================
def page_food_listings(df):
    st.title("🍱 Food Listings")

    with st.expander("🔎 Filters", expanded=True):
        prov_type = st.multiselect("Provider Type",
                                   options=sorted(df["Provider_Type"].dropna().unique()) if "Provider_Type" in df.columns else [],
                                   default=sorted(df["Provider_Type"].dropna().unique()) if "Provider_Type" in df.columns else [])
        location = st.multiselect("Location",
                                  options=sorted(df["Location"].dropna().unique()) if "Location" in df.columns else [],
                                  default=sorted(df["Location"].dropna().unique()) if "Location" in df.columns else [])
        food_type = st.multiselect("Food Type",
                                   options=sorted(df["Food_Type"].dropna().unique()) if "Food_Type" in df.columns else [],
                                   default=sorted(df["Food_Type"].dropna().unique()) if "Food_Type" in df.columns else [])
        meal_type = st.multiselect("Meal Type",
                                   options=sorted(df["Meal_Type"].dropna().unique()) if "Meal_Type" in df.columns else [],
                                   default=sorted(df["Meal_Type"].dropna().unique()) if "Meal_Type" in df.columns else [])
        name_search = st.text_input("Search Food Name (contains)")

        # Date range on Expiry_Date
        date_range = None
        if "Expiry_Date" in df.columns and not df["Expiry_Date"].isna().all():
            min_d = pd.to_datetime(df["Expiry_Date"], errors="coerce").min()
            max_d = pd.to_datetime(df["Expiry_Date"], errors="coerce").max()
            if pd.notna(min_d) and pd.notna(max_d):
                date_range = st.date_input("Expiry Date Range", [min_d.date(), max_d.date()])

    f = df.copy()
    if prov_type and "Provider_Type" in f.columns:
        f = f[f["Provider_Type"].isin(prov_type)]
    if location and "Location" in f.columns:
        f = f[f["Location"].isin(location)]
    if food_type and "Food_Type" in f.columns:
        f = f[f["Food_Type"].isin(food_type)]
    if meal_type and "Meal_Type" in f.columns:
        f = f[f["Meal_Type"].isin(meal_type)]
    if name_search and "Food_Name" in f.columns:
        f = f[f["Food_Name"].str.contains(name_search, case=False, na=False)]
    if date_range and len(date_range) == 2 and "Expiry_Date" in f.columns:
        f = f[(f["Expiry_Date"] >= pd.to_datetime(date_range[0])) &
              (f["Expiry_Date"] <= pd.to_datetime(date_range[1]))]

    st.dataframe(f, use_container_width=True, height=380)

    st.subheader("📊 Insights")
    g1, g2 = st.columns(2)
    with g1:
        if "Food_Type" in f.columns and not f.empty:
            tdf = vc_df(f["Food_Type"], "Food_Type", "count")
            fig = px.bar(tdf, x="Food_Type", y="count", title="Listings by Food Type")
            st.plotly_chart(fig, use_container_width=True)
    with g2:
        if "Expiry_Date" in f.columns and not f["Expiry_Date"].isna().all():
            fig = px.histogram(f, x="Expiry_Date", title="Expiry Date Distribution", nbins=30)
            st.plotly_chart(fig, use_container_width=True)

    if {"Food_Type", "Quantity"}.issubset(f.columns) and not f.empty:
        st.subheader("📦 Total Quantity by Food Type")
        qdf = f.groupby("Food_Type", dropna=False)["Quantity"].sum().reset_index()
        qdf = qdf.sort_values("Quantity", ascending=False)
        fig = px.bar(qdf, x="Food_Type", y="Quantity", title="Total Quantity by Food Type")
        st.plotly_chart(fig, use_container_width=True)

# =========================
# Claims
# =========================
def page_claims(claims, food_listings, receivers):
    st.title("📦 Claims")

    with st.expander("🔎 Filters", expanded=True):
        status_sel = st.multiselect("Status",
                                    options=sorted(claims["Status"].dropna().unique()) if "Status" in claims.columns else [],
                                    default=sorted(claims["Status"].dropna().unique()) if "Status" in claims.columns else [])

        date_range = None
        if "Timestamp" in claims.columns and not claims["Timestamp"].isna().all():
            min_d = claims["Timestamp"].min()
            max_d = claims["Timestamp"].max()
            if pd.notna(min_d) and pd.notna(max_d):
                date_range = st.date_input("Timestamp Range", [min_d.date(), max_d.date()])

    f = claims.copy()
    if status_sel and "Status" in f.columns:
        f = f[f["Status"].isin(status_sel)]
    if date_range and len(date_range) == 2 and "Timestamp" in f.columns:
        f = f[(f["Timestamp"] >= pd.to_datetime(date_range[0])) &
              (f["Timestamp"] <= pd.to_datetime(date_range[1]))]

    st.dataframe(f, use_container_width=True, height=380)

    st.subheader("📊 Insights")
    g1, g2 = st.columns(2)

    with g1:
        if "Timestamp" in f.columns and not f["Timestamp"].isna().all():
            fig = px.histogram(f, x="Timestamp", title="Claims Over Time", nbins=30)
            st.plotly_chart(fig, use_container_width=True)
        elif "Status" in f.columns:
            sdf = vc_df(f["Status"], "Status", "count")
            fig = px.pie(sdf, names="Status", values="count", title="Claims by Status")
            st.plotly_chart(fig, use_container_width=True)

    with g2:
        # Claims per Provider (join via Food_ID -> Provider_ID from food_listings)
        if {"Food_ID"}.issubset(f.columns) and {"Food_ID", "Provider_ID"}.issubset(food_listings.columns):
            merged = f.merge(food_listings[["Food_ID", "Provider_ID"]], on="Food_ID", how="left")
            if "Provider_ID" in merged.columns and not merged["Provider_ID"].isna().all():
                cdf = vc_df(merged["Provider_ID"], "Provider_ID", "Claims")
                fig = px.bar(cdf, x="Provider_ID", y="Claims", title="Claims per Provider")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Provider_ID not available after merging claims with food_listings.")
        else:
            st.info("Need Food_ID in claims and Provider_ID in food_listings to show claims per provider.")

    # Top Receivers by Completed Claims
    if {"Receiver_ID", "Status"}.issubset(f.columns) and "Name" in receivers.columns:
        completed = f[f["Status"].str.lower() == "completed"] if f["Status"].dtype == object else f
        top_recv = completed["Receiver_ID"].value_counts().reset_index(name="Completed_Claims")
        top_recv.rename(columns={"index": "Receiver_ID"}, inplace=True)
        top_recv = top_recv.merge(receivers[["Receiver_ID", "Name"]], on="Receiver_ID", how="left")
        if not top_recv.empty:
            st.subheader("🏆 Top Receivers (Completed Claims)")
            fig = px.bar(top_recv.head(15), x="Name", y="Completed_Claims", title="Top Receivers by Completed Claims")
            st.plotly_chart(fig, use_container_width=True)

# =========================
# Sidebar & Routing
# =========================
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Providers", "Receivers", "Food Listings", "Claims"])

if page == "Overview":
    page_overview(providers, receivers, food_listings, claims)
elif page == "Providers":
    page_providers(providers)
elif page == "Receivers":
    page_receivers(receivers)
elif page == "Food Listings":
    page_food_listings(food_listings)
elif page == "Claims":
    page_claims(claims, food_listings, receivers)

