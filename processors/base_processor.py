#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Bill Processor Class
Define common interface and basic functionality for all processors
"""

import os
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


class BillRecord:
    """Bill record data class"""
    
    def __init__(self, time: str, amount: float, currency: str, 
                 bill_type: str, info: str = "", note: str = "", source: str = ""):
        self.id = str(uuid.uuid4())
        self.time = time
        self.amount = amount
        self.currency = currency
        self.bill_type = bill_type
        self.info = info
        self.note = note
        self.source = source
        self.update_time = int(datetime.now().timestamp())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'ID': self.id,
            'TIME': self.time,
            'AMOUNT': self.amount,
            'CURRENCY': self.currency,
            'TYPE': self.bill_type,
            'INFO': self.info,
            'NOTE': self.note,
            'SOURCE': self.source,
            'UPDATE_TIME': self.update_time
        }


class BaseProcessor(ABC):
    """Base bill processor abstract class"""
    
    def __init__(self, db_path: str = "billing.sqlite"):
        self.db_path = db_path
    
    @abstractmethod
    def can_process(self, file_path: str) -> bool:
        """
        Determine if the specified file can be processed
        
        Args:
            file_path (str): File path
            
        Returns:
            bool: Whether the file can be processed
        """
        pass
    
    @abstractmethod
    def process_file(self, file_path: str) -> List[BillRecord]:
        """
        Process bill file and return list of bill records
        
        Args:
            file_path (str): File path
            
        Returns:
            List[BillRecord]: List of bill records
        """
        pass
    
    def save_records(self, records: List[BillRecord]) -> int:
        """
        Save bill records to database (supports upsert operation)
        
        Args:
            records (List[BillRecord]): List of bill records
            
        Returns:
            int: Number of successfully saved records
        """
        if not records:
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            for record in records:
                try:
                    # Update UPDATE_TIME to current time
                    record.update_time = int(datetime.now().timestamp())
                    
                    # Check if record already exists (based on ID)
                    cursor.execute("SELECT ID FROM BILL WHERE ID = ?", (record.id,))
                    existing_record = cursor.fetchone()
                    
                    record_dict = record.to_dict()
                    
                    if existing_record:
                        # Record exists, perform update operation
                        update_columns = [col for col in record_dict.keys() if col != 'ID']
                        set_clause = ', '.join([f"{col} = ?" for col in update_columns])
                        values = [record_dict[col] for col in update_columns] + [record.id]
                        
                        sql = f"UPDATE BILL SET {set_clause} WHERE ID = ?"
                        cursor.execute(sql, values)
                        print(f"Updated record: {record.id}")
                    else:
                        # Record does not exist, perform insert operation
                        columns = ', '.join(record_dict.keys())
                        placeholders = ', '.join(['?' for _ in record_dict])
                        
                        sql = f"INSERT INTO BILL ({columns}) VALUES ({placeholders})"
                        cursor.execute(sql, list(record_dict.values()))
                        print(f"Inserted record: {record.id}")
                    
                    saved_count += 1
                    
                except sqlite3.Error as e:
                    print(f"Error saving record: {e}")
                    continue
            
            conn.commit()
            return saved_count
            
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_max_update_time(self) -> int:
        """
        Get the maximum UPDATE_TIME value from database
        
        Returns:
            int: Maximum UPDATE_TIME timestamp, returns 0 if no records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT MAX(UPDATE_TIME) FROM BILL")
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                return result[0]
            else:
                return 0
                
        except sqlite3.Error as e:
            print(f"Error querying maximum UPDATE_TIME: {e}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()
    
    def process_and_save(self, file_path: str) -> int:
        """
        Process file and save to database
        
        Args:
            file_path (str): File path
            
        Returns:
            int: Number of successfully saved records
        """
        print(f"Starting to process file: {file_path}")
        
        try:
            # Process file
            records = self.process_file(file_path)
            print(f"Parsed {len(records)} records from file")
            
            if not records:
                print("No valid bill records found")
                return 0
            
            # Save to database
            saved_count = self.save_records(records)
            print(f"Successfully saved {saved_count} records to database")
            
            return saved_count
            
        except Exception as e:
            print(f"Error processing file: {e}")
            return 0
