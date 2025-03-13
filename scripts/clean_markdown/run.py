import os
import argparse
import frontmatter  # Make sure to install this library: pip install python-frontmatter
import llm 

def clean_file(filepath):
    # Read the file content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the frontmatter and the body
    post = frontmatter.loads(content)
    
    # Clean the Markdown body using the LLM
    cleaned_body = llm.run('markdown-cleaner', {'markdown': post.content})
    
    # Update the body while keeping the frontmatter unchanged
    post.content = cleaned_body
    
    # Generate the final file content
    new_content = frontmatter.dumps(post)
    
    # Overwrite the file with the cleaned content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Processed file: {filepath}')

def process_folder(folder_path):
    # Recursively walk through all files in the folder and subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Process only Markdown files (adjust the extension as needed)
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                clean_file(filepath)

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Clean Markdown files by processing the body while preserving the frontmatter.')
    parser.add_argument('folder', help='Path to the folder containing Markdown files')
    args = parser.parse_args()

    process_folder(args.folder)