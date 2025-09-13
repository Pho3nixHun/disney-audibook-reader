#!/usr/bin/env python3

import os
import json
import struct

def read_id3v1_tag(filepath):
    """Read ID3v1 tag from MP3 file"""
    try:
        with open(filepath, 'rb') as f:
            # ID3v1 tag is in the last 128 bytes
            f.seek(-128, 2)
            tag_data = f.read(128)

            if tag_data[:3] != b'TAG':
                return None

            title = tag_data[3:33].decode('latin-1', errors='ignore').strip('\x00 ')
            artist = tag_data[33:63].decode('latin-1', errors='ignore').strip('\x00 ')
            album = tag_data[63:93].decode('latin-1', errors='ignore').strip('\x00 ')
            year = tag_data[93:97].decode('latin-1', errors='ignore').strip('\x00 ')
            comment = tag_data[97:127].decode('latin-1', errors='ignore').strip('\x00 ')
            genre = tag_data[127] if len(tag_data) > 127 else 0

            return {
                'title': title,
                'artist': artist,
                'album': album,
                'year': year,
                'comment': comment,
                'genre': genre
            }
    except Exception as e:
        print(f"Error reading ID3v1 tag from {filepath}: {e}")
        return None

def read_id3v2_tag(filepath):
    """Read basic ID3v2 tag info from MP3 file"""
    try:
        with open(filepath, 'rb') as f:
            # Check for ID3v2 header
            header = f.read(10)
            if header[:3] != b'ID3':
                return None

            # Parse header
            version = (header[3], header[4])
            flags = header[5]
            size = struct.unpack('>I', b'\x00' + header[6:9])[0]

            # Read tag data
            tag_data = f.read(size)

            frames = {}
            pos = 0

            while pos < len(tag_data) - 10:
                if tag_data[pos:pos+4] == b'\x00\x00\x00\x00':
                    break

                frame_id = tag_data[pos:pos+4].decode('ascii', errors='ignore')
                frame_size = struct.unpack('>I', tag_data[pos+4:pos+8])[0]
                frame_flags = tag_data[pos+8:pos+10]
                frame_data = tag_data[pos+10:pos+10+frame_size]

                if frame_id in ['TIT2', 'TPE1', 'TALB', 'TDRC', 'TYER', 'COMM']:
                    # Text frames usually start with encoding byte
                    if len(frame_data) > 0:
                        encoding = frame_data[0]
                        text_data = frame_data[1:]

                        if encoding == 0:  # ISO-8859-1
                            text = text_data.decode('latin-1', errors='ignore')
                        elif encoding == 1:  # UTF-16 with BOM
                            text = text_data.decode('utf-16', errors='ignore')
                        elif encoding == 3:  # UTF-8
                            text = text_data.decode('utf-8', errors='ignore')
                        else:
                            text = text_data.decode('latin-1', errors='ignore')

                        frames[frame_id] = text.strip('\x00 ')

                pos += 10 + frame_size

            return {
                'title': frames.get('TIT2', ''),
                'artist': frames.get('TPE1', ''),
                'album': frames.get('TALB', ''),
                'year': frames.get('TDRC', frames.get('TYER', '')),
                'comment': frames.get('COMM', ''),
                'version': f"2.{version[0]}.{version[1]}"
            }

    except Exception as e:
        print(f"Error reading ID3v2 tag from {filepath}: {e}")
        return None

def get_file_info(filepath):
    """Get basic file information"""
    try:
        stat = os.stat(filepath)
        return {
            'filename': os.path.basename(filepath),
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024*1024), 2)
        }
    except Exception as e:
        return {
            'filename': os.path.basename(filepath),
            'size_bytes': 0,
            'size_mb': 0,
            'error': str(e)
        }

def extract_all_metadata():
    audio_dir = 'extracted_audio'
    metadata = []

    if not os.path.exists(audio_dir):
        print(f"Directory {audio_dir} not found!")
        return

    mp3_files = sorted([f for f in os.listdir(audio_dir) if f.upper().endswith('.MP3')])

    print(f"Analyzing {len(mp3_files)} MP3 files...")

    for filename in mp3_files:
        filepath = os.path.join(audio_dir, filename)
        print(f"Processing {filename}...")

        file_info = get_file_info(filepath)
        id3v2_tag = read_id3v2_tag(filepath)
        id3v1_tag = read_id3v1_tag(filepath)

        # Combine metadata
        combined_metadata = {
            'file': file_info,
            'id3v2': id3v2_tag,
            'id3v1': id3v1_tag
        }

        # Extract best available metadata
        title = ''
        artist = ''
        album = ''
        year = ''

        if id3v2_tag:
            title = id3v2_tag.get('title', '')
            artist = id3v2_tag.get('artist', '')
            album = id3v2_tag.get('album', '')
            year = id3v2_tag.get('year', '')

        if not title and id3v1_tag:
            title = id3v1_tag.get('title', '')

        if not artist and id3v1_tag:
            artist = id3v1_tag.get('artist', '')

        if not album and id3v1_tag:
            album = id3v1_tag.get('album', '')

        if not year and id3v1_tag:
            year = id3v1_tag.get('year', '')

        summary = {
            'filename': filename,
            'title': title,
            'artist': artist,
            'album': album,
            'year': year,
            'size_mb': file_info['size_mb'],
            'raw_metadata': combined_metadata
        }

        metadata.append(summary)

        # Print a preview
        if title:
            print(f"  Title: {title}")
        if artist:
            print(f"  Artist: {artist}")
        if album:
            print(f"  Album: {album}")
        print()

    # Save to JSON
    output_file = 'disney_audio_metadata.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Metadata saved to {output_file}")

    # Print summary
    print(f"\nSummary:")
    print(f"Total files: {len(metadata)}")

    titles_found = sum(1 for item in metadata if item['title'])
    print(f"Files with titles: {titles_found}")

    artists_found = sum(1 for item in metadata if item['artist'])
    print(f"Files with artist info: {artists_found}")

    albums_found = sum(1 for item in metadata if item['album'])
    print(f"Files with album info: {albums_found}")

if __name__ == '__main__':
    extract_all_metadata()