import openai
import tkinter as tk
from tkinter import Entry, Label, Button, StringVar, Text, Scrollbar
import sqlite3

class AIResponseGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key


    def generate_response(self, prompt, engine="text-davinci-003", max_tokens=500):
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                max_tokens=max_tokens,
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f'An error occurred: {e}')
            return None


    def save_to_file(self, prompt, response):
        with open('user_responses.txt', 'a') as file:
            file.write(f'User Prompt: {prompt}\nAI Response: {response}\n\n')


    def save_to_database(self, prompt, response):
        # Create or connect to the SQLite database
        conn = sqlite3.connect('chatgpt_responses.db')
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_prompt TEXT,
                gpt_response TEXT
            )
        ''')

        # Insert the user prompt and GPT response into the table
        cursor.execute('INSERT INTO responses (user_prompt, gpt_response) VALUES (?, ?)', (prompt, response))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def view_database(self):
        # Connect to the database
        conn = sqlite3.connect('chatgpt_responses.db')
        cursor = conn.cursor()

        # Execute a SELECT query to fetch all records from the 'responses' table
        cursor.execute('SELECT * FROM responses')
        records = cursor.fetchall()

        # Close the connection
        conn.close()

        return records
    

    def build_prompt(prompt):
        modified_prompt = f'Tell me more about {prompt}. Label the three major ideas with a number followed by a period'
        return modified_prompt
    

class ChatGPTGUI:
    def __init__(self, root, ai_generator):
        self.root = root
        self.ai_generator = ai_generator
        self.gpt_response = tk.StringVar()
        self.responses = []

        # Create the scrollbar before creating other widgets
        self.scrollbar = tk.Scrollbar(self.root)
        
        self.create_widgets()


    def create_widgets(self):
        # Canvas widget for scrolling
        self.canvas = tk.Canvas(self.root, yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky='nsew', columnspan=3)

        # Attach scrollbar to canvas
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Frame inside the canvas
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        # Entry box for user prompt
        self.entry_prompt = tk.Entry(self.frame, width=50)
        self.entry_prompt.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Button to generate response
        self.button_generate = tk.Button(self.frame, text="Generate Response", command=self.on_generate)
        self.button_generate.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        # Label to display response
        self.label_response = tk.Label(self.frame, textvariable=self.gpt_response, wraplength=500)
        self.label_response.grid(row=2, column=0, padx=10, pady=30, columnspan=2)

        # Button to display database records
        self.display_button = tk.Button(self.frame, text="Display chat", command=self.display_chat)
        self.display_button.grid(row=3, column=0, padx=10, pady=10, columnspan=2)

        # Text widget for displaying database records
        self.text_display = tk.Text(self.frame, width=50, height=10)
        self.text_display.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

        # Scrollbar for the entire window
        self.scrollbar.grid(row=0, column=3, rowspan=5, sticky='ns')

        # Configure the canvas and the root window for scrolling
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Configure row and column weights for resizing
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)


    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


    def display_chat(self):
        # Call the view_database function from AIResponseGenerator
        records = self.ai_generator.view_database()

        # Display the records in the Text widget
        self.text_display.delete(1.0, tk.END)  # Clear previous content
        for record in records:
            self.text_display.insert(tk.END, f"{record}\n")





    def on_generate(self):
        prompt = ai_generator.build_prompt(self.entry_prompt.get())

        response_text = self.ai_generator.generate_response(prompt)

        if response_text:
            self.gpt_response.set(response_text)
            self.ai_generator.save_to_file(prompt, response_text)

            # Use the response as input for the next prompt
            self.entry_prompt.delete(0, tk.END)  # Clear the entry box
            self.deeper_button = Button(self.root, text='Go in depth', command=self.go_deeper)
            self.deeper_button.grid(row=1, column=2, padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("ChatGPT GUI")

    ai_key = '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'
    
    ai_generator = AIResponseGenerator(ai_key)

    chatgpt_gui = ChatGPTGUI(root, ai_generator)

    root.mainloop()

