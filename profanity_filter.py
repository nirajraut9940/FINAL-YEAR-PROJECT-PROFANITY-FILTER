import tkinter as tk
from tkinter import messagebox, scrolledtext, Menu, ttk
import os
import threading
import pyperclip
import google.generativeai as genai
import transformers
import torch

# Load pre-trained toxic comment classifier (once at the beginning)
tokenizer = transformers.AutoTokenizer.from_pretrained("unitary/toxic-bert")
model = transformers.AutoModelForSequenceClassification.from_pretrained(
    "unitary/toxic-bert"
)

# Gemini API Key (replace with your actual key)
GEMINI_API_KEY = "*****"

# Function to check for harmful content
def classify_content(text, threshold=0.7):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    probabilities = torch.sigmoid(outputs.logits).squeeze().tolist()

    harmful_categories = {
        "toxic": "Toxic",
        "severe_toxic": "Severe Toxic",
        "obscene": "Obscene",
        "threat": "Threat",
        "insult": "Insult",
        "identity_hate": "Identity Hate",
    }

    print(f"Text: {text}")
    print(f"Probabilities: {probabilities}")

    harmful_labels = []
    for label_id, probability in enumerate(probabilities):
        label = model.config.id2label[label_id]
        print(f"Label: {label}, Probability: {probability}")
        if label in harmful_categories and probability > threshold:
            harmful_labels.append(harmful_categories[label])

    return harmful_labels if harmful_labels else ["Safe Content"]

# Function to filter profanity and generate response
def filter_profanity(input_text):
    result = classify_content(input_text)
    if "Safe Content" not in result:
        messagebox.showwarning(
            "Warning",
            f"Harmful content found in the input text. Categories: {', '.join(result)}. It is against ethics to proceed further.",
        )
        return f"Harmful content detected ({', '.join(result)}). Cannot proceed further."
    else:
        os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(input_text)
        return response.text

# Function to handle button click event
def on_submit(event=None):
    input_text = text_input.get("1.0", "end-1c")
    if input_text.strip() == "":
        messagebox.showerror("Error", "Please enter some text")
        return

    def process_input():
        text_input.config(state=tk.DISABLED)
        final_text = filter_profanity(input_text)
        result_text.config(state=tk.NORMAL)
        # Insert at the beginning instead of appending at the end
        result_text.insert("1.0", f"Chatbot: {final_text}\n\n", "bot")
        result_text.insert("1.0", f"User: {input_text}\n", "user")
        result_text.config(state=tk.DISABLED)
        text_input.delete("1.0", "end")
        text_input.config(state=tk.NORMAL)
        progress_bar.stop()
        progress_bar.grid_remove()

    threading.Thread(target=process_input).start()
    progress_bar.grid(row=2, column=0, columnspan=2, pady=10)

# Function to handle "New" menu option
def new_chat():
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", "end")
    result_text.config(state=tk.DISABLED)
    text_input.delete("1.0", "end")

# Function to handle "Delete" button click event
def delete_input():
    text_input.delete("1.0", "end")

# Function to copy the chatbot's response to clipboard
def copy_output():
    result_text_content = result_text.get("1.0", "end-1c")
    pyperclip.copy(result_text_content)
    messagebox.showinfo("Copied", "Output copied to clipboard")

# Function to change theme
def change_theme(theme):
    if theme == "Light":
        root.configure(bg="#e0e0e0")
        input_frame.configure(bg="#e0e0e0")
        result_frame.configure(bg="#e0e0e0")
        button_frame.configure(bg="#e0e0e0")
        title_label.configure(bg="#4CAF50", fg="white")
        input_label.configure(bg="#e0e0e0", fg="#000000")
        result_label.configure(bg="#e0e0e0", fg="#000000")
        text_input.configure(bg="#ffffff", fg="#000000")
        result_text.configure(bg="#f7f7f7", fg="#000000")
    elif theme == "Dark":
        root.configure(bg="#2e2e2e")
        input_frame.configure(bg="#2e2e2e")
        result_frame.configure(bg="#2e2e2e")
        button_frame.configure(bg="#2e2e2e")
        title_label.configure(bg="#1e1e1e", fg="white")
        input_label.configure(bg="#2e2e2e", fg="#ffffff")
        result_label.configure(bg="#2e2e2e", fg="#ffffff")
        text_input.configure(bg="#3e3e3e", fg="#ffffff")
        result_text.configure(bg="#4e4e4e", fg="#ffffff")

# Function to display information about AI profanity filter
def about_ai():
    messagebox.showinfo(
        "About AI",
        "The AI profanity filter implemented in this chatbot detects and filters out various forms of profanity, including sexual explicit content, hate speech, harmful language, and abusive language. It utilizes a generative AI model to provide responses while ensuring that the conversation remains respectful and appropriate.\n\nFor more information about the profanity filter and its implementation, please refer to the documentation or contact the developer.",
    )

# Signup functionality
def signup():
    def register():
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_entry.get()
        # Check if any field is empty
        if not all([username, password, confirm_password]):
            messagebox.showerror("Error", "All fields are required")
            return

        # Check if passwords match
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        # Save the signup details to a file
        with open("user_signup_details.txt", "a") as file:
            file.write(f"Username: {username}, Password: {password}\n")

        messagebox.showinfo("Success", "Registration successful!")
        signup_window.destroy()

    signup_window = tk.Toplevel(root)
    signup_window.title("Sign Up")
    signup_window.geometry("300x200")

    signup_frame = tk.Frame(signup_window)
    signup_frame.pack(padx=10, pady=10)

    username_label = tk.Label(signup_frame, text="Username:")
    username_label.grid(row=0, column=0, sticky="e")

    username_entry = tk.Entry(signup_frame)
    username_entry.grid(row=0, column=1)

    password_label = tk.Label(signup_frame, text="Password:")
    password_label.grid(row=1, column=0, sticky="e")

    password_entry = tk.Entry(signup_frame, show="*")
    password_entry.grid(row=1, column=1)

    confirm_label = tk.Label(signup_frame, text="Confirm Password:")
    confirm_label.grid(row=2, column=0, sticky="e")

    confirm_entry = tk.Entry(signup_frame, show="*")
    confirm_entry.grid(row=2, column=1)

    signup_btn = tk.Button(signup_frame, text="Register", command=register)
    signup_btn.grid(row=3, columnspan=2, pady=10)

# GUI setup
root = tk.Tk()
root.title("Chatbot: Profanity Detection Generative AI")
root.geometry("1000x700")
root.configure(bg="#e0e0e0")

# Style configurations
title_font = ("Helvetica", 18, "bold")
label_font = ("Helvetica", 12, "bold")
button_font = ("Helvetica", 12)
text_font = ("Helvetica", 12)

# Navigation Bar
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_chat)
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

theme_menu = tk.Menu(menu_bar, tearoff=0)
theme_menu.add_command(label="Light", command=lambda: change_theme("Light"))
theme_menu.add_command(label="Dark", command=lambda: change_theme("Dark"))
menu_bar.add_cascade(label="Themes", menu=theme_menu)

about_menu = tk.Menu(menu_bar, tearoff=0)
about_menu.add_command(label="About AI", command=about_ai)
menu_bar.add_cascade(label="About", menu=about_menu)

signup_menu = tk.Menu(menu_bar, tearoff=0)
signup_menu.add_command(label="Sign Up", command=signup)
menu_bar.add_cascade(label="Signup", menu=signup_menu)

root.config(menu=menu_bar)

# Title
title_label = tk.Label(
    root,
    text="Chatbot: Profanity Detection Generative AI",
    font=title_font,
    bg="#4CAF50",
    fg="white",
    pady=10,
)
title_label.pack(fill=tk.X)

# Input Frame
input_frame = tk.Frame(root, bg="#e0e0e0", padx=10, pady=10)
input_frame.pack(fill=tk.X)

input_label = tk.Label(input_frame, text="Enter your text:", font=label_font, bg="#e0e0e0", fg="#000000")
input_label.grid(row=0, column=0, sticky="w")

text_input = scrolledtext.ScrolledText(input_frame, height=6, font=text_font)
text_input.grid(row=1, column=0, columnspan=2, pady=5, sticky="we")

submit_button = tk.Button(input_frame, text="Submit", font=button_font, command=on_submit)
submit_button.grid(row=2, column=0, pady=10, sticky="e")

delete_button = tk.Button(input_frame, text="Delete", font=button_font, command=delete_input)
delete_button.grid(row=2, column=1, pady=10, sticky="w")

progress_bar = ttk.Progressbar(input_frame, mode="indeterminate")

# Result Frame
result_frame = tk.Frame(root, bg="#e0e0e0", padx=10, pady=10)
result_frame.pack(fill=tk.BOTH, expand=True)

result_label = tk.Label(result_frame, text="Chatbot Response:", font=label_font, bg="#e0e0e0", fg="#000000")
result_label.grid(row=0, column=0, sticky="w")

result_text = scrolledtext.ScrolledText(result_frame, height=15, font=text_font, state=tk.DISABLED)
result_text.grid(row=1, column=0, pady=5, sticky="we")

# Button Frame
button_frame = tk.Frame(root, bg="#e0e0e0", pady=10)
button_frame.pack(fill=tk.X)

copy_button = tk.Button(button_frame, text="Copy Output", font=button_font, command=copy_output)
copy_button.grid(row=0, column=0, padx=10)

# Text tags for coloring user and bot text
result_text.tag_config("user", foreground="blue")
result_text.tag_config("bot", foreground="green")

# Bind the Enter key to the submit function
root.bind("<Return>", on_submit)

# Run the GUI main loop
root.mainloop()


