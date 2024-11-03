import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import customtkinter as ctk
import heapq
from collections import Counter
import time

# Step 1: Define Node for Huffman Tree
class Node:
    def __init__(self, freq, symbol, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

# Step 2: Calculate Frequency of Words
def calculate_frequency(text):
    if not text.strip():
        raise ValueError("Input text is empty.")
    words = text.split()
    return dict(Counter(words))

# Step 3: Build Huffman Tree
def build_huffman_tree(frequencies):
    heap = [Node(freq, symbol) for symbol, freq in frequencies.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        new_node = Node(left.freq + right.freq, None, left, right)
        heapq.heappush(heap, new_node)
    
    return heapq.heappop(heap)

# Step 4: Generate Huffman Codes
def generate_codes(node, binary_str='', codes={}):
    if node is None:
        return
    if node.symbol is not None:
        codes[node.symbol] = binary_str
    generate_codes(node.left, binary_str + '0', codes)
    generate_codes(node.right, binary_str + '1', codes)
    return codes

# Step 5: Compress the Text
def compress_text(text, codes):
    words = text.split()
    return ''.join([codes[word] for word in words])

# Step 6: Decompress the Text with Live Processing Update
def decompress_text_with_progress(compressed_data, root, progress_label, progress_bar, tk_root):
    decoded_text = []
    current_node = root
    total_bits = len(compressed_data)
    processed_bits = 0

    for bit in compressed_data:
        current_node = current_node.left if bit == '0' else current_node.right
        processed_bits += 1

        if current_node.left is None and current_node.right is None:
            decoded_text.append(current_node.symbol)
            current_node = root
            
            # Update the progress label and bar
            progress = (processed_bits / total_bits) * 100
            progress_label.configure(text=f"Decompressing... {progress:.2f}%")
            progress_bar['value'] = progress
            tk_root.update_idletasks()
            time.sleep(0.01)  # Small delay to simulate processing time

    progress_label.configure(text="Decompression Complete!")
    tk_root.update()
    return ' '.join(decoded_text)

# Helper function to calculate text size in KB
def size_in_kb(text, is_compressed=False):
    if is_compressed:
        return len(text) / 8 / 1024
    return len(text.encode('utf-8')) / 1024

# Main function for compression and decompression
def huffman_word_compression(text):
    frequencies = calculate_frequency(text)
    huffman_tree = build_huffman_tree(frequencies)
    huffman_codes = generate_codes(huffman_tree)
    compressed_text = compress_text(text, huffman_codes)
    return compressed_text, huffman_tree, huffman_codes

# GUI Function
def compress_decompress():
    input_text = text_input.get("1.0", tk.END).strip()
    
    if not input_text:
        messagebox.showwarning("Input Error", "Please enter some text to compress.")
        return

    # Create a Toplevel window for showing compression progress
    progress_window = tk.Toplevel(root)
    progress_window.title("Progress")
    progress_window.geometry("300x150")
    progress_label = ctk.CTkLabel(progress_window, text="Starting...", font=("Arial", 12))
    progress_label.pack(pady=10)

    # Create Progress Bar widget
    progress_bar = ttk.Progressbar(progress_window, orient='horizontal', length=200, mode='determinate')
    progress_bar.pack(pady=10)

    try:
        # Compression Process
        progress_label.configure(text="Compressing...")
        root.update()
        
        # Compression steps with progress update
        compressed_data, huffman_tree, codes = huffman_word_compression(input_text)
        
        # Decompression Process
        progress_label.configure(text="Decompressing...")
        decompressed_text = decompress_text_with_progress(compressed_data, huffman_tree, progress_label, progress_bar, root)

        # Close the progress window after decompression is complete
        progress_window.destroy()

        # Calculate sizes in KB
        original_size_kb = size_in_kb(input_text)
        compressed_size_kb = size_in_kb(compressed_data, is_compressed=True)

        # Display results
        compressed_output.configure(state='normal')
        compressed_output.delete("1.0", tk.END)
        compressed_output.insert(tk.END, f"Compressed Data:\n{compressed_data}\n\n")
        compressed_output.insert(tk.END, f"Huffman Codes:\n{codes}\n\n")
        compressed_output.insert(tk.END, f"Original Size: {original_size_kb:.4f} KB\n")
        compressed_output.insert(tk.END, f"Compressed Size: {compressed_size_kb:.4f} KB\n")
        compressed_output.insert(tk.END, f"Compression Ratio: {original_size_kb / compressed_size_kb:.2f}")
        compressed_output.configure(state='disabled')
        
        decompressed_output.configure(state='normal')
        decompressed_output.delete("1.0", tk.END)
        decompressed_output.insert(tk.END, f"Decompressed Text:\n{decompressed_text}")
        decompressed_output.configure(state='disabled')
        
    except ValueError as e:
        progress_window.destroy()
        messagebox.showerror("Error", str(e))

    status_label.configure(text="Done")
    root.update()

# Custom Tkinter main window
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Huffman Word Compression")
root.geometry("700x650")

# Input Text Label and Entry
input_label = ctk.CTkLabel(root, text="Enter Text for Compression:", font=("Arial", 12))
input_label.pack(pady=10)

text_input = ctk.CTkTextbox(root, height=100, width=600)
text_input.pack(pady=10)

# Compress Button
compress_button = ctk.CTkButton(root, text="Compress & Decompress", command=compress_decompress)
compress_button.pack(pady=10)

# Status Label for Processing Indicator
status_label = ctk.CTkLabel(root, text="", font=("Arial", 12))
status_label.pack(pady=5)

# Compressed Data Output
compressed_output_label = ctk.CTkLabel(root, text="Compressed Data:", font=("Arial", 12))
compressed_output_label.pack(pady=10)

compressed_output = ctk.CTkTextbox(root, height=150, width=600, state='disabled')
compressed_output.pack(pady=10)

# Decompressed Text Output
decompressed_output_label = ctk.CTkLabel(root, text="Decompressed Text:", font=("Arial", 12))
decompressed_output_label.pack(pady=10)

decompressed_output = ctk.CTkTextbox(root, height=100, width=600, state='disabled')
decompressed_output.pack(pady=10)

# Run the main Tkinter event loop
root.mainloop()
