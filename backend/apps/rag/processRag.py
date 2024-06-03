import vectorSearch as vs
import pprint as pp
import os, glob, re

def chunkize_and_save(text):
    clear_directory()
    chunks = text.split('\n\n')
    for i, chunk in enumerate(chunks):
        # Skip the chunk if it's empty
        if not chunk.strip():
            continue
        # Save the chunk into a separate file in the ./hits/ directory
        with open(f'./hits/hit_{i}.txt', 'w') as f:
            f.write(chunk)

def clear_directory():
    files = glob.glob('./hits/*')
    for file in files:
        os.remove(file)

def build_content(mode):
    content = ""
    files = sorted(os.listdir('./hits/'), key=lambda x: int(x[4:-4]))
    for file in files:
        if file.startswith('hit_') and file.endswith('.txt'):
            with open(f'./hits/{file}', 'r') as f:
                file_content = eval(f.read())
                hit_number = re.findall(r'\d+', file)[0]
                content_values = [file_content[key] for key in sorted(k for k in file_content.keys() if k.startswith('content_'))]
                if mode == 0:
                    result_string = f"#VectorDatabase result {hit_number}\n"
                    result_string += f"#File name = '{file_content['_id']}'\n"
                    result_string += f"#Similarity score = {file_content['_score']}\n"
                    result_string += f"#Most relevant part of the document = '{list(file_content['_highlights'][0].values())[0]}'\n"
                    result_string += f"#This file exists on the path = {file_content['path']}.\n"
                    result_string += "\n"
                    content += result_string
                elif mode == 1:
                    result_string = f"#VectorDatabase result {hit_number}\n"
                    result_string += f"#File name = '{file_content['_id']}'\n"
                    result_string += f"#Similarity score = {file_content['_score']}\n"
                    result_string += f"#Most relevant part of the document = '{list(file_content['_highlights'][0].values())[0]}'\n"
                    result_string += f"#This file exists on the path = {file_content['path']}\n"
                    
                    highlight_index = sorted(file_content.keys()).index([key for key in sorted(file_content.keys()) if key.startswith('content_')][0])
                    start_index = max(0, highlight_index - 1)
                    end_index = min(len(content_values), highlight_index + 2)
                    relevant_content = ' '.join(content_values[start_index:highlight_index] + ["+ Most relevant part goes here +"] + content_values[highlight_index:end_index])
                    
                    result_string += f"#And here is a bit more context around the most relevant part of the document = '{relevant_content}'.\n"
                    result_string += "\n"
                    content += result_string
                elif mode == 2:
                    result_string = f"#VectorDatabase result N\n"
                    result_string += f"#File name = '{file_content['_id']}'\n"
                    result_string += f"#Similarity score = {file_content['_score']}\n"
                    result_string += f"#Most relevant part of the document = '{list(file_content['_highlights'][0].values())[0]}'\n"
                    result_string += f"#This file exists on the path = {file_content['path']}\n"
                    result_string += f"#And here is the whole document = '{' '.join(content_values)}'.\n"
                    result_string += f"\n"
                    content += result_string
    return content

def sum(query, limit, index):
    output_string, metadata = vs.index_search(index, query, limit)
    chunkize_and_save(output_string)
    content = build_content(1)
    to_be = prompt_concat(query, content, metadata)
    with open('sum.txt', 'w') as f:
        f.write(content)
    with open('sum2.txt', 'w') as f:
        f.write(to_be)
    return to_be, metadata, content

def prompt_concat(prompt, content, metadata):
    to_be = ''
    to_be += "("
    to_be += "the following is a the output of the vectorDB search based of the prompt above, this database consists of all documents in the masterdocuments directory of BSS.\n"
    to_be += "\n"
    to_be += content
    to_be += ")\n"
    to_be += "This is the query asked by the USER for you:\n"
    to_be += prompt
    to_be += "\n\n"
    return to_be

