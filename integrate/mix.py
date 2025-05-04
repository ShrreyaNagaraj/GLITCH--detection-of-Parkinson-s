import streamlit as st
import subprocess
import sys
import multiprocessing

# Function to launch your Tkinter app
def launch_tkinter_app():
    st.text("Launching Tkinter app...")
    try:
        # Try to launch the Tkinter app
        subprocess.Popen([sys.executable, "typepress.py"])
        st.success("Tkinter app launched successfully!")
    except Exception as e:
        st.error(f"Error launching Tkinter app: {e}")

# Function for the Spiral Streamlit app
def launch_spiral_app():
    st.text("Launching Spiral app...")
    try:
        # Launch a separate Streamlit app for the Spiral test
        subprocess.Popen(["streamlit", "run", "spiral.py"])
        st.success("Spiral app launched successfully!")
    except Exception as e:
        st.error(f"Error launching Spiral app: {e}")

# Function for the Voice functionality (to be implemented)
def launch_voice_app():
    st.write("Voice functionality is not implemented yet.")

# Streamlit Interface
def main():
    st.title("Choose a Test")

    # Create the buttons
    if st.button("Typing Test"):
        # Launch the Tkinter app in a separate process using multiprocessing
        p = multiprocessing.Process(target=launch_tkinter_app)
        p.start()

    if st.button("Spiral Test"):
        launch_spiral_app()

    if st.button("Voice Test"):
        launch_voice_app()

if __name__ == "__main__":
    main()
