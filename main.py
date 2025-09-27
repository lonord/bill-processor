#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bill Processor Main Entry
Process all bill files in the specified directory
"""

import os
import sys
import argparse
from typing import List
from processors import BaseProcessor, get_available_processors




def find_matching_processor(file_path: str, processors: List[BaseProcessor]) -> BaseProcessor:
    """
    Find matching processor for the specified file
    
    Args:
        file_path (str): File path
        processors (List[BaseProcessor]): List of processors
        
    Returns:
        BaseProcessor: Matching processor, returns None if not found
    """
    for processor in processors:
        if processor.can_process(file_path):
            return processor
    return None


def process_bill_files(bill_dir: str, db_path: str) -> int:
    """
    Process all files in the bill directory
    
    Args:
        bill_dir (str): Bill file directory
        db_path (str): Database file path
        
    Returns:
        int: Number of successfully processed files
    """
    if not os.path.exists(bill_dir):
        print(f"Error: Bill directory does not exist: {bill_dir}")
        return 0
    
    if not os.path.exists(db_path):
        print(f"Error: Database file does not exist: {db_path}")
        print("Please run setup_database.py first to create the database")
        return 0
    
    # Get all processors
    processors = get_available_processors()
    print(f"Loaded {len(processors)} processors")
    
    # Get the maximum UPDATE_TIME from database
    temp_processor = processors[0] if processors else None
    if temp_processor:
        temp_processor.db_path = db_path
        max_update_time = temp_processor.get_max_update_time()
        print(f"Maximum UPDATE_TIME in database: {max_update_time}")
    else:
        max_update_time = 0
        print("No available processors, will process all files")
    
    # Get all files in the directory
    files = [f for f in os.listdir(bill_dir) if os.path.isfile(os.path.join(bill_dir, f))]
    print(f"Found {len(files)} files in directory {bill_dir}")
    
    processed_count = 0
    total_records = 0
    skipped_count = 0
    
    for filename in files:
        file_path = os.path.join(bill_dir, filename)
        
        # Check file modification time
        try:
            file_mtime = int(os.path.getmtime(file_path))
            if file_mtime <= max_update_time:
                skipped_count += 1
                continue
        except OSError as e:
            print(f"\nWarning: Unable to get modification time for file {filename}: {e}")
            # If unable to get modification time, continue processing the file
        
        print(f"\nProcessing file: {filename}")
        
        # Find matching processor
        processor = find_matching_processor(file_path, processors)
        
        if processor is None:
            print(f"  Skip: No suitable processor found")
            continue
        
        print(f"  Using processor: {processor.__class__.__name__}")
        
        # Set database path
        processor.db_path = db_path
        
        # Process file
        try:
            saved_count = processor.process_and_save(file_path)
            if saved_count > 0:
                processed_count += 1
                total_records += saved_count
                print(f"  ✓ Successfully processed, saved {saved_count} records")
            else:
                print(f"  ✗ Processing failed or no valid records")
        except Exception as e:
            print(f"  ✗ Error processing file: {e}")
    
    print(f"\nProcessing completed!")
    print(f"Successfully processed files: {processed_count}")
    print(f"Skipped files: {skipped_count}")
    print(f"Total records: {total_records}")
    
    return processed_count


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Bill Processor - Process various bill file formats')
    parser.add_argument('--bill-dir', '-d', 
                       default='extract',
                       help='Bill file directory path (default: extract)')
    parser.add_argument('--db-path', '-db',
                       default='billing.sqlite',
                       help='Database file path (default: billing.sqlite)')
    parser.add_argument('--list-processors', '-l',
                       action='store_true',
                       help='List all available processors')
    
    args = parser.parse_args()
    
    # List processor information
    if args.list_processors:
        print("Available bill processors:")
        print("-" * 50)
        processors = get_available_processors()
        for processor in processors:
            print(f"• {processor.__class__.__name__}")
        return 0
    
    # Process bill files
    print("Bill Processor")
    print("=" * 60)
    print(f"Bill directory: {os.path.abspath(args.bill_dir)}")
    print(f"Database file: {os.path.abspath(args.db_path)}")
    print("=" * 60)
    
    processed_count = process_bill_files(args.bill_dir, args.db_path)
    
    if processed_count > 0:
        print(f"\n✓ Successfully processed {processed_count} files")
    else:
        print("\n✗ No files were successfully processed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
