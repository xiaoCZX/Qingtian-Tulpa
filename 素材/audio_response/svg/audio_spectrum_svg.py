#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频频谱图SVG生成器
支持多种音频格式，生成可定制的SVG频谱图
"""

import os
import sys
import numpy as np
import librosa
import toml
from pathlib import Path
from typing import Tuple, List
from tqdm import tqdm


class AudioSpectrumSVG:
    """音频频谱图SVG生成器类"""
    
    def __init__(self, config_path: str = "config.toml"):
        """
        初始化生成器
        
        Args:
            config_path: TOML配置文件路径
        """
        self.config = self._load_config(config_path)
        self.audio_data = None
        self.sample_rate = None
        
    def _load_config(self, config_path: str) -> dict:
        """加载TOML配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
            return config
        except FileNotFoundError:
            print(f"错误: 配置文件 '{config_path}' 不存在")
            sys.exit(1)
        except Exception as e:
            print(f"错误: 无法读取配置文件: {e}")
            sys.exit(1)
    
    def load_audio(self, audio_file: str = None) -> Tuple[np.ndarray, int]:
        """
        加载音频文件
        
        Args:
            audio_file: 音频文件路径，如果为None则从配置文件读取
            
        Returns:
            音频数据和采样率的元组
        """
        if audio_file is None:
            audio_file = self.config['audio']['input_file']
        
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件不存在: {audio_file}")
        
        # 获取文件扩展名
        ext = os.path.splitext(audio_file)[1].lower()
        supported_formats = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']
        
        if ext not in supported_formats:
            raise ValueError(f"不支持的音频格式: {ext}。支持的格式: {', '.join(supported_formats)}")
        
        print(f"正在加载音频文件: {audio_file}")
        
        # 使用librosa加载音频，自动处理多种格式
        self.audio_data, self.sample_rate = librosa.load(audio_file, sr=None, mono=True)
        
        duration = len(self.audio_data) / self.sample_rate
        print(f"音频加载完成 - 时长: {duration:.2f}秒, 采样率: {self.sample_rate}Hz")
        
        return self.audio_data, self.sample_rate
    
    def calculate_spectrum(self) -> List[float]:
        """
        计算音频频谱
        
        Returns:
            频谱条高度列表
        """
        if self.audio_data is None:
            raise ValueError("请先加载音频文件")
        
        # 获取配置参数
        time_window = self.config['spectrum']['time_window']
        num_bars = self.config['spectrum']['num_bars']
        bars_per_second = self.config['spectrum']['bars_per_second']
        freq_min = self.config['spectrum']['freq_min']
        freq_max = self.config['spectrum']['freq_max']
        
        # 计算音频时长
        duration = len(self.audio_data) / self.sample_rate
        
        # 确定频谱条数量
        if num_bars == 0:
            num_bars = int(duration * bars_per_second)
        
        print(f"生成 {num_bars} 个频谱条")
        
        with tqdm(total=100, desc="计算频谱", unit="%") as pbar:
            # 计算每个频谱条对应的时间窗口
            hop_length = int(self.sample_rate * time_window)
            n_fft = min(2048, hop_length * 2)
            pbar.update(20)
            
            # 计算短时傅里叶变换（STFT）
            stft = librosa.stft(self.audio_data, n_fft=n_fft, hop_length=hop_length)
            magnitude = np.abs(stft)
            pbar.update(40)
            
            # 获取频率bins
            freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=n_fft)
            
            # 选择频率范围内的bins
            freq_mask = (freqs >= freq_min) & (freqs <= freq_max)
            magnitude_filtered = magnitude[freq_mask, :]
            pbar.update(20)
            
            # 对每个时间帧，计算能量平均值
            energy = np.mean(magnitude_filtered, axis=0)
            pbar.update(20)
        
        # 如果需要的频谱条数量不同于计算出的帧数，进行重采样
        if len(energy) != num_bars:
            # 使用线性插值重采样
            x_old = np.linspace(0, 1, len(energy))
            x_new = np.linspace(0, 1, num_bars)
            energy = np.interp(x_new, x_old, energy)
        
        # 归一化能量值到0-1范围
        if np.max(energy) > 0:
            energy = energy / np.max(energy)
        
        # 应用对数缩放以增强动态范围
        energy = np.log1p(energy * 10) / np.log1p(10)
        
        return energy.tolist()
    
    def generate_svg(self, spectrum: List[float], output_file: str = None) -> str:
        """
        生成SVG频谱图
        
        Args:
            spectrum: 频谱数据列表
            output_file: 输出文件路径，如果为None则从配置文件读取
            
        Returns:
            SVG内容字符串
        """
        if output_file is None:
            output_file = self.config['audio']['output_file']
        
        # 获取SVG配置
        svg_config = self.config['svg']
        bar_width = svg_config['bar_width']
        bar_spacing = svg_config['bar_spacing']
        bar_color = svg_config['bar_color']
        border_radius = svg_config['border_radius']
        min_bar_height = svg_config['min_bar_height']
        max_bar_height_percent = svg_config['max_bar_height_percent']
        background_color = svg_config.get('background_color', '')
        
        # 获取对齐配置
        vertical_align = self.config['alignment']['vertical_align']
        
        # 计算SVG尺寸
        num_bars = len(spectrum)
        svg_width = num_bars * (bar_width + bar_spacing) - bar_spacing
        svg_height = svg_config['height']
        
        # 更新实际宽度
        if svg_config['width'] == 0 or svg_config['width'] < svg_width:
            svg_width = svg_width
        else:
            svg_width = svg_config['width']
        
        # 计算最大频谱条高度
        max_bar_height = svg_height * (max_bar_height_percent / 100.0)
        
        # 开始生成SVG
        svg_lines = []
        svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">')
        
        # 添加背景色（如果指定）
        if background_color:
            svg_lines.append(f'  <rect width="{svg_width}" height="{svg_height}" fill="{background_color}"/>')
        
        svg_lines.append('  <g id="spectrum">')
        
        # 生成每个频谱条
        x_offset = 0
        with tqdm(total=len(spectrum), desc="生成SVG", unit="条") as pbar:
            for i, energy in enumerate(spectrum):
                # 计算频谱条高度
                bar_height = max(min_bar_height, energy * max_bar_height)
                
                # 根据对齐方式计算y坐标
                if vertical_align == 'center':
                    y = (svg_height - bar_height) / 2
                elif vertical_align == 'top':
                    y = 0
                elif vertical_align == 'bottom':
                    y = svg_height - bar_height
                else:
                    # 默认居中
                    y = (svg_height - bar_height) / 2
                
                # 生成矩形元素
                if border_radius > 0:
                    svg_lines.append(
                        f'    <rect id="bar_{i}" width="{bar_width}" height="{bar_height:.2f}" '
                        f'x="{x_offset}" y="{y:.2f}" fill="{bar_color}" rx="{border_radius}" ry="{border_radius}"/>'
                    )
                else:
                    svg_lines.append(
                        f'    <rect id="bar_{i}" width="{bar_width}" height="{bar_height:.2f}" '
                        f'x="{x_offset}" y="{y:.2f}" fill="{bar_color}"/>'
                    )
                
                x_offset += bar_width + bar_spacing
                pbar.update(1)
        
        svg_lines.append('  </g>')
        svg_lines.append('</svg>')
        
        svg_content = '\n'.join(svg_lines)
        
        # 保存SVG文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"SVG文件已生成: {output_file}")
        print(f"SVG尺寸: {svg_width}x{svg_height}")
        
        return svg_content
    
    def process(self, audio_file: str = None, output_file: str = None):
        """
        处理音频并生成SVG
        
        Args:
            audio_file: 音频文件路径
            output_file: 输出SVG文件路径
        """
        # 加载音频
        self.load_audio(audio_file)
        
        # 如果未指定output_file且配置中启用use_audio_name，则使用音频文件名
        if output_file is None and self.config['audio'].get('use_audio_name', False):
            if audio_file is None:
                audio_file = self.config['audio']['input_file']
            # 获取音频文件名（不含扩展名）
            audio_name = os.path.splitext(os.path.basename(audio_file))[0]
            output_file = f"{audio_name}.svg"
        
        # 计算频谱
        spectrum = self.calculate_spectrum()
        
        # 生成SVG
        self.generate_svg(spectrum, output_file)
    
    def process_batch(self, input_folder: str = None, output_folder: str = None):
        """
        批量处理文件夹中的所有音频文件
        
        Args:
            input_folder: 输入文件夹路径，如果为None则从配置文件读取
            output_folder: 输出文件夹路径，如果为None则从配置文件读取或使用输入文件夹
        """
        # 获取输入文件夹
        if input_folder is None:
            input_folder = self.config['audio'].get('input_folder', '')
        
        if not input_folder or not os.path.exists(input_folder):
            raise ValueError(f"输入文件夹不存在或未指定: {input_folder}")
        
        # 获取输出文件夹
        if output_folder is None:
            output_folder = self.config['audio'].get('output_folder', '')
        
        if not output_folder:
            output_folder = input_folder
        
        # 创建输出文件夹
        os.makedirs(output_folder, exist_ok=True)
        
        # 支持的音频格式
        supported_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']
        
        # 查找所有音频文件
        audio_files = []
        for ext in supported_extensions:
            audio_files.extend(Path(input_folder).glob(f'*{ext}'))
            audio_files.extend(Path(input_folder).glob(f'*{ext.upper()}'))
        
        if not audio_files:
            print(f"在文件夹 '{input_folder}' 中未找到支持的音频文件")
            return
        
        print(f"\n找到 {len(audio_files)} 个音频文件")
        print(f"输入文件夹: {input_folder}")
        print(f"输出文件夹: {output_folder}")
        print("-" * 60)
        
        # 批量处理
        success_count = 0
        failed_files = []
        
        for i, audio_path in enumerate(audio_files, 1):
            try:
                # 生成输出文件名
                output_filename = audio_path.stem + '.svg'
                output_path = os.path.join(output_folder, output_filename)
                
                print(f"\n[{i}/{len(audio_files)}] 处理: {audio_path.name}")
                
                # 处理单个文件
                self.process(str(audio_path), output_path)
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ 处理失败: {e}")
                failed_files.append((audio_path.name, str(e)))
        
        # 输出统计信息
        print("\n" + "=" * 60)
        print(f"批量处理完成！")
        print(f"成功: {success_count}/{len(audio_files)}")
        
        if failed_files:
            print(f"\n失败的文件 ({len(failed_files)}):")
            for filename, error in failed_files:
                print(f"  - {filename}: {error}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='音频频谱图SVG生成器')
    parser.add_argument('-c', '--config', default='config.toml', help='配置文件路径')
    parser.add_argument('-i', '--input', help='输入音频文件路径（覆盖配置文件）')
    parser.add_argument('-o', '--output', help='输出SVG文件路径（覆盖配置文件）')
    parser.add_argument('-b', '--batch', help='批量处理模式：指定输入文件夹路径')
    parser.add_argument('--output-folder', help='批量模式下的输出文件夹路径')
    
    args = parser.parse_args()
    
    # 创建生成器实例
    generator = AudioSpectrumSVG(args.config)
    
    try:
        # 判断是批量处理还是单文件处理
        if args.batch:
            # 批量处理模式
            generator.process_batch(args.batch, args.output_folder)
        else:
            # 单文件处理模式
            # 检查配置文件中是否设置了批量模式
            input_folder = generator.config['audio'].get('input_folder', '')
            if input_folder and not args.input:
                # 使用配置文件中的批量模式
                output_folder = generator.config['audio'].get('output_folder', '')
                generator.process_batch(input_folder, output_folder)
            else:
                # 单文件模式
                generator.process(args.input, args.output)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
