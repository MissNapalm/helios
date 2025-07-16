import subprocess
import os
import time
import sys
import threading

def typewriter_effect(text, speed=0.001):
    """Ultra-fast typewriter effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def thinking_animation():
    """Simple spinner animation"""
    thinking = True
    start_time = time.time()
    spinner_frames = ["|", "/", "-", "\\"]
    
    def animate():
        i = 0
        while thinking:
            sys.stdout.write(f"\rthinking {spinner_frames[i % len(spinner_frames)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
    
    thread = threading.Thread(target=animate)
    thread.daemon = True
    thread.start()
    
    def stop():
        nonlocal thinking
        thinking = False
        elapsed = time.time() - start_time
        sys.stdout.write(f"\rthought for {elapsed:.1f} seconds\n\n")
        sys.stdout.flush() 
    
    return stop

def ensure_ollama_running():
    """Ensure Ollama service is running"""
    try:
        subprocess.run("ollama serve", shell=True, timeout=1, capture_output=True)
    except:
        pass  # Already running or will start

def get_quick_fallback(user_input):
    """Quick fallback responses for common questions"""
    user_lower = user_input.lower()
    
    # Greetings
    if any(word in user_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! Great to meet you! I'm HELIOS, ready to chat about anything. What's on your mind?"
    
    # Food/dinner questions
    if any(word in user_lower for word in ['dinner', 'eat', 'food', 'hungry', 'meal']):
        return "For dinner, you could try:\n• Something quick: pasta, stir-fry, or sandwiches\n• Comfort food: pizza, burgers, or soup\n• Healthy: salad, grilled chicken, or fish\n• Order in: your favorite takeout!\n\nWhat sounds good to you?"
    
    # Music/songs
    if any(word in user_lower for word in ['song', 'music', 'favorite', 'listen']):
        return "I don't have personal preferences, but I can suggest some great music! What genre do you like? Rock, pop, hip-hop, electronic, classical? Or tell me your mood and I'll suggest something!"
    
    # Personal questions about AI
    if any(phrase in user_lower for phrase in ['what do you enjoy', 'what are you', 'who are you']):
        return "I'm HELIOS! I enjoy having conversations, helping with questions, and learning about what interests you. I'm curious about your thoughts and happy to chat about anything!"
    
    return None

def get_ollama_response(user_input):
    """Get response from Ollama with no timeout"""
    try:
        # Start thinking animation
        stop_thinking = thinking_animation()
        
        # Add prompt to keep responses short
        prompt = f"{user_input}\n\nPlease keep your response brief and concise."
        
        result = subprocess.run(
            ["ollama", "run", "llama3.2:1b", prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Stop thinking animation
        stop_thinking()
        
        if result.returncode == 0 and result.stdout.strip():
            response = result.stdout.strip()
            # Only filter out truly problematic responses, not normal AI responses
            if len(response) > 5:  # Any response longer than 5 chars is probably valid
                return response
        
        return "I'm having trouble connecting to the AI. Try asking again!"
            
    except Exception as e:
        # Stop thinking animation  
        stop_thinking()
        return f"Error: {str(e)}"

def main():
    """Main HELIOS CTF Assistant loop"""
    print("🔄 Starting HELIOS CTF Assistant...")
    
    # Ensure Ollama is running
    ensure_ollama_running()
    
    print("\n🔥 HELIOS CTF Assistant Ready!")
    print("⚡ Simple conversational mode with Ollama LLM\n")
    
    while True:
        try:
            user_input = input("🎯 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                typewriter_effect("👋 Happy hacking! See you next time!")
                break
                
            if not user_input:
                continue
                
            # Get AI response (animation will show automatically)
            response = get_ollama_response(user_input)
            
            typewriter_effect(response, speed=0.01)  # Fast typewriter
            print()  # Add spacing
            
        except KeyboardInterrupt:
            print("\n\n👋 Caught Ctrl+C - Exiting HELIOS...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
