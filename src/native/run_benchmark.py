#!/usr/bin/env python3
"""
标准 Benchmark 运行脚本

用法:
    python run_benchmark.py                          # 运行默认 harness
    python run_benchmark.py --rerun                   # 强制重新运行
    python run_benchmark.py harness_v8_0_standard.py  # 指定 harness 文件
"""

import os
import sys
import re
import argparse

def get_api_key():
    """获取 API key"""
    # 优先从环境变量
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if api_key:
        return api_key
    
    # 从现有 harness 文件中提取
    harness_files = [
        "harness_v12_0.py",
        "harness_v8_0_standard.py",
        "harness_v9_0_extended.py"
    ]
    
    for hf in harness_files:
        if os.path.exists(hf):
            try:
                with open(hf, 'r') as f:
                    content = f.read()
                match = re.search(r'api_key = "([^"]+)"', content)
                if match:
                    return match.group(1)
            except:
                pass
    
    return None

def find_harness_class(filepath):
    """从文件内容中推断 harness 类名"""
    patterns = [
        (r'class\s+HarnessV(\d+[_\.]\d*)\w*', 'HarnessV{}'),
        (r'class\s+(\w*Harness\w*)', r'\1'),
    ]
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    for pattern, template in patterns:
        match = re.search(pattern, content)
        if match:
            if '{}' in template:
                return template.format(match.group(1))
            return match
    
    return None

def run_harness(harness_file, force_rerun=False):
    """运行指定的 harness"""
    print(f"\n{'='*60}")
    print(f"Running: {harness_file}")
    print(f"{'='*60}")
    
    api_key = get_api_key()
    if not api_key:
        print("Error: Could not find API key")
        return False
    
    # 导入 harness 模块
    module_name = harness_file.replace('.py', '')
    try:
        # 动态导入
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, harness_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 查找 harness 类
        harness_class = None
        for name in dir(module):
            if name.startswith('Harness'):
                harness_class = getattr(module, name)
                break
        
        if not harness_class:
            print(f"Error: Could not find Harness class in {harness_file}")
            return False
        
        print(f"Found harness class: {harness_class.__name__}")
        
        # 创建并运行
        harness = harness_class(api_key)
        
        if hasattr(harness, 'run_benchmark'):
            result = harness.run_benchmark(force_rerun=force_rerun)
            print(f"\n{'='*60}")
            print(f"RESULT: {result['summary'].harness_version}")
            print(f"{'='*60}")
            print(f"Composite: {result['summary'].composite_score:.2f}")
            print(f"Core: {result['summary'].core_avg_score:.2f}")
            print(f"Gen: {result['summary'].gen_avg_score:.2f}")
            print(f"Actionability: {result['summary'].avg_actionability_level:.2f}")
            return True
        else:
            print(f"Error: Harness class {harness_class.__name__} has no run_benchmark method")
            return False
            
    except Exception as e:
        print(f"Error loading harness: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='Run benchmark harness')
    parser.add_argument('--rerun', action='store_true', help='Force rerun all tasks')
    parser.add_argument('--list', action='store_true', help='List available harness files')
    parser.add_argument('harness', nargs='?', help='Harness file to run')
    
    args = parser.parse_args()
    
    if args.list:
        # 列出可用的 harness 文件
        harness_files = sorted([f for f in os.listdir('.') if f.startswith('harness_v') and f.endswith('.py')])
        print("Available harness files:")
        for f in harness_files:
            print(f"  - {f}")
        return
    
    # 确定要运行的 harness
    if args.harness:
        harness_file = args.harness
    else:
        # 默认运行最新版本
        harness_files = sorted([f for f in os.listdir('.') if f.startswith('harness_v') and f.endswith('.py')])
        if harness_files:
            harness_file = harness_files[-1]
            print(f"No harness specified, using latest: {harness_file}")
        else:
            print("No harness files found")
            return
    
    if not os.path.exists(harness_file):
        print(f"Harness file not found: {harness_file}")
        return
    
    success = run_harness(harness_file, force_rerun=args.rerun)
    
    if success:
        print(f"\n✓ Benchmark completed successfully")
    else:
        print(f"\n✗ Benchmark failed")
        sys.exit(1)

if __name__ == "__main__":
    main()