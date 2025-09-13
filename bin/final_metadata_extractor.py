#!/usr/bin/env python3

import os
import json
import struct

def read_synchsafe_int(data):
    result = 0
    for byte in data:
        result = (result << 7) | (byte & 0x7F)
    return result

def decode_text_frame(frame_data):
    if len(frame_data) < 1:
        return ""

    encoding = frame_data[0]
    text_data = frame_data[1:]

    try:
        if encoding == 0:
            return text_data.rstrip(b'\x00').decode('latin-1', errors='ignore')
        elif encoding == 1:
            return text_data.rstrip(b'\x00').decode('utf-16', errors='ignore')
        elif encoding == 2:
            return text_data.rstrip(b'\x00').decode('utf-16be', errors='ignore')
        elif encoding == 3:
            return text_data.rstrip(b'\x00').decode('utf-8', errors='ignore')
        else:
            return text_data.rstrip(b'\x00').decode('latin-1', errors='ignore')
    except:
        return ""

def read_id3v2_metadata(filepath):
    try:
        with open(filepath, 'rb') as f:
            header = f.read(10)
            if header[:3] != b'ID3':
                return None

            version_major = header[3]
            version_minor = header[4]

            size_bytes = header[6:10]
            if version_major >= 4:
                tag_size = read_synchsafe_int(size_bytes)
            else:
                tag_size = struct.unpack('>I', size_bytes)[0]

            tag_data = f.read(tag_size)
            frames = {}
            pos = 0

            while pos < len(tag_data) - 10:
                if tag_data[pos:pos+4] == b'\x00\x00\x00\x00':
                    break

                if pos + 10 > len(tag_data):
                    break

                frame_id = tag_data[pos:pos+4]
                try:
                    frame_id_str = frame_id.decode('ascii')
                except:
                    break

                if version_major >= 4:
                    frame_size = read_synchsafe_int(tag_data[pos+4:pos+8])
                else:
                    frame_size = struct.unpack('>I', tag_data[pos+4:pos+8])[0]

                if pos + 10 + frame_size > len(tag_data):
                    break

                frame_data = tag_data[pos+10:pos+10+frame_size]

                if frame_id_str in ['TIT1', 'TIT2', 'TIT3', 'TPE1', 'TPE2', 'TALB', 'TDRC', 'TYER', 'TCON']:
                    text = decode_text_frame(frame_data)
                    frames[frame_id_str] = text

                pos += 10 + frame_size

            return {
                'version': f"2.{version_major}.{version_minor}",
                'title': frames.get('TIT2', frames.get('TIT1', '')),
                'artist': frames.get('TPE1', ''),
                'album': frames.get('TALB', ''),
                'year': frames.get('TDRC', frames.get('TYER', '')),
                'genre': frames.get('TCON', ''),
                'frames_found': list(frames.keys())
            }
    except Exception:
        return None

def guess_title_from_filename(filename):
    """Attempt to guess the content from truncated filename"""
    base = filename.replace('.MP3', '').replace('_', '').upper()

    # Map known prefixes to likely Disney stories
    mappings = {
        '01-ALA': 'Aladdin',
        '02-SNO': 'Snow White',
        '03-LIO': 'Lion King',
        '04-FIN': 'Finding Nemo',
        '05-JUN': 'Jungle Book',
        '06-TOY': 'Toy Story',
        '07-PET': 'Peter Pan',
        '08-DUM': 'Dumbo',
        '09-LIT': 'Little Mermaid',
        '10-PIN': 'Pinocchio',
        '11-FRO': 'Frozen',
        '12-101': '101 Dalmatians',
        '13-BEA': 'Beauty and the Beast',
        '18-TAN': 'Tangled',
        '20-RAT': 'Ratatouille',
        '24-INC': 'The Incredibles',
        '25-SLE': 'Sleeping Beauty',
        '26-ARI': 'The Little Mermaid (Ariel)',
        '27-POC': 'Pocahontas',
        '29-LIL': 'Lady and the Tramp',
        '30-HUN': 'The Hunchback of Notre Dame',
        '31-ZOO': 'Zootopia',
        '38-MOA': 'Moana'
    }

    for prefix, title in mappings.items():
        if base.startswith(prefix):
            return title

    # For generic DIS files, just return the number
    if base.startswith('DIS') or 'DIS' in base:
        return f"Disney Story {base.split('-')[0]}"

    return ""

def create_complete_metadata():
    audio_dir = 'extracted_audio'

    if not os.path.exists(audio_dir):
        print(f"Directory {audio_dir} not found!")
        return

    mp3_files = sorted([f for f in os.listdir(audio_dir) if f.upper().endswith('.MP3')])
    print(f"Processing {len(mp3_files)} MP3 files...")

    metadata = []

    for filename in mp3_files:
        filepath = os.path.join(audio_dir, filename)

        # Get file info
        stat = os.stat(filepath)
        file_info = {
            'filename': filename,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024*1024), 2)
        }

        # Get ID3 metadata
        id3_data = read_id3v2_metadata(filepath)

        # Guess title from filename
        guessed_title = guess_title_from_filename(filename)

        entry = {
            'filename': filename,
            'file_size_mb': file_info['size_mb'],
            'file_size_bytes': file_info['size_bytes'],
            'guessed_title': guessed_title,
            'id3_metadata': id3_data,
            'actual_title': id3_data['title'] if id3_data else '',
            'actual_artist': id3_data['artist'] if id3_data else '',
            'actual_album': id3_data['album'] if id3_data else '',
            'actual_year': id3_data['year'] if id3_data else '',
            'actual_genre': id3_data['genre'] if id3_data else ''
        }

        metadata.append(entry)

    # Save complete metadata
    output_file = 'complete_disney_metadata.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Complete metadata saved to {output_file}")

    # Print summary
    print(f"\nSummary:")
    print(f"Total files: {len(metadata)}")

    with_id3 = sum(1 for item in metadata if item['id3_metadata'])
    print(f"Files with ID3v2 tags: {with_id3}")

    with_genre = sum(1 for item in metadata if item['actual_genre'])
    print(f"Files with genre info: {with_genre}")

    guessed = sum(1 for item in metadata if item['guessed_title'])
    print(f"Files with guessed titles: {guessed}")

    # Show first few entries
    print(f"\nFirst 10 files:")
    for i, item in enumerate(metadata[:10]):
        title = item['guessed_title'] or item['actual_title'] or 'Unknown'
        print(f"  {i+1:2d}. {item['filename']:15} -> {title}")

if __name__ == '__main__':
    create_complete_metadata()