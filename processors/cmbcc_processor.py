#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
China Merchants Bank Credit Card Bill Processor
Process China Merchants Bank credit card CSV files
"""

import csv
import os
import re
from datetime import datetime
from typing import List
from .base_processor import BaseProcessor, BillRecord


class CmbccProcessor(BaseProcessor):
    """China Merchants Bank credit card bill processor"""
    
    def can_process(self, file_path: str) -> bool:
        """
        Determine if the specified file can be processed
        Matching rule: filename starts with cmbcc_ and ends with .csv
        """
        if not os.path.exists(file_path):
            return False
        
        filename = os.path.basename(file_path)
        return filename.startswith('cmbcc_') and filename.endswith('.csv')
    
    def process_file(self, file_path: str) -> List[BillRecord]:
        """
        Process China Merchants Bank credit card bill file
        """
        records = []
        
        try:
            # Extract year and month from filename
            filename = os.path.basename(file_path)
            year_month = self._extract_year_month_from_filename(filename)
            if not year_month:
                print(f"Unable to extract year and month from filename: {filename}")
                return records
            
            # Check if previous month bill file exists (check only once)
            year = year_month[:4]
            file_month = year_month[4:]
            previous_month_exists = self._check_previous_month_file_exists(year, file_month, file_path)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader, [])
                
                # Find key column indices
                time_col = self._find_column_index(headers, ['交易日', '交易时间', '时间'])
                amount_col = self._find_column_index(headers, ['人民币金额', '金额', '交易金额'])
                info_col = self._find_column_index(headers, ['交易摘要', '摘要', '商品名称', '商户名称'])
                card_col = self._find_column_index(headers, ['卡号末四位', '卡号'])
                foreign_amount_col = self._find_column_index(headers, ['交易地金额'])
                location_col = self._find_column_index_exact(headers, ['交易地'])
                
                record_sequence = 0  # Record sequence counter
                
                for row in csv_reader:
                    if len(row) < max(time_col, amount_col, info_col, card_col, foreign_amount_col, location_col) + 1:
                        continue
                    
                    try:
                        # Parse transaction summary
                        info = row[info_col] if info_col < len(row) else ""
                        
                        # Filter condition 1: Ignore records starting with "财付通-", "支付宝-"
                        if info.startswith(('财付通-', '支付宝-')):
                            continue
                        
                        # Parse RMB amount
                        amount_str = row[amount_col] if amount_col < len(row) else "0"
                        amount = self._parse_amount(amount_str)
                        
                        # Filter condition 2: Ignore records with RMB amount <= 0
                        if amount <= 0:
                            continue
                        
                        # Parse transaction date
                        time_str = row[time_col] if time_col < len(row) else ""
                        if not time_str:
                            continue
                        
                        # Process time format: from filename year-month + transaction date MMdd format
                        formatted_time = self._format_time(year_month, time_str, previous_month_exists)
                        if not formatted_time:
                            continue
                        
                        # Parse last four digits of card number
                        card_last_four = row[card_col] if card_col < len(row) else ""
                        
                        # Format info column: transaction summary + # + last four digits of card
                        formatted_info = f"{info}#{card_last_four}" if card_last_four else info
                        
                        # Parse transaction location and foreign amount
                        location = row[location_col] if location_col < len(row) else ""
                        foreign_amount_str = row[foreign_amount_col] if foreign_amount_col < len(row) else ""
                        foreign_amount = self._parse_amount(foreign_amount_str) if foreign_amount_str else 0
                        
                        # Process note column: empty by default, unless transaction location is not CN
                        note = ""
                        if location and location != "CN":
                            note = f"{foreign_amount}@{location}"
                        
                        # Generate custom ID: YYYY-MM-DD part of time column + record sequence
                        date_part = formatted_time.split(' ')[0]  # Extract YYYY-MM-DD part
                        record_sequence += 1
                        custom_id = f"{date_part}@{record_sequence}"
                        
                        # Create bill record
                        record = BillRecord(
                            time=formatted_time,
                            amount=amount,
                            currency="CNY",
                            bill_type="消费",
                            info=formatted_info,
                            note=note,
                            source="cmbcc"
                        )
                        
                        # Set custom ID
                        record.id = custom_id
                        
                        records.append(record)
                        
                    except Exception as e:
                        print(f"Error parsing row data: {e}, row content: {row}")
                        continue
        
        except Exception as e:
            print(f"Error reading CSV file: {e}")
        
        return records
    
    def _find_column_index(self, headers: List[str], keywords: List[str]) -> int:
        """Find column index containing keywords"""
        for i, header in enumerate(headers):
            for keyword in keywords:
                if keyword in header:
                    return i
        return -1
    
    def _find_column_index_exact(self, headers: List[str], keywords: List[str]) -> int:
        """Find column index with exact keyword match"""
        for i, header in enumerate(headers):
            for keyword in keywords:
                if header.strip() == keyword.strip():
                    return i
        return -1
    
    def _extract_year_month_from_filename(self, filename: str) -> str:
        """Extract year and month from filename"""
        # Match format: cmbcc_2025_07.csv
        match = re.search(r'cmbcc_(\d{4})_(\d{2})\.csv', filename)
        if match:
            year = match.group(1)
            month = match.group(2)
            return f"{year}{month}"
        return ""
    
    def _format_time(self, year_month: str, transaction_date: str, previous_month_exists: bool) -> str:
        """Format time: year-month + transaction date MMdd format, fill hours:minutes:seconds with 0"""
        if not year_month or not transaction_date:
            return ""
        
        # Extract year and month
        year = year_month[:4]
        file_month = year_month[4:]
        
        # Transaction date format is MMdd
        if len(transaction_date) == 4 and transaction_date.isdigit():
            month = transaction_date[:2]
            day = transaction_date[2:]
        else:
            return ""
        
        # Check if month matches
        if month != file_month:
            # Month mismatch, indicates record from previous month
            if not previous_month_exists:
                print(f"Skipping cross-month record: filename month {file_month}, record month {month} (previous month bill file does not exist)")
                return ""
            # January files may contain previous December records, which belong to the previous year.
            if file_month == "01" and month == "12":
                year = str(int(year) - 1)
        
        # Concatenate complete time, fill hours:minutes:seconds with 0
        return f"{year}-{month}-{day} 00:00:00"
    
    def _check_previous_month_file_exists(self, year: str, current_month: str, current_file_path: str) -> bool:
        """Check if previous month bill file exists"""
        try:
            # Calculate previous month
            current_month_int = int(current_month)
            if current_month_int == 1:
                # If current is January, previous month is December of previous year
                prev_year = str(int(year) - 1)
                prev_month = "12"
            else:
                # Other months, previous month is current month minus 1
                prev_year = year
                prev_month = f"{current_month_int - 1:02d}"
            
            # Get current file directory
            current_dir = os.path.dirname(current_file_path)
            
            # Construct previous month bill filename
            previous_month_file = f"cmbcc_{prev_year}_{prev_month}.csv"
            previous_month_path = os.path.join(current_dir, previous_month_file)
            
            # Check if file exists
            return os.path.exists(previous_month_path)
        except Exception as e:
            print(f"Error checking previous month bill file: {e}")
            return False
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string"""
        if not amount_str:
            return 0.0
        
        # Remove commas and other non-numeric characters (keep minus sign and decimal point)
        cleaned = re.sub(r'[^\d.-]', '', amount_str)
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
