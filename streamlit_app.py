
import streamlit as st
import pandas as pd
import datetime
import qrcode
from io import BytesIO

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="EcoLoop Node | NGIH",
    page_icon="♻️",
    layout="wide"
)

# --------------------------------------------------
# SESSION DATA
# --------------------------------------------------

if "users" not in st.session_state:
    st.session_state.users = []

if "contributions" not in st.session_state:
    st.session_state.contributions = []

if "collections" not in st.session_state:
    st.session_state.collections = []

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "bins" not in st.session_state:
    st.session_state.bins = {
        "Plastic": 0.0,
        "Paper": 0.0,
        "Metal": 0.0,
        "Glass": 0.0,
        "Organic": 0.0,
        "Electronic": 0.0
    }

CAPACITY = 50

STATIONS = {
    "EcoLoop Station 001": "ECO001",
    "EcoLoop Station 002": "ECO002",
    "EcoLoop Station 003": "ECO003"
}

MATERIALS = list(st.session_state.bins.keys())

# --------------------------------------------------
# STYLING
# --------------------------------------------------

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
    font-weight: bold;
}

.metric-card {
    background-color: #eef5ff;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
}

.footer {
    text-align: center;
    padding: 20px;
    color: #1687FF;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

col1, col2 = st.columns([1, 4])

with col1:
    try:
        st.image(
            "IMG-20261028-WA0000.jpg",
            width=105
        )
    except Exception:
        st.write("♻️ NGIH")

with col2:
    st.title("♻️ EcoLoop Node")
    st.caption("Intelligent Waste Management & Environmental Impact Platform")
    st.caption("Powered by Next Gen Impact Hub (NGIH)")

st.info(
    "Prototype demonstration: data is currently stored in temporary "
    "session memory. Permanent database storage is not connected."
)

st.divider()

# --------------------------------------------------
# SIDEBAR AND DEMO ACCOUNT
# --------------------------------------------------

st.sidebar.title("EcoLoop Navigation")

page = st.sidebar.radio(
    "Choose a section",
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

st.sidebar.warning(
    "Prototype mode: user roles are selectable for testing. "
    "They are not protected by real authentication."
)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def total_waste():
    return sum(st.session_state.bins.values())


def generate_qr(code):
    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=3
    )
    qr.add_data(code)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")

    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return output


def award_points(weight):
    return 5 + int(weight * 2)


def approved_records():
    return [
        record for record in st.session_state.contributions
        if record["Status"] == "Approved"
    ]


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if page == "Home":

    st.header("EcoLoop Dashboard")

    records = approved_records()

    total = total_waste()
    approved_count = len(records)
    pending_count = sum(
        1 for x in st.session_state.contributions
        if x["Status"] == "Pending"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Waste Recorded", f"{total:.1f} kg")
    c2.metric("Approved Contributions", approved_count)
    c3.metric("Pending Verification", pending_count)
    c4.metric("Registered Users", len(st.session_state.users))

    st.divider()

    st.subheader("Waste Collection Stations")

    for material, quantity in st.session_state.bins.items():

        st.write(f"**{material} Bin**")

        st.progress(min(quantity / CAPACITY, 1.0))

        col1, col2 = st.columns(2)

        col1.write(f"Recorded: {quantity:.1f} kg")
        col2.write(f"Capacity: {CAPACITY} kg")

        if quantity >= CAPACITY:
            st.warning("Collection needed")
        else:
            st.success("Capacity available")

    st.divider()

    st.subheader("Recent Contributions")

    if st.session_state.contributions:

        recent = pd.DataFrame(
            st.session_state.contributions
        )

        st.dataframe(
            recent.tail(5),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No contributions have been recorded yet.")

# --------------------------------------------------
# REGISTRATION AND PROFILE
# --------------------------------------------------

elif page == "Register / Profile":

    st.header("Registration and User Profiles")

    st.write(
        "EcoLoop Node welcomes individuals, schools, "
        "universities and organisations."
    )

    with st.form("registration_form"):

        name = st.text_input("Your name or organisation name")

        account_type = st.selectbox(
            "Account type",
            [
                "Individual",
                "School",
                "University",
                "Organisation"
            ]
        )

        team = st.text_input(
            "Team or organisation name (optional)"
        )

        submitted = st.form_submit_button("Register")

        if submitted:

            if not name.strip():
                st.error("Please enter a name.")

            else:

                user = {
                    "Name": name.strip(),
                    "Account Type": account_type,
                    "Team": team.strip() if team.strip() else name.strip(),
                    "Points": 0,
                    "Date Registered": datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )
                }

                st.session_state.users.append(user)
                st.session_state.current_user = user

                st.success("Registration completed in this prototype!")

    st.divider()

    st.subheader("Registered Participants")

    if st.session_state.users:

        st.dataframe(
            pd.DataFrame(st.session_state.users),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No registered participants yet.")

# --------------------------------------------------
# RECORD WASTE
# --------------------------------------------------

elif page == "Record Waste":

    st.header("Record a Waste Contribution")

    st.write(
        "Select a collection station and record the "
        "material and quantity contributed."
    )

    st.subheader("Collection Station QR Codes")

    selected_station = st.selectbox(
        "Choose a station",
        list(STATIONS.keys())
    )

    station_code = STATIONS[selected_station]

    st.image(
        generate_qr(station_code),
        width=170,
        caption=f"Station code: {station_code}"
    )

    st.caption(
        "This prototype generates station QR codes. "
        "The code must currently be selected manually; "
        "camera scanning is not yet connected."
    )

    st.divider()

    with st.form("waste_form"):

        contributor = st.text_input("Contributor name")

        material = st.selectbox(
            "Waste material",
            MATERIALS
        )

        weight = st.number_input(
            "Quantity in kilograms",
            min_value=0.1,
            max_value=100.0,
            step=0.5
        )

        station_confirmation = st.text_input(
            "Enter station code shown above"
        )

        submitted = st.form_submit_button(
            "Submit Contribution"
        )

        if submitted:

            if not contributor.strip():
                st.error("Please enter the contributor name.")

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
                    "Date": datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "Status": "Pending",
                    "Points": 0,
                    "Verified By": ""
                }

                st.session_state.contributions.append(
                    contribution
                )

                st.success(
                    "Contribution submitted! Awaiting coordinator verification."
                )

# --------------------------------------------------
# COORDINATOR VERIFICATION
# --------------------------------------------------

elif page == "Verification":

    st.header("Coordinator Verification Dashboard")

    st.warning(
        "Demonstration only: coordinator access is not yet "
        "protected by secure user accounts."
    )

    pending = [
        x for x in st.session_state.contributions
        if x["Status"] == "Pending"
    ]

    st.metric("Pending Contributions", len(pending))

    if pending:

        for record in pending:

            st.divider()

            st.subheader(
                f"Contribution #{record['ID']}"
            )

            st.write(f"Contributor: {record['Contributor']}")
            st.write(f"Material: {record['Material']}")
            st.write(f"Weight: {record['Weight (kg)']} kg")
            st.write(f"Station: {record['Station']}")
            st.write(f"Date: {record['Date']}")

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Approve",
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

                    for user in st.session_state.users:

                        if user["Name"].lower() == record[
                            "Contributor"
                        ].lower():

                            user["Points"] += record["Points"]

                    st.success("Contribution approved and points awarded.")
                    st.rerun()

            with col2:

                if st.button(
                    "Reject",
                    key=f"reject_{record['ID']}"
                ):

                    record["Status"] = "Rejected"
                    record["Verified By"] = "Demo Coordinator"

                    st.warning("Contribution rejected.")
                    st.rerun()

    else:
        st.success("There are no pending contributions.")

    st.divider()

    st.subheader("Verification History")

    if st.session_state.contributions:

        st.dataframe(
            pd.DataFrame(st.session_state.contributions),
            use_container_width=True,
            hide_index=True
        )

# --------------------------------------------------
# LEADERBOARDS
# --------------------------------------------------

elif page == "Leaderboards":

    st.header("EcoLoop Leaderboards")

    st.write(
        "Recognising individuals and organisations "
        "making a difference through waste management."
    )

    tab1, tab2 = st.tabs(
        ["Individual Rankings", "Team Rankings"]
    )

    with tab1:

        if st.session_state.users:

            individuals = [
                user for user in st.session_state.users
                if user["Account Type"] == "Individual"
            ]

            individuals = sorted(
                individuals,
                key=lambda x: x["Points"],
                reverse=True
            )

            if individuals:

                st.dataframe(
                    pd.DataFrame(individuals)[
                        ["Name", "Points"]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No individual rankings yet.")

        else:
            st.info("No registered users yet.")

    with tab2:

        if st.session_state.users:

            teams = {}

            for user in st.session_state.users:

                team_name = user["Team"]

                if team_name not in teams:
                    teams[team_name] = 0

                teams[team_name] += user["Points"]

            team_data = [
                {"Team": name, "Points": points}
                for name, points in teams.items()
            ]

            team_data = sorted(
                team_data,
                key=lambda x: x["Points"],
                reverse=True
            )

            st.dataframe(
                pd.DataFrame(team_data),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No teams registered yet.")

# --------------------------------------------------
# COLLECTION MANAGEMENT
# --------------------------------------------------

elif page == "Collection Management":

    st.header("Waste Collection Management")

    st.write(
        "Monitor waste stations and record collection activities."
    )

    for material, quantity in st.session_state.bins.items():

        st.subheader(f"{material} Bin")

        st.write(f"Current quantity: {quantity:.1f} kg")

        if quantity >= CAPACITY:
            st.warning("Bin is full. Collection required.")

        if quantity > 0:

            if st.button(
                f"Mark {material} as Collected",
                key=f"collect_{material}"
            ):

                collection = {
                    "Material": material,
                    "Collected Quantity (kg)": quantity,
                    "Date": datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )
                }

                st.session_state.collections.append(collection)

                st.session_state.bins[material] = 0.0

                st.success("Collection recorded.")
                st.rerun()

    st.divider()

    st.subheader("Collection History")

    if st.session_state.collections:

        st.dataframe(
            pd.DataFrame(st.session_state.collections),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No collections recorded yet.")

# --------------------------------------------------
# ENVIRONMENTAL IMPACT
# --------------------------------------------------

elif page == "Environmental Impact":

    st.header("Environmental Impact Dashboard")

    records = approved_records()

    total_approved = sum(
        record["Weight (kg)"]
        for record in records
    )

    st.metric(
        "Verified Waste Contributions",
        f"{total_approved:.1f} kg"
    )

    st.metric(
        "Total Approved Contributions",
        len(records)
    )

    st.subheader("Material Breakdown")

    if records:

        df = pd.DataFrame(records)

        material_data = df.groupby(
            "Material"
        )["Weight (kg)"].sum()

        st.bar_chart(material_data)

        st.subheader("Verified Contribution Records")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "Environmental impact statistics will appear "
            "after contributions are approved."
        )

# --------------------------------------------------
# ABOUT
# --------------------------------------------------

elif page == "About EcoLoop":

    st.header("About EcoLoop Node")

    st.write("""
    EcoLoop Node is a youth-driven environmental technology
    initiative developed under Next Gen Impact Hub (NGIH).

    The platform aims to improve waste management through
    digital contribution tracking, collection coordination,
    environmental awareness and community participation.

    Its long-term vision is to combine software, electronics,
    robotics and artificial intelligence to create affordable
    intelligent waste-management solutions.
    """)

    st.subheader("Our Objectives")

    st.markdown("""
    - Encourage responsible waste disposal.
    - Promote recycling and environmental protection.
    - Connect individuals, schools, universities and organisations.
    - Recognise verified environmental contributions.
    - Improve waste collection coordination.
    - Generate useful environmental data.
    - Introduce smart-bin technology in future developments.
    """)

    st.subheader("Future Technology")

    st.write("""
    Sensor integration, automated waste classification,
    permanent user accounts and real-time collection
    monitoring are planned for future development.
    """)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown("""
<div class="footer">
    <strong>POWERED BY NEXT GEN IMPACT HUB (NGIH)</strong>
    <p><strong>Munashe Roy Mutopa</strong></p>
    <p>Project Coordinator & Developer</p>
    <small>Building technology for sustainable communities.</small>
    <br>
    <small>EcoLoop Node | Prototype Development</small>
</div>
""", unsafe_allow_html=True)
