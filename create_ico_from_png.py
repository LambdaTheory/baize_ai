import os
from PIL import Image

def create_ico_from_png(png_path, ico_path):
    """
    从PNG文件创建一个包含多种分辨率的ICO文件。

    Args:
        png_path (str): 源PNG文件的路径。
        ico_path (str): 输出ICO文件的路径。
    """
    try:
        # 打开高分辨率PNG图像
        img = Image.open(png_path)
    except FileNotFoundError:
        print(f"错误: 源文件未找到 - {png_path}")
        return

    # 定义需要包含在ICO文件中的标准尺寸
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)]
    
    # 保存为ICO格式，Pillow会自动处理多尺寸的保存
    try:
        img.save(ico_path, format='ICO', sizes=sizes)
        print(f"成功创建ICO文件: {ico_path}")
    except Exception as e:
        print(f"创建ICO文件时发生错误: {e}")

if __name__ == '__main__':
    # 定义源PNG和目标ICO路径
    source_png = os.path.join('assets', 'icons', 'baize_icon_1024x1024.png')
    output_ico = os.path.join('assets', 'icons', 'baize_app_icon_generated.ico')
    
    print("开始生成高质量ICO文件...")
    create_ico_from_png(source_png, output_ico)
    print("生成完成。") 