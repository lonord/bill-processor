#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账单处理器模块
统一管理和加载所有账单处理器
"""

from .base_processor import BaseProcessor, BillRecord
from .alipay_processor import AlipayProcessor
from .wechat_processor import WechatProcessor
from .cmbcc_processor import CmbccProcessor
from .simple_processor import SimpleProcessor

# 所有可用的处理器类
AVAILABLE_PROCESSORS = [
    AlipayProcessor,
    WechatProcessor,
    CmbccProcessor,
    SimpleProcessor
]

def get_available_processors():
    """
    获取所有可用的处理器实例
    
    Returns:
        List[BaseProcessor]: 处理器实例列表
    """
    return [processor_class() for processor_class in AVAILABLE_PROCESSORS]

def get_processor_by_name(name: str):
    """
    根据名称获取处理器类
    
    Args:
        name (str): 处理器名称
        
    Returns:
        BaseProcessor: 处理器类，如果未找到则返回None
    """
    processor_map = {
        'AlipayProcessor': AlipayProcessor,
        'WechatProcessor': WechatProcessor,
        'CmbccProcessor': CmbccProcessor,
        'SimpleProcessor': SimpleProcessor
    }
    return processor_map.get(name)

def register_processor(processor_class):
    """
    注册新的处理器类
    
    Args:
        processor_class: 处理器类
    """
    if processor_class not in AVAILABLE_PROCESSORS:
        AVAILABLE_PROCESSORS.append(processor_class)

# 导出主要类和函数
__all__ = [
    'BaseProcessor',
    'BillRecord', 
    'AlipayProcessor',
    'WechatProcessor',
    'CmbccProcessor',
    'SimpleProcessor',
    'get_available_processors',
    'get_processor_by_name',
    'register_processor',
    'AVAILABLE_PROCESSORS'
]
