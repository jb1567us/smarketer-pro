
import os
import re

def resolve_conflict(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex to find <<<<<<< HEAD ... ======= ... >>>>>>> origin/branch
    # We use re.DOTALL to match across lines
    pattern = re.compile(r'<<<<<<< HEAD\n(.*?)\n?=======\n(.*?)\n?>>>>>>> [^\n]+', re.DOTALL)
    
    def replace_func(match):
        head_content = match.group(1)
        # return the HEAD content, essentially choosing HEAD
        return head_content

    new_content = pattern.sub(replace_func, content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    agents_dir = os.path.join(os.getcwd(), 'src', 'agents')
    modified_files = []
    for root, dirs, files in os.walk(agents_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                if resolve_conflict(path):
                    modified_files.append(path)
    
    if modified_files:
        print(f"SUCCESS: Resolved conflicts in {len(modified_files)} files:")
        for f in modified_files:
            print(f" - {f}")
    else:
        print("No conflicts found in agents directory.")

if __name__ == "__main__":
    main()
