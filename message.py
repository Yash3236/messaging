# Main Streamlit application
def main():
    st.set_page_config(
        page_title="Contact Messaging App",
        page_icon=":speech_balloon:",
        layout="wide",
    )

    # App Title
    title_image_html = img_to_html("chat.png")
    st.title(f"{title_image_html} Contact Messaging App")

    # Initialize Session State
    if "contacts" not in st.session_state:
        st.session_state["contacts"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = {}

    # Device Contacts Section
    st.header("Device Contacts")

    if st.button("Import Device Contacts"):
        device_contacts = get_device_contacts()
        if device_contacts:
            new_contacts = []
            for contact in device_contacts:
                # Check for duplicates more robustly (handle None values)
                existing = next(
                    (
                        c
                        for c in st.session_state["contacts"]
                        if c.get("name") == contact.get("name")
                        and c.get("phone_number") == contact.get("phone_number")
                    ),
                    None,
                )  # default to None
                if not existing:
                    new_contacts.append(contact)
                    st.session_state["messages"][contact["name"]] = []
            st.session_state["contacts"].extend(new_contacts)
            st.success(f"Imported {len(new_contacts)} contacts.")
        else:
            st.warning("No contacts found or access denied.")

    # Manual Contact Management (Sidebar)
    with st.sidebar:
        st.header("Manual Contact Management")

        # Add Contact Form
        with st.form("add_contact_form"):
            st.subheader("Add Contact Manually")
            name = st.text_input("Name")
            phone_number = st.text_input("Phone Number")
            submitted = st.form_submit_button("Add Contact")

            if submitted:
                if name and phone_number:
                    # Check for duplicate contact details
                    existing = next(
                        (
                            c
                            for c in st.session_state["contacts"]
                            if c.get("name") == name
                            and c.get("phone_number") == phone_number
                        ),
                        None,
                    )
                    if not existing:
                        new_contact = {"name": name, "phone_number": phone_number}
                        st.session_state["contacts"].append(new_contact)
                        st.session_state["messages"][name] = []
                        st.success("Contact added!")
                    else:
                        st.warning("Contact already exists.")
                else:
                    st.error("Please enter both name and phone number.")

        # CSV Upload
        st.subheader("Upload Contacts (CSV)")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)

                # Normalize column names and handle missing values gracefully
                df.columns = [
                    col.lower().strip().replace(" ", "_") for col in df.columns
                ]
                name_cols = [col for col in df.columns if "name" in col]
                phone_cols = [
                    col for col in df.columns if "phone" in col or "number" in col
                ]

                if not name_cols or not phone_cols:
                    st.error("CSV needs columns with 'name' and 'phone' in their names.")
                else:
                    name_col = name_cols[0]
                    phone_col = phone_cols[0]

                    new_contacts = []
                    for index, row in df.iterrows():
                        name = row[name_col]
                        phone = row[phone_col]

                        if pd.isna(name) or pd.isna(phone):  # handle missing data
                            st.warning(
                                f"Skipping row {index+2} due to missing name or phone."
                            )
                            continue

                        name = str(name)  # cast to string, handles numbers
                        phone = str(phone)
                        # Robust duplicate checking
                        existing = next(
                            (
                                c
                                for c in st.session_state["contacts"]
                                if c.get("name") == name
                                and c.get("phone_number") == phone
                            ),
                            None,
                        )
                        if not existing:
                            new_contacts.append({"name": name, "phone_number": phone})
                            st.session_state["messages"][name] = []

                    st.session_state["contacts"].extend(new_contacts)
                    st.success(f"Uploaded {len(new_contacts)} contacts.")

            except Exception as e:
                st.error(f"CSV processing error: {e}")

    # Contact & Messaging Area
    st.header("Contacts and Messaging")

    if not st.session_state["contacts"]:
        st.info("No contacts added. Add contacts via sidebar or device import.")
    else:
        for contact in st.session_state["contacts"]:
            name = contact["name"]  # Get name
            phone = contact["phone_number"]  # Get number

            st.subheader(f"{name} - {phone}")

            # Display Previous Messages
            if st.session_state["messages"].get(name):
                st.write("Previous Messages:")
                for msg in st.session_state["messages"][name]:
                    st.write(msg)

            # Message Input
            message = st.text_input(
                "Message", key=f"message_{name}", placeholder="Type your message..."
            )
            col1, col2, _ = st.columns([0.2, 0.2, 0.6])  # Added columns for layout

            with col1:
                send_button = st.button(
                    "Send", key=f"send_{name}"
                )

            if send_button and message:
                if name not in st.session_state["messages"]:
                    st.session_state["messages"][name] = []
                st.session_state["messages"][name].append(f"You: {message}")

                # Trigger a re-run by changing a session state variable:
                st.session_state["rerun_flag"] = not st.session_state.get(
                    "rerun_flag", False
                )
#Run the app
if __name__ == "__main__":
    main()
