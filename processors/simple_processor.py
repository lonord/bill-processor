#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Bill Processor
Process simple bill files starting with bill_ and ending with .csv
File format: time,amount,label,note (no header, data starts from first row)
"""

import os
import csv
from typing import List
from .base_processor import BaseProcessor, BillRecord


class SimpleProcessor(BaseProcessor):
    """Simple bill processor"""
    
    def can_process(self, file_path: str) -> bool:
        """
        Determine if the specified file can be processed
        
        Args:
            file_path (str): File path
            
        Returns:
            bool: Whether the file can be processed
        """
        if not os.path.exists(file_path):
            return False
        
        filename = os.path.basename(file_path)
        return filename.startswith('bill_') and filename.endswith('.csv')
    
    def process_file(self, file_path: str) -> List[BillRecord]:
        """
        Process simple bill file and return list of bill records
        
        Args:
            file_path (str): File path
            
        Returns:
            List[BillRecord]: List of bill records
        """
        records = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                
                for row_num, row in enumerate(csv_reader, 1):
                    # Skip empty rows
                    if not row or len(row) < 4:
                        continue
                    
                    try:
                        # Parse data: time,amount,label,note
                        time_str = row[0].strip()
                        amount_str = row[1].strip()
                        label = row[2].strip()
                        note = row[3].strip() if len(row) > 3 else ""
                        
                        # Validate time format
                        if not time_str:
                            print(f"Row {row_num}: Time field is empty, skipping")
                            continue
                        
                        # Validate amount format
                        try:
                            amount = float(amount_str)
                        except ValueError:
                            print(f"Row {row_num}: Invalid amount format '{amount_str}', skipping")
                            continue
                        
                        # Create bill record
                        record = BillRecord(
                            time=time_str,
                            amount=amount,
                            currency="CNY",  # Fixed as CNY
                            bill_type="消费",  # Fixed as consumption
                            info=label,  # Use label column as info
                            note=note,  # Use note column as note
                            source="legacy"  # Fixed as legacy
                        )
                        
                        # Generate unique ID: time + @ + row number
                        record.id = f"{time_str}@{row_num}"
                        
                        records.append(record)
                        
                    except Exception as e:
                        print(f"Row {row_num} processing failed: {e}")
                        continue
                        
        except Exception as e:
            print(f"Failed to read file: {e}")
            return []
        
        print(f"Parsed {len(records)} records from file {os.path.basename(file_path)}")
        return records
