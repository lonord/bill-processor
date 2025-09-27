#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alipay Bill Processor
Process Alipay transaction detail CSV files
"""

import csv
import os
import re
from datetime import datetime
from typing import List
from .base_processor import BaseProcessor, BillRecord


class AlipayProcessor(BaseProcessor):
    """Alipay bill processor"""
    
    def can_process(self, file_path: str) -> bool:
        """
        Determine if the specified file can be processed
        Matching rule: filename starts with alipay_ and ends with .csv
        """
        if not os.path.exists(file_path):
            return False
        
        filename = os.path.basename(file_path)
        return filename.startswith('alipay_') and filename.endswith('.csv')
    
    def process_file(self, file_path: str) -> List[BillRecord]:
        """
        Process Alipay bill file
        """
        records = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Alipay CSV files often have encoding issues, try different encodings
                content = file.read()
                
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    content = file.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='gb2312') as file:
                    content = file.read()
        
        # Split content by lines
        lines = content.split('\n')
        
        # Find data start position (skip file header information)
        data_start = 0
        for i, line in enumerate(lines):
            if '交易时间' in line and '交易分类' in line:
                data_start = i
                break
        
        if data_start == 0:
            print("Alipay data header not found")
            return records
        
        # Parse CSV data
        csv_reader = csv.reader(lines[data_start:])
        headers = next(csv_reader, [])
        
        # Find key column indices
        time_col = self._find_column_index(headers, ['交易时间'])
        amount_col = self._find_column_index(headers, ['金额'])
        category_col = self._find_column_index(headers, ['交易分类'])
        counterpart_col = self._find_column_index(headers, ['交易对方'])
        product_col = self._find_column_index(headers, ['商品说明'])
        income_expense_col = self._find_column_index(headers, ['收/支'])
        status_col = self._find_column_index(headers, ['交易状态'])
        order_id_col = self._find_column_index(headers, ['交易订单号'])
        note_col = self._find_column_index(headers, ['备注'])
        
        for row in csv_reader:
            if len(row) < max(time_col, amount_col, category_col, counterpart_col, 
                             product_col, income_expense_col, status_col, order_id_col, note_col) + 1:
                continue
            
            try:
                # Parse time
                time_str = row[time_col] if time_col < len(row) else ""
                if not time_str:
                    continue
                
                # Parse amount
                amount_str = row[amount_col] if amount_col < len(row) else "0"
                amount = self._parse_amount(amount_str)
                
                # Parse income/expense status
                income_expense = row[income_expense_col] if income_expense_col < len(row) else ""
                if income_expense == "不计收支":
                    continue
                
                # If income, set amount as negative
                if income_expense == "收入":
                    amount = -abs(amount)
                
                # Parse transaction status
                status = row[status_col] if status_col < len(row) else ""
                if status != "交易成功":
                    continue
                
                # Parse transaction category and generate type
                category = row[category_col] if category_col < len(row) else ""
                bill_type = "转账" if category == "转账红包" or category == "收入" else "消费"
                
                # Parse counterpart and product description, combine into info
                counterpart = row[counterpart_col] if counterpart_col < len(row) else ""
                product = row[product_col] if product_col < len(row) else ""
                info = f"{counterpart}@{product}" if counterpart and product else counterpart or product
                
                # Parse transaction order number as ID
                order_id = row[order_id_col] if order_id_col < len(row) else ""
                if not order_id:
                    continue
                
                # Parse note
                note = row[note_col] if note_col < len(row) else ""
                
                # Create bill record
                record = BillRecord(
                    time=time_str,
                    amount=amount,
                    currency="CNY",
                    bill_type=bill_type,
                    info=info,
                    note=note,
                    source="alipay"
                )
                
                # Set ID as transaction order number
                record.id = order_id
                
                records.append(record)
                
            except Exception as e:
                print(f"Error parsing row data: {e}, row content: {row}")
                continue
        
        return records
    
    def _find_column_index(self, headers: List[str], keywords: List[str]) -> int:
        """Find column index containing keywords"""
        for i, header in enumerate(headers):
            for keyword in keywords:
                if keyword in header:
                    return i
        return -1
    
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
