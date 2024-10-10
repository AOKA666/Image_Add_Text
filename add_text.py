from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import time

def get_dominant_color(image, box=None):
    if box:
        x0, y0, x1, y1 = box
        im = image.crop(box)
    else:
        im = image.copy()
    im = im.convert('RGB')
    im = im.resize((32, 32), Image.Resampling.LANCZOS)  # 使用 Image.Resampling.LANCZOS
    im = np.array(im)

    # 计算主导颜色
    dominant_color = np.mean(im, axis=(0, 1)).astype(int)
    return tuple(dominant_color)

def calculate_brightness(color):
    # 确保color是一个三元组
    if isinstance(color, np.ndarray):
        color = tuple(color)
    return sum([c/255.0 for c in color]) / 3  # 返回颜色的亮度值

def add_text_to_image(image_path, text, output_path, font_path, font_size=24, line_spacing=5, top_margin=0):
    # 打开图片
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)

    # 获取图片的宽度和高度
    width, height = image.size

    # 根据逗号分割文本
    sentences = text.strip('。').split('，')

    # 初始化lines列表
    lines = []
    current_line = ''
    
    # 不分段落是否超出宽度限制
    bbox_full = draw.textbbox((0, 0), text, font=font)
    text_width_full = bbox_full[2] - bbox_full[0]
    if text_width_full > width * 0.75 or (width - text_width_full) < width * 0.125:
        longest_sentence = max(sentences, key=len)
        bbox = draw.textbbox((0, 0), longest_sentence, font=font)
        text_width = bbox[2] - bbox[0]
        flag = True
        while flag:
            if text_width > width * 0.75 or (width - text_width) < width * 0.125:
                font_size -= 10
                print('字体大小更改为:{}'.format(font_size))
                font = ImageFont.truetype(font_path, font_size)
                bbox = draw.textbbox((0, 0), longest_sentence, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                flag = False
                lines = sentences
    else:
        lines = [text,]

    # 绘制文本
    y_text = top_margin
    text_color = ''
    for line in lines:
        if not line.strip():
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_text = (width - text_width) / 2

        # 获取文本区域的背景颜色
        if not text_color:
            left, top, right, bottom = bbox
            background_color = get_dominant_color(image, (left, top, right, bottom))
            brightness = calculate_brightness(background_color)
            print(brightness)
            # 根据背景颜色亮度选择文字颜色
            text_color = "black" if brightness > 0.5 else "white"

        # 绘制文本
        draw.text((x_text, y_text), line, font=font, fill=text_color)

        y_text += text_height + line_spacing

    # 确保文本不会超出图片高度
    if y_text > height - font_size:
        raise ValueError("Text is too long to fit in the image.")

    # 保存图片
    image.save(output_path)


# 使用示例
if __name__ == '__main__':

    # 获取图片列表
    image_paths = []
    folder_path = './图片'
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']

    # 遍历文件夹中的文件
    for filename in os.listdir(folder_path):
        # 检查文件扩展名是否在支持的图片格式列表中
        if os.path.splitext(filename)[1].lower() in image_extensions:
            # 构建完整的文件路径
            file_path = os.path.join(folder_path, filename).replace('\\','/')
            # 将图片路径添加到列表中
            image_paths.append(file_path)

    # 获得文案列表
    text_list = []
    texts = open('./文案.txt',encoding='utf-8').readlines()
    for text in texts:
        text_list.append(text.strip('\n'))

    # 检查可用字体
    current_file_path = os.path.abspath(__file__)
    base_dir = os.path.dirname(current_file_path)
    for filename in os.listdir(base_dir):
        if os.path.splitext(filename)[1] == '.ttf':
            file_path = os.path.join(base_dir, filename).replace('\\','/')
            font_path = file_path
    
    # 执行函数
    start = time.perf_counter()
    for i in range(min(len(image_paths),len(text_list))):
        add_text_to_image(
            image_path=image_paths[i],
            text=text_list[i],
            output_path='./output/{}.jpeg'.format(time.time()),
            font_path=font_path,
            font_size=80,
            top_margin=50
        )
        print('已完成{}个'.format(i+1))
    end = time.perf_counter()
    print('全部完成，用时{:.2f}秒'.format(end-start))