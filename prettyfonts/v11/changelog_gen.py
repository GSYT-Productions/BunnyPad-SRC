import difflib

def generate_changelog(file1, file2, output_file="changelog.txt"):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        diff = difflib.unified_diff(
            f1.readlines(), f2.readlines(), fromfile=file1, tofile=file2
        )
        with open(output_file, 'w') as output:
            output.writelines(diff)
    print(f"Changelog saved to {output_file}")
file1input = input("Please enter the path of the first file: ")
file2input = input("Please enter the path of the second file: ")
# Usage
generate_changelog(file1input, file2input)
