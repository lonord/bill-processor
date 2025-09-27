#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Pay Bill Processor
Process WeChat Pay bill Excel files
"""

import os
import re
from datetime import datetime
from typing import List
from .base_processor import BaseProcessor, BillRecord

try:
    import pandas as pd
except ImportError:
    print("Warning: pandas library is required to process Excel files")
    print("Please run: pip install pandas openpyxl")
    pd = None


class WechatProcessor(BaseProcessor):
    """WeChat Pay bill processor"""
    
    def can_process(self, file_path: str) -> bool:
        """
        Determine if the specified file can be processed
        Matching rule: filename starts with wechat_ and ends with .xlsx
        """
        if not os.path.exists(file_path):
            return False
        
        filename = os.path.basename(file_path)
        return filename.startswith('wechat_') and filename.endswith('.xlsx')
    
    def process_file(self, file_path: str) -> List[BillRecord]:
        """
        Process WeChat Pay bill file
        """
        records = []
        
        if pd is None:
            print("Error: pandas library is required to process Excel files")
            return records
        
        try:
            # First read file to find header row
            df_raw = pd.read_excel(file_path, header=None)
            header_row = self._find_header_row(df_raw)
            
            if header_row is None:
                print("Header row not found")
                return records
            
            # Re-read file using found header row
            df = pd.read_excel(file_path, header=header_row)
            
            # Find key columns
            time_col = self._find_column(df.columns, ['交易时间'])
            amount_col = self._find_column(df.columns, ['金额(元)'])
            type_col = self._find_column(df.columns, ['交易类型'])
            counterpart_col = self._find_column(df.columns, ['交易对方'])
            product_col = self._find_column(df.columns, ['商品'])
            income_expense_col = self._find_column(df.columns, ['收/支'])
            transaction_id_col = self._find_column(df.columns, ['交易单号'])
            note_col = self._find_column(df.columns, ['备注'])
            
            for _, row in df.iterrows():
                try:
                    # Parse time
                    time_str = str(row[time_col]) if time_col and pd.notna(row[time_col]) else ""
                    if not time_str or time_str == 'nan':
                        continue
                    
                    # Parse amount
                    amount_str = str(row[amount_col]) if amount_col and pd.notna(row[amount_col]) else "0"
                    amount = self._parse_amount(amount_str)
                    
                    # Parse income/expense, set amount as negative for income
                    income_expense = str(row[income_expense_col]) if income_expense_col and pd.notna(row[income_expense_col]) else ""
                    if income_expense == "收入":
                        amount = -abs(amount)
                    
                    # Parse transaction type, set type as consumption for merchant consumption, otherwise transfer
                    transaction_type = str(row[type_col]) if type_col and pd.notna(row[type_col]) else "未知"
                    if transaction_type == "商户消费":
                        bill_type = "消费"
                    else:
                        bill_type = "转账"
                    
                    # Parse info: counterpart + @ + product
                    counterpart = str(row[counterpart_col]) if counterpart_col and pd.notna(row[counterpart_col]) else ""
                    product = str(row[product_col]) if product_col and pd.notna(row[product_col]) else ""
                    if counterpart == 'nan':
                        counterpart = ""
                    if product == 'nan':
                        product = ""
                    
                    info = f"{counterpart}@{product}" if counterpart or product else ""
                    
                    # Parse transaction ID as ID
                    transaction_id = str(row[transaction_id_col]) if transaction_id_col and pd.notna(row[transaction_id_col]) else ""
                    if transaction_id == 'nan':
                        transaction_id = ""
                    
                    # Parse note
                    note = str(row[note_col]) if note_col and pd.notna(row[note_col]) else ""
                    if note == 'nan':
                        note = ""
                    
                    # Create bill record
                    record = BillRecord(
                        time=time_str,
                        amount=amount,
                        currency="CNY",
                        bill_type=bill_type,
                        info=info,
                        note=note,
                        source="wechat"
                    )
                    
                    # Set ID as transaction ID
                    if transaction_id:
                        record.id = transaction_id
                    
                    records.append(record)
                    
                except Exception as e:
                    print(f"Error parsing row data: {e}")
                    continue
        
        except Exception as e:
            print(f"Error reading Excel file: {e}")
        
        return records
    
    def _find_header_row(self, df):
        """Find header row containing transaction time, transaction type and other columns"""
        for i, row in df.iterrows():
            row_str = ' '.join([str(x) for x in row.tolist() if pd.notna(x)])
            if '交易时间' in row_str and '交易类型' in row_str:
                return i
        return None
    
    def _find_column(self, columns, keywords):
        """Find column containing keywords"""
        for col in columns:
            for keyword in keywords:
                if keyword in str(col):
                    return col
        return None
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string, remove currency symbols"""
        if not amount_str or amount_str == 'nan':
            return 0.0
        
        # Remove all non-numeric characters (including currency symbols, commas, etc., keep minus sign and decimal point)
        cleaned = re.sub(r'[^\d.-]', '', str(amount_str))
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
