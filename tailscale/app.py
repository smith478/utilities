import streamlit as st

st.title("Simple Text Saver")

# Create a text area for the user to type text
user_text = st.text_area("Enter your text here:")

# Button to save the text
if st.button("Save Text"):
    # Specify the file name; adjust path as needed
    file_name = "saved_text.txt"
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(user_text)
        st.success(f"Text saved successfully to {file_name}!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
