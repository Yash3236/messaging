import streamlit as st
import random
import time
import sqlite3
import os  # For setting file path
import re  # added regex
from urllib.parse import quote, unquote  # For URL encoding

# Room Capacity
MAX_USERS = 50

# List of System Emojis (Extend as desired)
EMOJIS = ["😀", "😂", "😎", "😍", "🤔", "👍", "❤️", "🎉", "🎈", "🎁", "🌟", "🔥", "💯", "✨", "✅", "😊", "👏", "🙌", "🥳"]

# Database setup
DATABASE_FILE = os.path.join(".", "chat_database.db")  # Database File


def get_random_emoji():
    """Returns a random emoji from the list."""
    return random.choice(EMOJIS)


def create_table(room_id):
    """Creates a table for the chat history of a specific room."""
    safe_room_id = re.sub(r'[^a-zA-Z0-9_]', '', room_id)  # Remove invalid characters.
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    try:
        c.execute(f'''CREATE TABLE IF NOT EXISTS room_{safe_room_id}
                     (timestamp REAL, message TEXT)''')  # Use safe table name
        conn.commit()
    except sqlite3.Error as e:  # Added except in case table is not created.
        print(f"Database error: {e}")
    finally:
        conn.close()


def save_message(room_id, message):
    """Saves a message to the chat history table."""
    safe_room_id = re.sub(r'[^a-zA-Z0-9_]', '', room_id)  # Remove invalid characters.
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    try:
        c.execute(f"INSERT INTO room_{safe_room_id} (timestamp, message) VALUES (?, ?)",
                  (time.time(), message))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def load_chat_history(room_id):
    """Loads chat history from the database."""
    safe_room_id = re.sub(r'[^a-zA-Z0-9_]', '', room_id)  # Remove invalid characters.
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    try:
        c.execute(f"SELECT message FROM room_{safe_room_id} ORDER BY timestamp ASC")
        messages = [row[0] for row in c.fetchall()]
    except sqlite3.OperationalError:  # If table does not exists.
        messages = []  # return empty array.
    finally:
        conn.close()
    return messages


def display_chat(room_id):
    """Displays the chat interface."""

    # Load chat history from the database
    chat_history = load_chat_history(room_id)
    for message in chat_history:
        st.markdown(message, unsafe_allow_html=True)  # Allow HTML for emoji inclusion

    # Input area
    new_message = st.text_input("Enter your message:", key="new_message", value="")

    # Emoji Selection
    with st.expander("Send an Emoji"):
        cols = st.columns(6)  # Adjust number of columns as needed
        for i in range(len(EMOJIS)):
            with cols[i % 6]:  # Distribute emojis across columns
                emoji = EMOJIS[i]
                if st.button(emoji, key=f"emoji_{i}"):
                    new_message = emoji  # Select emoji, and assign it to be new message.
    return new_message


def main():
    st.set_page_config(page_title="Anonymous Chatroom", layout="wide")

    # Determine if user is the host
    is_host = st.secrets.get("IS_HOST", False)  # Check environment variable

    # Room Creation/Joining
    if 'room_id' not in st.session_state:
        st.session_state['room_id'] = None  # Initialize room_id
        st.session_state['username'] = None  # Initialize username

    # Get room_id from URL parameters
    query_params = st.query_params #The New API.
    url_room_id = query_params.get("room_id", None)  # Get room_id from URL

    if url_room_id and not st.session_state['room_id']:  # Has the room id been set before?
        st.session_state['room_id'] = url_room_id
        create_table(st.session_state['room_id'])
        st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)  # Rerun

    if not st.session_state['room_id']:
        st.header("Create or Join a Chatroom")
        if is_host:
            st.subheader("Host Controls")
            room_id_input = st.text_input("Enter 6-digit Chatroom ID:", max_chars=6, type="password")
            create_room = st.button("Create Room")

            if create_room:
                if room_id_input.isdigit() and len(room_id_input) == 6:
                    safe_room_id = re.sub(r'[^a-zA-Z0-9_]', '', room_id_input)  # Sanitize the room ID
                    st.session_state['room_id'] = safe_room_id  # Generate unique room ID
                    st.success(f"Room created! Share this app URL with `?room_id={st.session_state['room_id']}` with others.")
                    create_table(st.session_state['room_id'])  # Create table for room.
                    st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False) #Rerun
                else:
                    st.error("Room ID must be a 6-digit number.")

        else:  # Regular user
            st.subheader("Join a Chatroom")
            join_room = st.text_input("Enter Chatroom ID:")
            if join_room:
                safe_join_room = re.sub(r'[^a-zA-Z0-9_]', '', join_room)
                st.session_state['room_id'] = safe_join_room
                create_table(st.session_state['room_id'])
                st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)  # Rerun

        return  # Stop execution until room ID is set

    # Username Input
    if not st.session_state['username']:  # Make sure user has joined before setting user name
        username = st.text_input("Enter your username:")
        if username:
            st.session_state['username'] = username  # Set Username
            st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)  # Rerun
        else:
            st.warning("Please enter a username.")
            return

    # Display Username
    st.write(f"You are chatting as: **{st.session_state['username']}**")  # Show Username.

    # Check User Limit
    if len(st.session_state.get('users', [])) >= MAX_USERS:  # Create a list of users.
        st.error("This room is full.")
        return

    # Add user to session (basic implementation - improve for concurrency)
    if 'users' not in st.session_state:
        st.session_state['users'] = []

    if st.session_state['username'] not in st.session_state['users']:
        st.session_state['users'].append(st.session_state['username'])

    # Main display chat
    st.title(f"Chatroom: {st.session_state['room_id']}")
    message = display_chat(st.session_state['room_id'])  # message from text input.

    # Send Button
    if st.button("Send Message"):
        if message.strip():
            formatted_message = f"**{st.session_state['username']}:** {message}"  # Message format
            # Save the message to the database
            save_message(st.session_state['room_id'], formatted_message)
            st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)  # Rerun

    st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)  # rerun

if __name__ == "__main__":
    main()
