import streamlit as st
import random
import time

# Room Capacity
MAX_USERS = 50

# List of System Emojis (Extend as desired)
EMOJIS = ["😀", "😂", "😎", "😍", "🤔", "👍", "❤️", "🎉", "🎈", "🎁", "🌟", "🔥", "💯", "✨", "✅", "😊", "👏", "🙌", "🥳"]

def get_random_emoji():
    """Returns a random emoji from the list."""
    return random.choice(EMOJIS)

def display_chat(room_id):
    """Displays the chat interface."""
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Display chat messages
    for message in st.session_state['chat_history']:
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
                    new_message = emoji #Select emoji, and assign it to be new message.
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
            st.session_state['room_id'] = str(time.time())  # Generate unique room ID
            st.success(f"Room created! Share this URL with others. Room ID: {st.session_state['room_id']}")
            st.experimental_rerun()  # Re-run once the room id has been created.

        if join_room:
            st.session_state['room_id'] = join_room  # Set room ID from user input
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
    message = display_chat(st.session_state['room_id']) #message from text input.

    # Send Button
    if st.button("Send Message"):
        if message.strip():
            formatted_message = f"**{st.session_state['username']}:** {message}"  # Message format
            st.session_state['chat_history'].append(formatted_message)  # Append to message
            st.experimental_rerun()#clear textbox

    st.experimental_rerun()  # Simulate real-time updates


if __name__ == "__main__":
    main()
