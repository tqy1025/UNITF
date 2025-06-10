import os
import random
import shutil


def collect_images(root_A, directory_B):
    all_images = []

    # 遍历根目录A下的一级子目录
    for entry in os.listdir(root_A):
        entry_path = os.path.join(root_A, entry)
        # 检查是否为以_analysis结尾的目录
        if os.path.isdir(entry_path) and entry.endswith('_analysis'):
            # 递归遍历该目录下的所有文件
            for foldername, _, filenames in os.walk(entry_path):
                for filename in filenames:
                    # 检查文件是否为图片
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        file_path = os.path.join(foldername, filename)
                        # 计算相对于当前一级子目录的相对路径
                        relative_path = os.path.relpath(file_path, entry_path)
                        relative_dir = os.path.dirname(relative_path)
                        dir_components = relative_dir.split(os.sep)

                        # 确保有足够多的目录层级
                        if len(dir_components) >= 6:
                            level2 = dir_components[0]
                            level3 = dir_components[1]
                            level7 = dir_components[5]
                            all_images.append((file_path, level2, level3, level7, filename))

    # 随机选取最多100张图片
    selected = random.sample(all_images, k=min(10, len(all_images)))

    # 确保目标目录存在
    if not os.path.exists(directory_B):
        os.makedirs(directory_B)

    # 复制并重命名文件
    for item in selected:
        src_path, l2, l3, l7, orig_name = item
        new_name = f"{l2}_{l3}_{l7}_{orig_name}"
        dest_path = os.path.join(directory_B, new_name)
        shutil.copy2(src_path, dest_path)
        print(f"Copied: {src_path} -> {dest_path}")


if __name__ == '__main__':
    # 使用示例
    root_A = "I:\\"  # 修改为实际的根目录路径
    directory_B = "I:\\Target_LLM_Testing\\Intervened1"  # 修改为实际的目标目录路径

    collect_images(root_A, directory_B)
