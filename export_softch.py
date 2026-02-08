

import os

# 设定要扫描的文件夹
TARGET_DIRS = ['web_interface', 'static', 'prompts', 'utils', 'tests']
# 设定要扫描的根目录文件
TARGET_FILES = ['main.py', 'requirements.txt']
# 设定输出文件名
OUTPUT_FILE = '软著申请源码_康熙大人.txt'

def is_text_file(filename):
    return filename.endswith(('.py', '.html', '.css', '.js', '.txt', '.md'))

def export_code():
    total_lines = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        # 1. 扫描根目录文件
        for filename in TARGET_FILES:
            if os.path.exists(filename):
                write_file_content(outfile, filename)
                total_lines += count_lines(filename)

        # 2. 扫描文件夹
        for d in TARGET_DIRS:
            if os.path.exists(d):
                for root, _, files in os.walk(d):
                    for file in files:
                        if is_text_file(file):
                            path = os.path.join(root, file)
                            write_file_content(outfile, path)
                            total_lines += count_lines(path)
    
    print(f"✅ 导出完成！")
    print(f"📄 文件名: {OUTPUT_FILE}")
    print(f"📊 总行数: {total_lines} 行")
    if total_lines < 3000:
        print("⚠️ 提示: 行数未满3000行，建议多写点 Prompt 或增加 HTML 注释凑数！")
    else:
        print("🎉 完美！行数达标，足以申请软著！")

def write_file_content(outfile, path):
    outfile.write(f"{'='*50}\n")
    outfile.write(f"文件路径: {path}\n")
    outfile.write(f"{'='*50}\n")
    try:
        with open(path, 'r', encoding='utf-8') as infile:
            outfile.write(infile.read())
            outfile.write("\n\n")
    except Exception as e:
        outfile.write(f"读取错误: {e}\n\n")

def count_lines(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0

if __name__ == "__main__":
    export_code()