#!/usr/bin/env python3

import os
from fat16_reader import FAT16Reader

def extract_all_audio_files():
    reader = FAT16Reader('partition1.img')

    # Create output directory
    output_dir = 'extracted_audio'
    os.makedirs(output_dir, exist_ok=True)

    # Get all files
    all_files = reader.list_all_files()

    audio_files = []
    for path, size, is_dir in all_files:
        if not is_dir and path.upper().endswith('.MP3'):
            audio_files.append((path, size))

    print(f"Found {len(audio_files)} MP3 files to extract:")

    # Extract each audio file
    for path, size in audio_files:
        # Find the file entry to get its cluster
        dir_parts = path.split('/')
        current_cluster = 0

        # Navigate to the directory containing the file
        for part in dir_parts[:-1]:
            entries = reader.read_directory(current_cluster)
            found = False
            for entry in entries:
                if entry['name'].upper() == part.upper() and entry['is_dir']:
                    current_cluster = entry['first_cluster']
                    found = True
                    break
            if not found:
                print(f"Could not find directory {part}")
                continue

        # Find the file in the final directory
        entries = reader.read_directory(current_cluster)
        file_entry = None
        filename = dir_parts[-1]

        for entry in entries:
            if entry['name'].upper() == filename.upper():
                file_entry = entry
                break

        if file_entry is None:
            print(f"Could not find file {filename}")
            continue

        # Extract the file
        print(f"Extracting {path} ({size} bytes)...")
        data = reader.read_file(file_entry['first_cluster'], size)

        # Clean up the filename for saving
        output_filename = path.replace('/', '_').replace('~1', '')
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"  -> {output_path}")

    reader.close()
    print(f"\nExtracted {len(audio_files)} audio files to {output_dir}/")

    # Also read the README.txt file for more info
    reader = FAT16Reader('partition1.img')
    entries = reader.read_directory(0)  # Root

    for entry in entries:
        if entry['name'].upper() == 'CODE' and entry['is_dir']:
            code_entries = reader.read_directory(entry['first_cluster'])
            for code_entry in code_entries:
                if code_entry['name'].upper() == 'README.TXT':
                    readme_data = reader.read_file(code_entry['first_cluster'], code_entry['size'])
                    print(f"\nREADME.TXT contents:")
                    print("-" * 40)
                    print(readme_data.decode('utf-8', errors='ignore'))
                    break
            break

    reader.close()

if __name__ == '__main__':
    extract_all_audio_files()