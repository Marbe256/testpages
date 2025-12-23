
import os

def append_to_npower():
    # Read generated content
    # Try different encodings as powershell might have output utf-16
    content = ""
    try:
        with open('npower_content.txt', 'r', encoding='utf-16') as f:
            content = f.read()
    except:
        with open('npower_content.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            
    # Filter for n^8 and above
    # content consists of blocks $$...$$
    
    blocks = content.split('\n\n')
    to_append = []
    
    existing_powers = [3, 4, 5, 6, 7] # roughly from file view
    
    for block in blocks:
        if 'n^{8}' in block or 'n^{9}' in block or 'n^{10}' in block or 'n^{11}' in block or 'n^{12}' in block or 'n^{13}' in block or 'n^{14}' in block:
             to_append.append(block)
        elif 'n^{15}' in block or 'n^{16}' in block or 'n^{17}' in block or 'n^{18}' in block:
             to_append.append(block)
        elif 'n^{19}' in block or 'n^{20}' in block:
             to_append.append(block)
             
    # Sort to be sure? The script sorted them.
    
    # Read current npower.md
    with open('npower.md', 'r', encoding='utf-8') as f:
        current_md = f.read()
        
    # Append
    new_content = current_md.strip() + '\n\n' + '\n\n'.join(to_append)
    
    with open('npower.md', 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    append_to_npower()
