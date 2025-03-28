import streamlit as st
import random
import time
import sqlite3
import os  # For setting file path
import re #added regex

# Room Capacity
MAX_USERS = 50

# List of System Emojis (Extend as desired)
EMOJIS = ["😀", "😂", "😎", "😍", "🤔", "👍", "❤️", "🎉", "🎈", "🎁", "🌟", "🔥", "💯", "✨", "✅", "😊", "👏", "🙌", "🥳"]

# Database setup
DATABASE_FILE = os.path.join(".", "chat_database.db")  # Database File
# os.path.join - this creates the database file in the same working directory where the script runs from. This is better than a static path because different users can have different paths.


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
    except sqlite3.Error as e: #Added except in case table is not created.
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

    # Room Creation/Joining
    if 'room_id' not in st.session_state:
        st.session_state['room_id'] = None  # Initialize room_id
        st.session_state['username'] = None  # Initialize username

    if not st.session_state['room_id']:
        st.header("Create or Join a Chatroom")

        create_room = st.button("Create New Room")
        join_room = st.text_input("Join Existing Room (Enter Room ID):")

        if create_room:
            roomid = str(time.time())
            safe_room_id = re.sub(r'[^a-zA-Z0-9_]', '', roomid)  # Remove invalid characters.
            st.session_state['room_id'] = safe_room_id  # Generate unique room ID
            st.success(f"Room created! Share this URL with others. Room ID: {st.session_state['room_id']}")
            create_table(st.session_state['room_id'])  # Create table for room.
            st.experimental_rerun()  # Re-run once the room id has been created.

        if join_room:
            safe_join_room = re.sub(r'[^a-zA-Z0-9_]', '',join_room)
            st.session_state['room_id'] = safe_join_room  # Set room ID from user input
            create_table(st.session_state['room_id'])
            st.experimental_rerun()

        return  # Stop execution until room ID is set

    # Username Input
    if not st.session_state['username']:  # Make sure user has joined before setting user name
        username = st.text_input("Enter your username:")
        if username:
            st.session_state['username'] = username  # Set Username
            st.experimental_rerun()
        else:
            st.warning("Please enter a username.")
            return

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
            st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag",False)  # re-run

    st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)  # Constant Re-run to ensure latest messages.


if __name__ == "__main__":
    main()
