import os

def append_string_2_txt(data_dir: str, text_to_add: str):

    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"The folder '{data_dir}' doesn't exist.")
    
    txt_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.txt')]
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in '{data_dir}'.")
    
    input_file = os.path.join(data_dir, txt_files[0])
    output_file = os.path.join(data_dir, f"{os.path.splitext(txt_files[0])[0]}_modified.txt")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
        if not content.endswith('\n'):
            f.write('\n')
        f.write(text_to_add)

    print(f"File successfully modified: {output_file}")

    return