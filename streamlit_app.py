
import streamlit as st
import pandas as pd
import datetime
import qrcode
from io import BytesIO
from pathlib import Path

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="EcoLoop Node | NGIH",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. APPLICATION SETTINGS
# =========================================================

CAPACITY = 50.0

LOGO_FILE = "IMG-20261028-WA0000.jpg"

STATIONS = {
    "EcoLoop Station 001": "ECO001",
    "EcoLoop Station 002": "ECO002",
    "EcoLoop Station 003": "ECO003"
}

MATERIALS = [
    "Plastic",
    "Paper",
    "Metal",
    "Glass",
    "Organic",
    "Electronic"
]

ACCOUNT_TYPES = [
    "Individual",
    "School",
    "University",
    "Organisation"
]

# =========================================================
# 3. SESSION DATA
# =========================================================

defaults = {
    "users": [],
    "contributions": [],
    "collections": [],
    "bins": {material: 0.0 for material in MATERIALS},
    "current_user": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, dict) else (
            value.copy() if isinstance(value, list) else value
        )

# =========================================================
# 4. VISUAL DESIGN
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

h1, h2, h3 {
    color: #1687FF;
}

div.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    min-height: 42px;
}

div.stFormSubmitButton > button {
    border-radius: 10px;
    font-weight: bold;
}

.metric-card {
    background: #eef5ff;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}

.footer {
    text-align: center;
    padding: 22px;
    color: #1687FF;
}

.small-note {
    color: #667085;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 5. HELPER FUNCTIONS
# =========================================================

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def total_waste():
    return sum(st.session_state.bins.values())


def approved_records():
    return [
        record
        for record in st.session_state.contributions
        if record["Status"] == "Approved"
    ]


def pending_records():
    return [
        record
        for record in st.session_state.contributions
        if record["Status"] == "Pending"
    ]


def award_points(weight):
    return 5 + int(weight * 2)


def generate_qr(code):
    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=3
    )

    qr.add_data(code)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return output


def find_user(name):
    for user in st.session_state.users:
        if user["Name"].lower() == name.lower():
            return user
    return None


def get_team_points():
    teams = {}

    for user in st.session_state.users:
        team = user["Team"]

        if team not in teams:
            teams[team] = 0

        teams[team] += user["Points"]

    return teams


def safe_dataframe(records):
    if records:
        st.dataframe(
            pd.DataFrame(records),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No records available yet.")


# =========================================================
# 6. HEADER AND BRANDING
# =========================================================

logo_col, title_col = st.columns([1, 5])

with logo_col:
    if Path(LOGO_FILE).is_file():
        st.image(LOGO_FILE, width=105)
    else:
        st.markdown("## ♻️ NGIH")

with title_col:
    st.title("EcoLoop Node")
    st.caption(
        "Intelligent Waste Management & Environmental Impact Platform"
    )
    st.caption("Powered by Next Gen Impact Hub (NGIH)")

st.info(
    "Prototype version: information is stored temporarily during "
    "the active application session. Permanent database storage "
    "and secure user authentication are not yet connected."
)

st.divider()

# =========================================================
# 7. NAVIGATION
# =========================================================

st.sidebar.title("♻️ EcoLoop Node")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Register / Profile",
        "Record Waste",
        "Verification",
        "Leaderboards",
        "Collection Management",
        "Environmental Impact",
        "About EcoLoop"
    ]
)

st.sidebar.divider()

st.sidebar.caption("Prototype navigation")

st.sidebar.warning(
    "Coordinator controls are for demonstration only. "
    "They are not protected by secure accounts yet."
)

st.sidebar.metric(
    "Registered Participants",
    len(st.session_state.users)
)

st.sidebar.metric(
    "Pending Contributions",
    len(pending_records())
)

# =========================================================
# 8. HOME DASHBOARD
# =========================================================

if page == "Home":

    st.header("EcoLoop Dashboard")

    approved = approved_records()
    pending = pending_records()

    total = total_waste()

    approved_weight = sum(
        record["Weight (kg)"]
        for record in approved
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Waste in Stations",
        f"{total:.1f} kg"
    )

    c2.metric(
        "Verified Waste",
        f"{approved_weight:.1f} kg"
    )

    c3.metric(
        "Pending Contributions",
        len(pending)
    )

    c4.metric(
        "Registered Participants",
        len(st.session_state.users)
    )

    st.divider()

    st.subheader("Waste Collection Stations")

    for material, quantity in st.session_state.bins.items():

        st.write(f"**{material} Bin**")

        progress = min(quantity / CAPACITY, 1.0)

        st.progress(progress)

        col1, col2, col3 = st.columns(3)

        col1.write(f"Recorded: {quantity:.1f} kg")
        col2.write(f"Capacity: {CAPACITY:.1f} kg")

        if quantity >= CAPACITY:
            col3.error("Collection needed")
        elif quantity >= CAPACITY * 0.8:
            col3.warning("Nearly full")
        else:
            col3.success("Capacity available")

    st.divider()

    st.subheader("Recent Contributions")

    recent = st.session_state.contributions[-5:]

    safe_dataframe(recent)

    st.divider()

    st.subheader("Platform Overview")

    st.write(
        "EcoLoop Node connects individuals, educational institutions "
        "and organisations through a shared environmental contribution "
        "and waste collection platform."
    )

# =========================================================
# 9. REGISTRATION AND PROFILES
# =========================================================

elif page == "Register / Profile":

    st.header("Registration and User Profiles")

    st.write(
        "Register as an individual, school, university or organisation."
    )

    with st.form("registration_form"):

        name = st.text_input(
            "Name or institution name"
        )

        account_type = st.selectbox(
            "Account type",
            ACCOUNT_TYPES
        )

        team = st.text_input(
            "Team or organisation name",
            placeholder="Enter your team name"
        )

        submitted = st.form_submit_button("Register")

        if submitted:

            if not name.strip():
                st.error("Please enter a name.")

            elif find_user(name.strip()):
                st.error("This name is already registered.")

            else:

                user = {
                    "Name": name.strip(),
                    "Account Type": account_type,
                    "Team": team.strip() if team.strip() else name.strip(),
                    "Points": 0,
                    "Date Registered": now()
                }

                st.session_state.users.append(user)
                st.session_state.current_user = user["Name"]

                st.success("Registration completed in this prototype.")

    st.divider()

    st.subheader("Registered Participants")

    safe_dataframe(st.session_state.users)

    if st.session_state.current_user:

        st.divider()

        st.subheader("Current Demo Profile")

        user = find_user(st.session_state.current_user)

        if user:
            st.write(f"**Name:** {user['Name']}")
            st.write(f"**Account type:** {user['Account Type']}")
            st.write(f"**Team:** {user['Team']}")
            st.metric("Points", user["Points"])

# =========================================================
# 10. RECORD WASTE
# =========================================================

elif page == "Record Waste":

    st.header("Record a Waste Contribution")

    st.write(
        "Submit a contribution at an EcoLoop collection station."
    )

    st.subheader("Collection Station QR Codes")

    selected_station = st.selectbox(
        "Select a collection station",
        list(STATIONS.keys())
    )

    station_code = STATIONS[selected_station]

    qr_col1, qr_col2 = st.columns([1, 2])

    with qr_col1:

        st.image(
            generate_qr(station_code),
            width=175,
            caption=station_code
        )

    with qr_col2:

        st.write("**Station identification**")
        st.write(selected_station)
        st.code(station_code)

        st.caption(
            "This prototype generates station QR codes. "
            "Camera-based QR scanning is a future feature. "
            "For now, contributors enter the displayed station code."
        )

    st.divider()

    registered_names = [
        user["Name"]
        for user in st.session_state.users
    ]

    with st.form("waste_contribution_form"):

        if registered_names:

            contributor = st.selectbox(
                "Registered contributor",
                registered_names
            )

        else:

            contributor = st.text_input(
                "Contributor name"
            )

            st.caption(
                "Register a participant first to connect contributions "
                "to a profile and leaderboard."
            )

        material = st.selectbox(
            "Waste material",
            MATERIALS
        )

        weight = st.number_input(
            "Quantity in kilograms",
            min_value=0.1,
            max_value=100.0,
            value=1.0,
            step=0.5
        )

        station_confirmation = st.text_input(
            "Enter the station code shown above"
        )

        submitted = st.form_submit_button(
            "Submit Contribution"
        )

        if submitted:

            if not contributor.strip():

                st.error("Please identify the contributor.")

            elif station_confirmation.strip().upper() != station_code:

                st.error("Station code does not match.")

            else:

                contribution = {
                    "ID": len(st.session_state.contributions) + 1,
                    "Contributor": contributor.strip(),
                    "Material": material,
                    "Weight (kg)": float(weight),
                    "Station": selected_station,
                    "Station Code": station_code,
                    "Date": now(),
                    "Status": "Pending",
                    "Points": 0,
                    "Verified By": "",
                    "Rejection Reason": ""
                }

                st.session_state.contributions.append(
                    contribution
                )

                st.success(
                    "Contribution submitted successfully. "
                    "It is awaiting coordinator verification."
                )

    st.divider()

    st.subheader("Your Contribution Records")

    safe_dataframe(
        [
            record
            for record in st.session_state.contributions
            if record["Contributor"] == st.session_state.current_user
        ]
    )

# =========================================================
# 11. COORDINATOR VERIFICATION
# =========================================================

elif page == "Verification":

    st.header("Coordinator Verification Dashboard")

    st.warning(
        "Demonstration mode: this page is not protected by "
        "coordinator authentication. Do not use it for real-world "
        "verification until secure roles are implemented."
    )

    pending = pending_records()

    st.metric(
        "Pending Contributions",
        len(pending)
    )

    if pending:

        for record in pending:

            st.divider()

            st.subheader(
                f"Contribution #{record['ID']}"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Contributor:** {record['Contributor']}")
                st.write(f"**Material:** {record['Material']}")
                st.write(f"**Quantity:** {record['Weight (kg)']} kg")

            with col2:
                st.write(f"**Station:** {record['Station']}")
                st.write(f"**Station code:** {record['Station Code']}")
                st.write(f"**Date:** {record['Date']}")

            reason = st.text_input(
                "Reason for rejection (if applicable)",
                key=f"reason_{record['ID']}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Approve Contribution",
                    key=f"approve_{record['ID']}"
                ):

                    record["Status"] = "Approved"

                    record["Points"] = award_points(
                        record["Weight (kg)"]
                    )

                    record["Verified By"] = "Demo Coordinator"

                    st.session_state.bins[
                        record["Material"]
                    ] += record["Weight (kg)"]

                    user = find_user(record["Contributor"])

                    if user:
                        user["Points"] += record["Points"]

                    st.success(
                        "Contribution approved and points awarded."
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "Reject Contribution",
                    key=f"reject_{record['ID']}"
                ):

                    record["Status"] = "Rejected"
                    record["Verified By"] = "Demo Coordinator"
                    record["Rejection Reason"] = reason.strip()

                    st.warning("Contribution rejected.")

                    st.rerun()

    else:

        st.success("There are no pending contributions.")

    st.divider()

    st.subheader("Verification History")

    safe_dataframe(st.session_state.contributions)

# =========================================================
# 12. INDIVIDUAL AND TEAM LEADERBOARDS
# =========================================================

elif page == "Leaderboards":

    st.header("EcoLoop Leaderboards")

    st.write(
        "Recognising individuals and teams contributing "
        "to environmental protection."
    )

    tab1, tab2 = st.tabs(
        ["Individual Rankings", "Team Rankings"]
    )

    with tab1:

        st.subheader("Individual Leaderboard")

        individuals = [
            user
            for user in st.session_state.users
            if user["Account Type"] == "Individual"
        ]

        individuals = sorted(
            individuals,
            key=lambda user: user["Points"],
            reverse=True
        )

        if individuals:

            individual_data = []

            for rank, user in enumerate(individuals, start=1):

                individual_data.append({
                    "Rank": rank,
                    "Participant": user["Name"],
                    "Points": user["Points"]
                })

            safe_dataframe(individual_data)

        else:

            st.info("No individual rankings available yet.")

    with tab2:

        st.subheader("Team Leaderboard")

        teams = get_team_points()

        if teams:

            team_data = []

            ranked_teams = sorted(
                teams.items(),
                key=lambda item: item[1],
                reverse=True
            )

            for rank, (team, points) in enumerate(
                ranked_teams,
                start=1
            ):

                team_data.append({
                    "Rank": rank,
                    "Team / Organisation": team,
                    "Points": points
                })

            safe_dataframe(team_data)

        else:

            st.info("No team rankings available yet.")

    st.caption(
        "Rankings are based on approved contributions only. "
        "Monthly and annual ranking periods can be added later."
    )

# =========================================================
# 13. COLLECTION MANAGEMENT
# =========================================================

elif page == "Collection Management":

    st.header("Waste Collection Management")

    st.write(
        "Monitor station capacity and record waste collections."
    )

    for material, quantity in st.session_state.bins.items():

        st.divider()

        st.subheader(f"{material} Bin")

        st.write(
            f"Current quantity: {quantity:.1f} kg"
        )

        st.progress(
            min(quantity / CAPACITY, 1.0)
        )

        if quantity >= CAPACITY:

            st.warning("This bin is full. Collection is required.")

        elif quantity >= CAPACITY * 0.8:

            st.warning("This bin is approaching capacity.")

        if quantity > 0:

            if st.button(
                f"Mark {material} as Collected",
                key=f"collect_{material}"
            ):

                collection = {
                    "Material": material,
                    "Collected Quantity (kg)": quantity,
                    "Date": now(),
                    "Recorded By": "Demo Coordinator"
                }

                st.session_state.collections.append(
                    collection
                )

                st.session_state.bins[material] = 0.0

                st.success("Collection recorded successfully.")

                st.rerun()

    st.divider()

    st.subheader("Collection History")

    safe_dataframe(st.session_state.collections)

# =========================================================
# 14. ENVIRONMENTAL IMPACT
# =========================================================

elif page == "Environmental Impact":

    st.header("Environmental Impact Dashboard")

    records = approved_records()

    total_approved = sum(
        record["Weight (kg)"]
        for record in records
    )

    number_of_contributions = len(records)

    col1, col2 = st.columns(2)

    col1.metric(
        "Verified Waste Contributions",
        f"{total_approved:.1f} kg"
    )

    col2.metric(
        "Approved Contributions",
        number_of_contributions
    )

    st.divider()

    st.subheader("Material Breakdown")

    if records:

        df = pd.DataFrame(records)

        material_data = df.groupby(
            "Material"
        )["Weight (kg)"].sum()

        st.bar_chart(material_data)

        st.subheader("Verified Contribution Records")

        safe_dataframe(records)

    else:

        st.info(
            "Environmental statistics will appear when "
            "contributions have been approved."
        )

    st.divider()

    st.subheader("Environmental Mission")

    st.write(
        "EcoLoop Node aims to encourage responsible waste disposal, "
        "improve recycling participation and support better "
        "community-level environmental decision-making."
    )

# =========================================================
# 15. ABOUT ECOLOOP NODE
# =========================================================

elif page == "About EcoLoop":

    st.header("About EcoLoop Node")

    st.write("""
    **EcoLoop Node** is a youth-driven environmental technology
    initiative developed under **Next Gen Impact Hub (NGIH)**.

    The platform aims to improve waste management through digital
    contribution tracking, verification, collection coordination,
    environmental awareness and community participation.

    Its long-term vision is to combine software, electronics,
    robotics and artificial intelligence to develop affordable
    intelligent waste-management solutions.
    """)

    st.divider()

    st.subheader("Who Can Participate?")

    st.markdown("""
    - Individuals
    - Schools
    - Universities
    - Community organisations
    - Environmental groups
    """)

    st.divider()

    st.subheader("Core Objectives")

    st.markdown("""
    - Encourage responsible waste disposal.
    - Promote recycling and environmental protection.
    - Connect individuals and institutions.
    - Recognise verified environmental contributions.
    - Improve waste collection coordination.
    - Generate useful environmental data.
    - Develop smart waste-management technology.
    """)

    st.divider()

    st.subheader("Future Technology Development")

    st.markdown("""
    - Secure user accounts and role-based access.
    - Permanent database storage.
    - Camera-based QR scanning.
    - Coordinator and QR verification workflows.
    - ESP32 and smart-bin sensor integration.
    - Automated fill-level monitoring.
    - AI-assisted waste classification.
    - Advanced environmental analytics.
    """)

    st.info(
        "EcoLoop Node is currently a software prototype. "
        "Physical sensors and automated waste classification "
        "are not yet connected."
    )

# =========================================================
# 16. FOOTER
# =========================================================

st.divider()

st.markdown("""
<div class="footer">

    <strong>POWERED BY NEXT GEN IMPACT HUB (NGIH)</strong>

    <p><strong>Munashe Roy Mutopa</strong></p>

    <p>Project Coordinator & Developer</p>

    <small>Building technology for sustainable communities.</small>

    <br><br>

    <small>EcoLoop Node | Prototype Development</small>

</div>
""", unsafe_allow_html=True)
