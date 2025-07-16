import subprocess
import os
import time
import sys
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText


def typewriter_effect_gui(text_widget, text, speed=0.001):
    text_widget.config(state=tk.NORMAL)
    for char in text:
        text_widget.insert(tk.END, char)
        text_widget.see(tk.END)
        text_widget.update_idletasks()
        time.sleep(speed)
    text_widget.config(state=tk.DISABLED)


def thinking_animation_gui(label):
    thinking = True
    start_time = time.time()
    spinner_frames = ["|", "/", "-", "\\"]

    def animate():
        i = 0
        while thinking:
            label.config(text=f"thinking {spinner_frames[i % len(spinner_frames)]}")
            label.update_idletasks()
            time.sleep(0.1)
            i += 1

    thread = threading.Thread(target=animate)
    thread.daemon = True
    thread.start()

    def stop():
        nonlocal thinking
        thinking = False
        elapsed = time.time() - start_time
        label.config(text=f"thought for {elapsed:.1f} seconds")

    return stop


def ensure_ollama_running():
    try:
        subprocess.run("ollama serve", shell=True, timeout=1, capture_output=True)
    except:
        pass


def get_ollama_response(user_input, label):
    try:
        stop_thinking = thinking_animation_gui(label)
        prompt = f"{user_input}\n\nPlease keep your response brief and concise."

        result = subprocess.run(
            ["ollama", "run", "llama3.2:1b", prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        stop_thinking()

        if result.returncode == 0 and result.stdout.strip():
            response = result.stdout.strip()
            if len(response) > 5:
                return response
        return "I'm having trouble connecting to the AI. Try asking again!"

    except Exception as e:
        stop_thinking()
        return f"Error: {str(e)}"


def show_helios_titlescreen(root, on_complete):
    # Title screen is 80% size of main window
    title_geometry = "480x320+440+240"  # 80% of 600x400, centered accordingly
    main_geometry = "600x400+400+200"   # Full size main window
    
    # Set up main window geometry but keep it hidden
    root.geometry(main_geometry)
    root.configure(bg="#0a0a0a")
    root.update_idletasks()
    root.withdraw()

    title_window = tk.Toplevel(root)
    title_window.overrideredirect(True)
    title_window.configure(bg="#0a0a0a")
    title_window.geometry(title_geometry)  # Smaller title screen
    title_window.attributes("-alpha", 0.0)

    label = tk.Label(title_window, text="☀ HELIOS ☀", fg="#00f5d4", bg="#0a0a0a", font=("Consolas", 48, "bold"))
    label.pack(expand=True)

    def fade_in(step=0):
        alpha = step / 20
        if alpha <= 1.0:
            title_window.attributes("-alpha", alpha)
            root.after(50, lambda: fade_in(step + 1))
        else:
            # Stay visible for 3 seconds before showing main window
            root.after(3000, show_main_window)

    def show_main_window():
        # Set up main window with full size geometry BEFORE showing it
        root.geometry(main_geometry)  # Full size main window
        root.title("HELIOS Assistant")
        root.configure(bg="#0a0a0a")
        root.deiconify()  # Show the main window
        root.after(100, lambda: fade_out(20))  # Small delay then start fade out

    def fade_out(step):
        alpha = step / 20
        if alpha >= 0.0:
            title_window.attributes("-alpha", alpha)
            root.after(50, lambda: fade_out(step - 1))
        else:
            title_window.destroy()
            root.lift()
            on_complete()

    fade_in()



def main():
    ensure_ollama_running()

    root = tk.Tk()
    root.withdraw()  # Hide main window initially

    def launch_main_ui():
        # Show loading bar while UI elements are being set up
        loading_label = tk.Label(root, text="Loading HELIOS...", bg="#0a0a0a", fg="#00f5d4", font=("Consolas", 12))
        loading_label.pack(expand=True)
        
        # Progress bar
        progress_frame = tk.Frame(root, bg="#0a0a0a")
        progress_frame.pack(pady=10)
        
        progress_bg = tk.Frame(progress_frame, bg="#1a1a1a", width=300, height=10)
        progress_bg.pack()
        
        progress_fill = tk.Frame(progress_bg, bg="#00f5d4", height=10)
        progress_fill.place(x=0, y=0, width=0)
        
        def animate_loading(step=0):
            if step <= 100:
                progress_fill.place(x=0, y=0, width=int(step * 3))  # 300px total
                root.after(20, lambda: animate_loading(step + 2))
            else:
                # Remove loading elements and set up main UI
                loading_label.destroy()
                progress_frame.destroy()
                setup_main_interface()
        
        animate_loading()
        
    def setup_main_interface():
        # UI setup - all the main interface elements
        output_display = ScrolledText(root, width=60, height=15, state=tk.DISABLED, bg="#0d1b2a", fg="#00f5d4", insertbackground="#00f5d4", font=("Consolas", 9), wrap=tk.WORD)
        output_display.pack(padx=8, pady=(8, 4), fill=tk.BOTH, expand=True)
        
        # Add initial greeting message with typewriter effect
        output_display.config(state=tk.NORMAL)
        output_display.insert(tk.END, "HELIOS: ")
        output_display.config(state=tk.DISABLED)
        
        # Use typewriter effect for greeting
        greeting = "Hello, I am Helios, a local chat assistant. How may I help you today?"
        typewriter_effect_gui(output_display, greeting, speed=0.02)
        
        output_display.config(state=tk.NORMAL)
        output_display.insert(tk.END, "\n\n")
        output_display.config(state=tk.DISABLED)

        status_label = tk.Label(root, text="Ready", bg="#0a0a0a", fg="#00f5d4", font=("Consolas", 9))
        status_label.pack(pady=3)

        input_frame = tk.Frame(root, bg="#0a0a0a")
        input_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        input_field = tk.Entry(input_frame, width=50, bg="#1a1a1a", fg="#ffffff", insertbackground="#00f5d4", relief=tk.FLAT, font=("Consolas", 9))
        input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        def on_submit():
            user_input = input_field.get().strip()
            if not user_input:
                return
            if user_input.lower() in ['exit', 'quit', 'q']:
                root.destroy()
                return
            
            # Show user input in output
            output_display.config(state=tk.NORMAL)
            output_display.insert(tk.END, f"You: {user_input}\n\n")
            output_display.config(state=tk.DISABLED)
            output_display.see(tk.END)
            
            input_field.delete(0, tk.END)
            threading.Thread(target=process_input, args=(user_input, output_display, status_label)).start()

        def process_input(user_input, text_widget, label):
            response = get_ollama_response(user_input, label)
            text_widget.config(state=tk.NORMAL)
            text_widget.insert(tk.END, "HELIOS: ")
            text_widget.config(state=tk.DISABLED)
            text_widget.see(tk.END)
            
            # Use typewriter effect for the response
            typewriter_effect_gui(text_widget, response, speed=0.01)
            
            text_widget.config(state=tk.NORMAL)
            text_widget.insert(tk.END, "\n\n")
            text_widget.config(state=tk.DISABLED)
            text_widget.see(tk.END)
            label.config(text="Ready")

        submit_button = tk.Button(input_frame, text="Send", command=on_submit, bg="#112240", fg="#00f5d4", activebackground="#0a0a0a", activeforeground="#ffffff", relief=tk.FLAT, font=("Consolas", 9))
        submit_button.pack(side=tk.RIGHT, padx=(4, 0), ipady=4)

        root.bind("<Return>", lambda event: on_submit())
        input_field.focus_set()  # Focus on input field

    show_helios_titlescreen(root, launch_main_ui)
    root.mainloop()


if __name__ == "__main__":
    main()
