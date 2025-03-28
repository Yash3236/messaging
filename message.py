import streamlit as st
import pandas as pd
import io
from PIL import Image
import base64


def img_to_bytes(img_path):
    """
    Convert an image to bytes, with improved error handling.
    
    Args:
        img_path (str): Path to the image file
    
    Returns:
        bytes or None: Base64 encoded image bytes or None if conversion fails
    """
    try:
        with Image.open(img_path) as img:
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
    except FileNotFoundError:
        st.error(f"Image not found: {img_path}")
        return None
    except Exception as e:
        st.error(f"Error processing image {img_path}: {e}")
        return None


def img_to_html(img_path, width=20, height=20):
    """
    Convert an image to an HTML img tag with base64 encoding.
    
    Args:
        img_path (str): Path to the image file
        width (int): Image width in pixels
        height (int): Image height in pixels
    
    Returns:
        str: HTML img tag or empty string if conversion fails
    """
    img_bytes = img_to_bytes(img_path)
    if img_bytes:
        base64_str = base64.b64encode(img_bytes).decode()
        return f'<img src="data:image/png;base64,{base64_str}" width="{width}" height="{height}">'
    return ""


def main():
    """
    Main Streamlit application for contact management and messaging.
    """
    # Configure Streamlit page
    st.set_page_config(
        page_title="Contact Management Messaging App",
        page_icon=":speech_balloon:",
        layout="wide",
    )

    # Page title with optional image
    title_image = img_to_html('chat.png')
    st.title(f"{title_image} Contact Management Messaging App")

    # Initialize session state for contacts and messages
    if 'contacts' not in st.session_state:
        st.session_state['contacts'] = []
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = {}

    # Sidebar for Contact Management
    with st.sidebar:
        st.header("Contact Management")

        # Manual Contact Entry
        st.subheader("Add Contact Manually")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", key="contact_name")
        
        with col2:
            phone_number = st.text_input("Phone Number", key="contact_phone")

        # Add Contact Button with optional image
        add_user_image = img_to_html('add_user.png')
        add_contact_button = st.button(
            f"{add_user_image} Add Contact" if add_user_image else "Add Contact"
        )

        if add_contact_button:
            if name and phone_number:
                # Check for duplicate contacts
                existing_contact = next(
                    (contact for contact in st.session_state['contacts'] 
                     if contact['name'] == name or contact['phone_number'] == phone_number), 
                    None
                )
                
                if existing_contact:
                    st.warning("Contact already exists!")
                else:
                    new_contact = {"name": name, "phone_number": phone_number}
                    st.session_state['contacts'].append(new_contact)
                    st.session_state['messages'][name] = []
                    st.success(f"Contact {name} added successfully!")
            else:
                st.warning("Please enter both name and phone number.")

        # CSV Contact Upload
        st.subheader("Upload Contacts (CSV)")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        if uploaded_file is not None:
            try:
                # Read CSV with flexible column names
                df = pd.read_csv(uploaded_file)
                
                # Normalize column names (remove spaces, convert to lowercase)
                df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
                
                # Try to find name and phone number columns
                name_cols = [col for col in df.columns if 'name' in col]
                phone_cols = [col for col in df.columns if 'phone' in col or 'number' in col]
                
                if not (name_cols and phone_cols):
                    st.error("CSV must contain columns for name and phone number.")
                else:
                    name_col = name_cols[0]
                    phone_col = phone_cols[0]
                    
                    # Add contacts from CSV
                    new_contacts = []
                    for _, row in df.iterrows():
                        name = row[name_col]
                        phone = row[phone_col]
                        
                        # Skip rows with missing data
                        if pd.isna(name) or pd.isna(phone):
                            continue
                        
                        # Check for duplicates
                        existing_contact = next(
                            (contact for contact in st.session_state['contacts'] 
                             if contact['name'] == name or contact['phone_number'] == phone), 
                            None
                        )
                        
                        if not existing_contact:
                            new_contacts.append({"name": name, "phone_number": phone})
                            st.session_state['messages'][name] = []
                    
                    st.session_state['contacts'].extend(new_contacts)
                    st.success(f"Uploaded {len(new_contacts)} new contacts.")
            
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    # Main Contact and Messaging Area
    st.header("Contacts and Messages")

    if not st.session_state['contacts']:
        st.info("No contacts added yet. Please add contacts using the sidebar.")
    else:
        # Display contacts and messaging interface
        for contact in st.session_state['contacts']:
            st.subheader(f"{contact['name']} - {contact['phone_number']}")
            
            # Display previous messages
            if st.session_state['messages'].get(contact['name']):
                st.write("Previous Messages:")
                for msg in st.session_state['messages'][contact['name']]:
                    st.write(msg)
            
            # Message input and send button
            message = st.text_input(
                f"Message to {contact['name']}", 
                key=f"msg_{contact['name']}"
            )
            
            send_image = img_to_html('send.png')
            if st.button(
                f"{send_image} Send" if send_image else "Send", 
                key=f"send_btn_{contact['name']}"
            ):
                if message.strip():
                    # Store message in session state
                    if contact['name'] not in st.session_state['messages']:
                        st.session_state['messages'][contact['name']] = []
                    
                    st.session_state['messages'][contact['name']].append(
                        f"You: {message}"
                    )
                    st.experimental_rerun()  # Refresh to show new message
                else:
                    st.warning("Message cannot be empty.")


if __name__ == "__main__":
    main()
