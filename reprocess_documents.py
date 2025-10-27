#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重新处理所有已上传文档的统计信息
"""

import os
import json
import glob
from app.document_processor import DocumentProcessor

def reprocess_all_documents():
    """重新处理所有文档的统计信息"""
    processor = DocumentProcessor()
    
    # 查找所有文档元数据文件
    document_files = glob.glob("data/document_*.json")
    
    if not document_files:
        print("没有找到已上传的文档")
        return
    
    print(f"找到 {len(document_files)} 个文档需要重新处理")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for doc_file in document_files:
        try:
            # 读取原始文档信息
            with open(doc_file, 'r', encoding='utf-8') as f:
                doc_info = json.load(f)
            
            doc_id = doc_info['id']
            filename = doc_info['filename']
            file_path = doc_info['file_path']
            
            print(f"\n处理文档: {filename}")
            print(f"文档ID: {doc_id}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"  警告: 文件不存在 {file_path}")
                error_count += 1
                continue
            
            # 重新处理文档
            result = processor.process_document(file_path, filename)
            new_metadata = result["metadata"]
            
            # 显示统计变化
            old_word_count = doc_info['metadata'].get('word_count', 0)
            old_paragraph_count = doc_info['metadata'].get('paragraph_count', 0)
            
            print(f"  原统计: 字数={old_word_count}, 段落={old_paragraph_count}")
            print(f"  新统计: 字数={new_metadata['word_count']}, 段落={new_metadata['paragraph_count']}")
            
            # 更新文档元数据
            doc_info['metadata'] = new_metadata
            
            # 保存更新后的文档信息
            with open(doc_file, 'w', encoding='utf-8') as f:
                json.dump(doc_info, f, ensure_ascii=False, indent=2)
            
            # 同时更新segments文件（如果需要）
            segments_file = f"data/segments_{doc_id}.json"
            if os.path.exists(segments_file):
                # 保存新的segments
                with open(segments_file, 'w', encoding='utf-8') as f:
                    json.dump(result["segments"], f, ensure_ascii=False, indent=2)
                print(f"  更新了 {len(result['segments'])} 个文本段")
            
            success_count += 1
            print(f"  ✓ 成功更新")
            
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            error_count += 1
            continue
    
    print("\n" + "=" * 60)
    print(f"处理完成！")
    print(f"成功: {success_count} 个文档")
    print(f"失败: {error_count} 个文档")
    
    # 重新构建向量索引（如果需要）
    if success_count > 0:
        print("\n提示: 文档已更新，可能需要重新构建向量索引")
        print("可以通过API调用 /api/build-knowledge-graph 重新构建")

if __name__ == "__main__":
    print("文档重新统计工具")
    print("=" * 60)
    reprocess_all_documents()