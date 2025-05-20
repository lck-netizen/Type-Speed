import tkinter as tk
from tkinter import ttk
import time
import random
from datetime import datetime
import winsound  # For sound feedback (Windows)

# Sentence pools for different difficulty levels
sentences = {
    "Easy": [
        "The sun shines brightly.",
        "Cats chase playful mice.",
        "Dogs wag happy tails.",
        "Birds chirp sweet songs.",
        "Fish swim in streams.",
        "Kids draw colorful pictures.",
        "Trees sway in breezes.",
        "Stars twinkle at night.",
        "Rain falls on roofs.",
        "Flowers bloom in spring.",
        "Cars zoom on roads.",
        "Bees buzz around hives.",
        "Kites soar in skies.",
        "Boats sail on lakes.",
        "Ants march in rows."
    ],
    "Medium": [
        "The quick brown fox jumps over the lazy dog.",
        "Typing speed tests are fun and useful.",
        "Python is a powerful and easy to learn language.",
        "Consistency is the key to mastering coding.",
        "Debugging is twice as hard as writing code.",
        "The moon glows softly in the night sky.",
        "Books open doors to new worlds of knowledge.",
        "Coffee fuels early morning coding sessions.",
        "Teamwork makes complex projects run smoothly.",
        "Clouds drift lazily across the blue sky.",
        "Music inspires creativity during long workdays.",
        "Nature offers peace after busy schedules.",
        "Algorithms solve problems with elegant precision.",
        "Stars align in patterns that guide sailors.",
        "Laughter brightens even the toughest days.",
        "Technology shapes the future of our world.",
        "Learning new skills boosts confidence daily.",
        "Sunsets paint the horizon with vivid colors."
    ],
    "Hard": [
        "The intricate algorithms of machine learning require meticulous tuning.",
        "Quantum computing promises to revolutionize cryptographic security.",
        "Asynchronous programming enhances application performance significantly.",
        "Distributed systems demand robust fault tolerance mechanisms.",
        "Functional programming paradigms emphasize immutability and purity.",
        "Neural networks simulate complex patterns in vast datasets.",
        "Cryptographic protocols safeguard sensitive information against breaches.",
        "Parallel processing optimizes computational efficiency in modern systems.",
        "Genetic algorithms mimic natural selection to solve optimization problems.",
        "Blockchain technology ensures decentralized and transparent transactions.",
        "Augmented reality blends digital content with physical environments.",
        "Graph theory underpins efficient network routing and analysis.",
        "Dynamic programming breaks complex problems into manageable subproblems.",
        "Compilers transform high-level code into machine-readable instructions.",
        "Quantum entanglement challenges our understanding of physical reality.",
        "Big data analytics uncover hidden trends in massive datasets.",
        "Microservices architecture promotes scalability in enterprise applications."
    ]
}

HISTORY_FILE = "typing_history.txt"

class TypingSpeedTest:
    def __init__(self, root):
        self.root = root
        self.root.title("TypeRush")
        self.root.geometry("850x650")
        self.root.config(bg="#ffffff")

        self.difficulty = "Medium"  # Default difficulty
        self.sentence = random.choice(sentences[self.difficulty])
        self.target_sentences = [self.sentence]  # Track all target sentences
        self.total_typed_text = ""  # Track all typed text
        self.start_time = None
        self.test_started = False
        self.timer_running = False
        self.paused = False
        self.time_limit = 60  # Default time limit
        self.time_elapsed = 0  # Track elapsed time for pause/resume

        # Title
        tk.Label(root, text="TypeRush check your speed", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333").pack(pady=10)

        # Difficulty Selection
        tk.Label(root, text="Select Difficulty", font=("Arial", 14), bg="#ffffff", fg="black").pack()
        self.difficulty_var = tk.StringVar(value=self.difficulty)
        self.difficulty_menu = tk.OptionMenu(root, self.difficulty_var, *sentences.keys(), command=self.update_difficulty)
        self.difficulty_menu.pack(pady=5)

        # Time Limit Selection
        tk.Label(root, text="Select Time Limit", font=("Arial", 14), bg="#ffffff", fg="black").pack()
        self.time_options = ["30s", "60s", "120s"]
        self.time_var = tk.StringVar(value=self.time_options[1])
        self.time_menu = tk.OptionMenu(root, self.time_var, *self.time_options)
        self.time_menu.pack(pady=5)

        # Start button
        self.start_button = tk.Button(root, text="Start Test", command=self.start_test, bg="#4CAF50", fg="white", font=("Arial", 14), width=12)
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress_label = tk.Label(root, text="Time Remaining", font=("Arial", 12), bg="#ffffff", fg="black")
        self.progress_label.pack()
        self.progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
        self.progress_bar.pack(pady=5)

        # Shadow display area
        self.shadow_text = tk.Text(root, height=3, width=100, font=("Courier New", 14), wrap="word", bg="#f5f5f5", bd=0)
        self.shadow_text.pack(pady=10)
        self.shadow_text.config(state='disabled')

        # Typing input
        self.input_text = tk.Text(root, height=5, width=100, font=("Courier New", 14), wrap="word", bd=2, relief="groove")
        self.input_text.pack()
        self.input_text.bind("<KeyRelease>", self.on_key_release)

        # Timer and Character Count Labels
        self.info_frame = tk.Frame(root, bg="#ffffff")
        self.info_frame.pack(pady=10)
        self.timer_label = tk.Label(self.info_frame, text=f"Time: {self.time_limit}s", font=("Arial", 14), bg="#ffffff", fg="black")
        self.timer_label.grid(row=0, column=0, padx=20)
        self.char_count_label = tk.Label(self.info_frame, text="Characters: 0", font=("Arial", 14), bg="#ffffff", fg="black")
        self.char_count_label.grid(row=0, column=1, padx=20)

        # Result
        self.result_label = tk.Label(root, text="", font=("Arial", 14), bg="#ffffff", fg="green")
        self.result_label.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(root, bg="#ffffff")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Reset", command=self.reset_test, bg="#f44336", fg="white", font=("Arial", 12), width=12).grid(row=0, column=0, padx=10)
        self.pause_button = tk.Button(btn_frame, text="Pause", command=self.toggle_pause, bg="#FFC107", fg="white", font=("Arial", 12), width=12)
        self.pause_button.grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="View History", command=self.view_history, bg="#2196F3", fg="white", font=("Arial", 12), width=12).grid(row=0, column=2, padx=10)

        self.update_shadow()  # Show initial shadow

    def update_difficulty(self, difficulty):
        """Update the sentence pool based on selected difficulty"""
        self.difficulty = difficulty
        self.sentence = random.choice(sentences[self.difficulty])
        self.target_sentences = [self.sentence]
        self.total_typed_text = ""
        self.input_text.delete("1.0", "end")
        self.update_shadow()

    def start_test(self):
        """Start the typing test with the selected time limit"""
        if self.paused:
            self.toggle_pause()  # Resume if paused
            return

        self.time_limit = int(self.time_var.get().replace("s", ""))
        self.sentence = random.choice(sentences[self.difficulty])
        self.target_sentences = [self.sentence]
        self.total_typed_text = ""
        self.test_started = False
        self.start_time = time.time()
        self.time_elapsed = 0
        self.timer_running = True
        self.paused = False
        self.input_text.delete("1.0", "end")
        self.result_label.config(text="")
        self.timer_label.config(text=f"Time: {self.time_limit}s")
        self.char_count_label.config(text="Characters: 0")
        self.progress_bar["maximum"] = self.time_limit
        self.progress_bar["value"] = self.time_limit
        self.update_shadow()
        self.input_text.focus_set()
        self.input_text.config(state='normal')
        self.update_timer()

    def update_timer(self):
        """Update the timer, progress bar, and show remaining time"""
        if self.timer_running and not self.paused:
            elapsed_time = int(time.time() - self.start_time) + self.time_elapsed
            remaining_time = self.time_limit - elapsed_time
            if remaining_time <= 0:
                remaining_time = 0
                self.end_test()
            self.timer_label.config(text=f"Time: {remaining_time}s")
            self.progress_bar["value"] = remaining_time
            if remaining_time > 0:
                self.root.after(1000, self.update_timer)

    def toggle_pause(self):
        """Pause or resume the test"""
        if not self.test_started:
            return

        if self.paused:
            self.paused = False
            self.timer_running = True
            self.start_time = time.time()
            self.pause_button.config(text="Pause", bg="#FFC107")
            self.input_text.config(state='normal')
            self.update_timer()
        else:
            self.paused = True
            self.timer_running = False
            self.time_elapsed += int(time.time() - self.start_time)
            self.pause_button.config(text="Resume", bg="#FF5722")
            self.input_text.config(state='disabled')
            winsound.Beep(500, 200)  # Short beep for pause

    def on_key_release(self, event):
        """Handle typing events and start the timer when the user begins typing"""
        if self.paused or not self.timer_running:
            return

        if not self.test_started:
            self.test_started = True

        typed = self.input_text.get("1.0", "end-1c")
        self.update_shadow()
        self.char_count_label.config(text=f"Characters: {len(self.total_typed_text) + len(typed)}")

        # Auto advance if sentence is completed correctly
        if typed.strip() == self.sentence:
            self.total_typed_text += typed + " "
            self.sentence = random.choice([s for s in sentences[self.difficulty] if s != self.sentence])
            self.target_sentences.append(self.sentence)
            self.input_text.delete("1.0", "end")
            self.update_shadow()
            winsound.Beep(1000, 100)  # High-pitched beep for sentence completion

    def update_shadow(self):
        """Update the shadow area to reflect the typed text and remaining text"""
        typed = self.input_text.get("1.0", "end-1c")
        self.shadow_text.config(state='normal')
        self.shadow_text.delete("1.0", "end")

        self.shadow_text.tag_config("correct", foreground="green")
        self.shadow_text.tag_config("wrong", foreground="red")
        self.shadow_text.tag_config("remaining", foreground="gray")

        for i, char in enumerate(self.sentence):
            if i < len(typed):
                if typed[i] == char:
                    self.shadow_text.insert("end", char, "correct")
                else:
                    self.shadow_text.insert("end", char, "wrong")
            else:
                self.shadow_text.insert("end", char, "remaining")

        self.shadow_text.config(state='disabled')

    def calculate_results(self):
        """Calculate and display the results based on total typing speed and accuracy"""
        if not self.test_started:
            self.result_label.config(text="You haven't started typing yet!")
            return

        current_typed = self.input_text.get("1.0", "end-1c").strip()
        if current_typed:
            self.total_typed_text += current_typed + " "

        time_taken = self.time_limit
        word_count = len(self.total_typed_text.split())
        wpm = round((word_count / time_taken) * 60) if time_taken > 0 else 0

        target_text = " ".join(self.target_sentences).strip()
        typed_text = self.total_typed_text.strip()
        correct_chars = sum(1 for a, b in zip(typed_text, target_text) if a == b)
        total_chars = max(len(target_text), len(typed_text))
        accuracy = round((correct_chars / total_chars) * 100, 2) if total_chars > 0 else 0

        result = f"Time: {time_taken}s | WPM: {wpm} | Accuracy: {accuracy}% | Difficulty: {self.difficulty}"
        self.result_label.config(text=result)

        self.save_history(wpm, accuracy, time_taken, self.difficulty)

    def save_history(self, wpm, accuracy, time_taken, difficulty):
        """Save the results to the history file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_line = f"[{timestamp}] WPM: {wpm} | Accuracy: {accuracy}% | Time: {time_taken}s | Difficulty: {difficulty}\n"
        with open(HISTORY_FILE, "a") as file:
            file.write(history_line)

    def view_history(self):
        """Display the history of previous tests"""
        try:
            with open(HISTORY_FILE, "r") as file:
                history_data = file.read()
        except FileNotFoundError:
            history_data = "No history yet."

        history_window = tk.Toplevel(self.root)
        history_window.title("TypeRush History")
        history_window.geometry("600x400")
        history_window.config(bg="#fefefe")

        tk.Label(history_window, text="Typing History", font=("Arial", 16, "bold"), bg="#fefefe").pack(pady=10)

        history_text = tk.Text(history_window, wrap="word", font=("Courier New", 12), bg="#f2f2f2")
        history_text.insert("1.0", history_data)
        history_text.config(state="disabled")
        history_text.pack(expand=True, fill="both", padx=10, pady=10)

    def reset_test(self):
        """Reset the test, allowing the user to start again"""
        self.sentence = random.choice(sentences[self.difficulty])
        self.target_sentences = [self.sentence]
        self.total_typed_text = ""
        self.input_text.delete("1.0", "end")
        self.result_label.config(text="")
        self.timer_label.config(text=f"Time: {self.time_limit}s")
        self.char_count_label.config(text="Characters: 0")
        self.progress_bar["value"] = self.time_limit
        self.test_started = False
        self.start_time = None
        self.time_elapsed = 0
        self.timer_running = False
        self.paused = False
        self.pause_button.config(text="Pause", bg="#FFC107")
        self.input_text.config(state='normal')
        self.update_shadow()
        self.input_text.focus_set()

    def end_test(self):
        """End the test and display the results"""
        self.timer_running = False
        self.paused = False
        self.input_text.config(state='disabled')
        self.calculate_results()
        self.result_label.config(text=self.result_label.cget("text") + "\nTime's up! Test completed.")
        self.pause_button.config(text="Pause", bg="#FFC107", state="disabled")
        winsound.Beep(800, 300)  # Beep for test completion

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTest(root)
    root.mainloop()