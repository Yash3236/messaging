import streamlit as st
import pandas as pd
import io
from PIL import Image
import base64
import platform
import os

# Platform-specific contact access libraries
try:
    if platform.system() == 'Darwin':  # macOS
        import contacts  # pip install pycontacts
    elif platform.system() == 'Windows':
        import win32com.client  # Needs pywin32: pip install pywin32
    elif platform.system() == 'Linux':
        # Placeholder; requires more specific library and setup
        pass # or st.warning("Linux contact access needs configuration.")
except ImportError as e:
    st.warning(f"Contact access libraries are not fully available: {e}")

# Function to get device contacts (platform-specific)
def get_device_contacts():
    contacts_list = []
    try:
        if platform.system() == 'Darwin':  # macOS
            try:
                contact_store = contacts.Contacts()
                for contact in contact_store.contacts:
                    name = contact.full_name
                    phone = contact.phones[0].value if contact.phones else ''
                    contacts_list.append({'name': name, 'phone_number': phone})
            except Exception as e:
                st.error(f"Error accessing contacts on macOS: {e}")

        elif platform.system() == 'Windows':
            try:
                outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
                for i in range(1, outlook.AddressLists.Count + 1):
                    address_book = outlook.AddressLists[i]  # Iterate through address books
                    for contact in address_book.AddressEntries:
                        try:
                            if contact.Class == 43: #OlContact
                                user = contact.GetContact()
                                name = contact.FullName
                                phone = user.BusinessTelephoneNumber if user.BusinessTelephoneNumber else ""
                                contacts_list.append({'name': name, 'phone_number': phone})

                        except Exception as e:
                            st.warning(f"Error processing a contact: {e}")
            except Exception as e:
                st.error(f"Error accessing Outlook on Windows: {e}")

        elif platform.system() == 'Linux':
            st.warning("Linux contact access requires specific configuration and libraries.")

        else:
            st.warning(f"Contact access not supported on {platform.system()}")

    except Exception as e:
        st.error(f"General error accessing contacts: {e}")

    return contacts_list


# Function to convert an image to bytes with error handling
def img_to_bytes(img_path):
    try:
        with Image.open(img_path) as img:
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="PNG")
            return img_buffer.getvalue()
    except FileNotFoundError:
        st.error(f"Image not found: {img_path}")
        return None
    except Exception as e:
        st.error(f"Error processing image {img_path}: {e}")
        return None


# Function to convert an image to HTML with base64 encoding
def img_to_html(img_path, width=20, height=20):
    img_bytes = img_to_bytes(img_path)
    if img_bytes:
        base64_str = base64.b64encode(img_bytes).decode()
        return f'<img src="data:image/png;base64,{base64_str}" width="{width}" height="{height}">'
    return ""


# Main Streamlit application
def main():
    try: # Added a try/except block for the entire main function
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

    except Exception as e:  # Catch any errors within the main function
        st.error(f"An unexpected error occurred: {e}")


#Run the app
if __name__ == "__main__":
    main()
