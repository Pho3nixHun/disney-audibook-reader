#!/usr/bin/env python3

import os
import json
import struct

def read_synchsafe_int(data):
    """Read a synchsafe integer (7 bits per byte)"""
    result = 0
    for byte in data:
        result = (result << 7) | (byte & 0x7F)
    return result

def decode_text_frame(frame_data):
    """Decode text frame data based on encoding"""
    if len(frame_data) < 1:
        return ""

    encoding = frame_data[0]
    text_data = frame_data[1:]

    try:
        if encoding == 0:  # ISO-8859-1
            return text_data.rstrip(b'\x00').decode('latin-1', errors='ignore')
        elif encoding == 1:  # UTF-16 with BOM
            return text_data.rstrip(b'\x00').decode('utf-16', errors='ignore')
        elif encoding == 2:  # UTF-16BE
            return text_data.rstrip(b'\x00').decode('utf-16be', errors='ignore')
        elif encoding == 3:  # UTF-8
            return text_data.rstrip(b'\x00').decode('utf-8', errors='ignore')
        else:
            return text_data.rstrip(b'\x00').decode('latin-1', errors='ignore')
    except:
        return ""

def read_id3v2_improved(filepath):
    """Improved ID3v2 tag reader"""
    try:
        with open(filepath, 'rb') as f:
            # Read header
            header = f.read(10)
            if header[:3] != b'ID3':
                return None

            version_major = header[3]
            version_minor = header[4]
            flags = header[5]

            # Read synchsafe size
            size_bytes = header[6:10]
            if version_major >= 4:
                # ID3v2.4+ uses synchsafe integers
                tag_size = read_synchsafe_int(size_bytes)
            else:
                # ID3v2.3 uses regular big-endian integer
                tag_size = struct.unpack('>I', size_bytes)[0]

            print(f"  ID3v2.{version_major}.{version_minor}, size: {tag_size}")

            # Read the entire tag
            tag_data = f.read(tag_size)

            frames = {}
            pos = 0

            while pos < len(tag_data) - 10:
                # Check for padding
                if tag_data[pos:pos+4] == b'\x00\x00\x00\x00':
                    break

                # Read frame header
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

                frame_flags = tag_data[pos+8:pos+10]

                # Bounds check
                if pos + 10 + frame_size > len(tag_data):
                    break

                frame_data = tag_data[pos+10:pos+10+frame_size]

                print(f"    Frame: {frame_id_str}, size: {frame_size}")

                # Parse important text frames
                if frame_id_str in ['TIT1', 'TIT2', 'TIT3', 'TPE1', 'TPE2', 'TALB', 'TDRC', 'TYER', 'TCON']:
                    text = decode_text_frame(frame_data)
                    frames[frame_id_str] = text
                    if text:
                        print(f"      Content: {text}")

                pos += 10 + frame_size

            return {
                'title': frames.get('TIT2', frames.get('TIT1', '')),
                'artist': frames.get('TPE1', ''),
                'album': frames.get('TALB', ''),
                'year': frames.get('TDRC', frames.get('TYER', '')),
                'genre': frames.get('TCON', ''),
                'version': f"2.{version_major}.{version_minor}",
                'all_frames': frames
            }

    except Exception as e:
        print(f"    Error: {e}")
        return None

def analyze_sample_files():
    """Analyze first few files to understand the metadata structure"""
    audio_dir = 'extracted_audio'

    if not os.path.exists(audio_dir):
        print(f"Directory {audio_dir} not found!")
        return

    mp3_files = sorted([f for f in os.listdir(audio_dir) if f.upper().endswith('.MP3')])[:5]

    print(f"Analyzing first {len(mp3_files)} files for metadata structure...\n")

    results = []

    for filename in mp3_files:
        filepath = os.path.join(audio_dir, filename)
        print(f"Analyzing {filename}:")

        # Get file info
        stat = os.stat(filepath)
        file_info = {
            'filename': filename,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024*1024), 2)
        }

        # Try improved ID3v2 reader
        metadata = read_id3v2_improved(filepath)

        result = {
            'file': file_info,
            'metadata': metadata
        }

        results.append(result)
        print()

    return results

if __name__ == '__main__':
    analyze_sample_files()