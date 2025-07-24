import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF
import os
import pyttsx3
import socket
from gtts import gTTS
from deep_translator import GoogleTranslator

class PDFToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📘 PDF to Audiobook Converter")
        self.root.geometry("540x550")
        self.root.configure(bg="#f0f4ff")
        self.filename = ""
        self.audio_file = ""
        self.engine = pyttsx3.init()

        self.language_dict = {
            "English": "en",
            "Hindi": "hi",
            "Telugu": "te",
            "Tamil": "ta",
            "Bengali": "bn",
            "Gujarati": "gu",
            "Kannada": "kn",
            "Malayalam": "ml",
            "Marathi": "mr",
            "Punjabi": "pa",
            "Urdu": "ur",
            "Japanese": "ja",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it"
        }

        tk.Label(root, text="📖 PDF to Audiobook", font=("Helvetica", 18, "bold"), fg="#003366", bg="#f0f4ff").pack(pady=10)

        frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Button(frame, text="📁 Upload PDF", font=("Arial", 12), bg="#4caf50", fg="white", command=self.load_pdf).pack(pady=10)

        tk.Label(frame, text="🌐 Translate to Language:", bg="#ffffff", font=("Arial", 11)).pack()
        self.lang_var = tk.StringVar(value="English")
        lang_menu = ttk.Combobox(frame, textvariable=self.lang_var, values=list(self.language_dict.keys()), state="readonly")
        lang_menu.pack(pady=5)

        tk.Label(frame, text="💾 Output MP3 File Name:", bg="#ffffff", font=("Arial", 11)).pack(pady=5)
        self.name_entry = tk.Entry(frame, font=("Arial", 11))
        self.name_entry.insert(0, "output")
        self.name_entry.pack()

        tk.Label(frame, text="🎚️ Voice Speed (0.5 - 2.0):", bg="#ffffff", font=("Arial", 11)).pack(pady=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        tk.Scale(frame, from_=0.5, to=2.0, resolution=0.1, orient="horizontal", variable=self.speed_var, bg="#e0e0e0").pack()

        tk.Button(frame, text="🔊 Read Aloud (Offline)", font=("Arial", 12), bg="#2196f3", fg="white", command=self.speak_text).pack(pady=10)
        tk.Button(frame, text="💿 Save as MP3 (Online)", font=("Arial", 12), bg="#ff9800", fg="white", command=self.save_as_mp3).pack(pady=5)
        tk.Button(frame, text="⛔ Stop Speaking", font=("Arial", 12), bg="#f44336", fg="white", command=self.stop_speaking).pack(pady=5)

        tk.Label(root, text="Created with ❤️ using Python + Tkinter", font=("Arial", 9), fg="#666666", bg="#f0f4ff").pack(side="bottom", pady=10)

    def load_pdf(self):
        self.filename = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.filename:
            messagebox.showinfo("Loaded", os.path.basename(self.filename))

    def extract_text(self):
        if not self.filename:
            messagebox.showwarning("No File", "Please upload a PDF first.")
            return ""
        try:
            text = ""
            with fitz.open(self.filename) as doc:
                for page in doc:
                    text += page.get_text()
            if not text.strip():
                messagebox.showwarning("Empty PDF", "No text found in PDF.")
            return text.strip()
        except Exception as e:
            messagebox.showerror("Error Reading PDF", f"Failed to read PDF: {str(e)}")
            return ""

    def is_online(self):
        try:
            socket.create_connection(("www.google.com", 80), timeout=3)
            return True
        except:
            return False

    def translate_text(self, text, lang_code):
        if lang_code == "en":
            return text
        try:
            translated_chunks = []
            sentences = text.split(". ")
            for sentence in sentences:
                if sentence.strip():
                    translated = GoogleTranslator(source='auto', target=lang_code).translate(sentence)
                    translated_chunks.append(translated)
            return ". ".join(translated_chunks)
        except Exception as e:
            messagebox.showerror("Translation Error", f"Could not translate text: {str(e)}")
            return ""

    def speak_text(self):
        text = self.extract_text()
        if not text:
            return
        lang_name = self.lang_var.get()
        lang_code = self.language_dict.get(lang_name)
        if lang_code not in self.language_dict.values():
            messagebox.showerror("Unsupported Language", f"Language '{lang_name}' is not supported.")
            return
        translated_text = self.translate_text(text, lang_code)
        if not translated_text:
            return
        try:
            self.engine.setProperty('rate', int(200 * self.speed_var.get()))
            self.engine.say(translated_text)
            self.engine.runAndWait()
        except Exception as e:
            messagebox.showerror("Speech Error", f"Failed to speak text: {str(e)}")

    def stop_speaking(self):
        try:
            self.engine.stop()
        except:
            pass

    def save_as_mp3(self):
        if not self.is_online():
            messagebox.showwarning("Offline", "Internet connection required to save MP3 using gTTS.")
            return
        text = self.extract_text()
        if not text:
            return
        lang_name = self.lang_var.get()
        lang_code = self.language_dict.get(lang_name)
        if lang_code not in self.language_dict.values():
            messagebox.showerror("Unsupported Language", f"Language '{lang_name}' is not supported.")
            return
        translated_text = self.translate_text(text, lang_code)
        if not translated_text:
            return
        try:
            filename = self.name_entry.get().strip() or "output"
            self.audio_file = f"{filename}.mp3"
            if os.path.exists(self.audio_file):
                overwrite = messagebox.askyesno("File Exists", f"{self.audio_file} already exists. Overwrite?")
                if not overwrite:
                    return
            tts = gTTS(text=translated_text, lang=lang_code, slow=False)
            tts.save(self.audio_file)
            messagebox.showinfo("Saved", f"Audio saved as {self.audio_file}")
        except Exception as e:
            messagebox.showerror("gTTS Error", f"Failed to save MP3: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToSpeechApp(root)
    root.mainloop()