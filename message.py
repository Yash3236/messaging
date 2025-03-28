import streamlit as st
import pandas as pd
import io
from PIL import Image  # For image icons
import base64
import os  # Import os module


# Function to convert an image to base64 for embedding in HTML
def img_to_bytes(img_path):
    try:
        img = Image.open(img_path)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')  # Or another suitable format
        return img_buffer.getvalue()
    except FileNotFoundError:
        st.error(f"Image file not found: {img_path}")
        return None  # Return None if the image is not found
    except Exception as e:
        st.error(f"Error processing image {img_path}: {e}")
        return None


def img_to_html(img_path):
    img_bytes = img_to_bytes(img_path)
    if img_bytes:  # Check if img_bytes is not None
        base64_str = base64.b64encode(img_bytes).decode()
        return f'<img src="data:image/png;base64,{base64_str}" width="20" height="20">'  # Adjust size as needed
    else:
        return ""  # Return an empty string if the image is missing


def main():
    st.set_page_config(
        page_title="My Messaging App",
        page_icon=":speech_balloon:",  # Emoji icon
        layout="wide",
    )

    # Ensure image files exist before proceeding
    image_files = ['chat.png', 'add_user.png', 'send.png']
    for img_file in image_files:
        if not os.path.exists(img_file):
            st.error(f"Error: Image file '{img_file}' not found.  Place it in the same directory as the script.")
            st.stop()  # Stop the app if images are missing

    title_html = img_to_html('chat.png')
    if title_html:
        st.title(f"{title_html} My Messaging App")  # Using image for title
    else:
        st.title("My Messaging App")  # Fallback title if image fails to load

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

        add_user_html = img_to_html('add_user.png')
        if st.button(f"{add_user_html} Add Contact" if add_user_html else "Add Contact"):  # Button with image or text
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
            message = st.text_input(f"Message to {contact['name']}", key=contact['name'])  # unique key for each input

            send_html = img_to_html('send.png')
            if st.button(f"{send_html} Send" if send_html else "Send",
                         key=f"send_{contact['name']}"):  # Image or text for button
                st.write(f"Simulating sending message: '{message}' to {contact['name']}")
    else:
        st.info("No contacts added yet.  Please add contacts using the sidebar.")


if __name__ == "__main__":
    main()
