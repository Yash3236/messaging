import streamlit as st
import pandas as pd
import io
from PIL import Image  # For image icons
import base64

# Function to convert an image to base64 for embedding in HTML
def img_to_bytes(img_path):
    img = Image.open(img_path)
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')  # Or another suitable format
    return img_buffer.getvalue()

def img_to_html(img_path):
    img_bytes = img_to_bytes(img_path)
    base64_str = base64.b64encode(img_bytes).decode()
    return f'<img src="data:image/png;base64,{base64_str}" width="20" height="20">'  # Adjust size as needed


def main():
    st.set_page_config(
        page_title="My Messaging App",
        page_icon=":speech_balloon:",  # Emoji icon
        layout="wide",
    )

    st.title(f"{img_to_html('chat.png')} My Messaging App") # Using image for title

    # Initialize contacts in session state
    if 'contacts' not in st.session_state:
        st.session_state['contacts'] = []

    # Sidebar for Contact Management
    with st.sidebar:
        st.header("Contact Management")

        # Option 1: Manual Contact Entry
        st.subheader("Add Contact Manually")
        name = st.text_input("Name")
        phone_number = st.text_input("Phone Number")

        if st.button(f"{img_to_html('add_user.png')} Add Contact"):  # Button with image
            if name and phone_number:
                st.session_state['contacts'].append({"name": name, "phone_number": phone_number})
                st.success(f"Contact {name} added!")
            else:
                st.warning("Please enter both name and phone number.")

        # Option 2: CSV Upload
        st.subheader("Upload Contacts (CSV)")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                # Assuming CSV has 'name' and 'phone_number' columns
                new_contacts = df.to_dict('records')
                st.session_state['contacts'].extend(new_contacts)
                st.success(f"Uploaded {len(new_contacts)} contacts.")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    # Main area: Contact List and Messaging (Simulated)
    st.header("Contacts")

    if st.session_state['contacts']:
        for contact in st.session_state['contacts']:
            st.write(f"**{contact['name']}**: {contact['phone_number']}")
            # Simulated messaging area (replace with actual logic if possible)
            message = st.text_input(f"Message to {contact['name']}", key=contact['name']) # unique key for each input
            if st.button(f"{img_to_html('send.png')} Send", key=f"send_{contact['name']}"):
                st.write(f"Simulating sending message: '{message}' to {contact['name']}")
    else:
        st.info("No contacts added yet.  Please add contacts using the sidebar.")

if __name__ == "__main__":
    main()
