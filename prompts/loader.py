#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模块名称: Prompt Loader (提示词加载器)
描述: 负责从文件系统中读取、解析和缓存系统提示词。
"""

import os
import logging

# 获取当前模块的 logger
logger = logging.getLogger("HuiyanEngine")

def load_system_prompt(filename='system_instruction.txt'):
    """
    从指定文件加载系统提示词
    :param filename: 提示词文件名，默认在 prompts 目录下
    :return: 提示词字符串 content
    """
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filename)
    
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"提示词文件不存在: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.strip():
            logger.warning(f"警告: 提示词文件 {filename} 为空！")
            return "You are a helpful coding assistant."
            
        return content

    except Exception as e:
        logger.error(f"加载提示词失败: {e}")
        # 返回一个保底的 Prompt，防止系统崩溃
        return "你是一个编程助手。"