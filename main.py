from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.text import LabelBase
import psutil
import platform
import os

# 注册中文字体 - Android版本使用系统默认字体
try:
    # Windows版本
    if platform.system() == 'Windows':
        LabelBase.register(name="CustomFont", 
                           fn_regular=r"C:\Windows\Fonts\msyh.ttc")
    else:
        # Android等其他系统使用默认字体
        LabelBase.register(name="CustomFont")
except:
    # 如果字体注册失败，使用默认字体
    pass

class SystemInfoApp(App):
    def __init__(self):
        super().__init__()
        self.info_label = None
        
    def build(self):
        # 创建主布局
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title = Label(
            text='系统信息查看器',
            size_hint_y=None,
            height=50,
            font_size='20sp',
            font_name='CustomFont',
            bold=True
        )
        main_layout.add_widget(title)
        
        # 刷新按钮
        refresh_btn = Button(
            text='刷新信息',
            size_hint_y=None,
            height=50,
            font_name='CustomFont',
            background_color=(0.2, 0.6, 1, 1)
        )
        refresh_btn.bind(on_press=self.refresh_info)
        main_layout.add_widget(refresh_btn)
        
        # 信息显示区域
        self.info_label = Label(
            text='点击刷新按钮查看系统信息',
            size_hint_y=None,
            text_size=(None, None),
            font_name='CustomFont',
            halign='left',
            valign='top',
            markup=True
        )
        # 绑定text_size到width，使文本能够自动换行
        self.info_label.bind(width=lambda *x: self.info_label.setter('text_size')(self.info_label, (self.info_label.width, None)))
        
        # 使用滚动视图包装信息标签
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.info_label)
        main_layout.add_widget(scroll_view)
        
        # 初始刷新
        self.refresh_info()
        
        # 自动刷新
        Clock.schedule_interval(self.auto_refresh, 5)  # 每5秒刷新一次
        
        return main_layout
    
    def get_system_info(self):
        """获取系统信息"""
        info = []
        
        # 系统基本信息
        info.append("=== 系统基本信息 ===")
        try:
            info.append(f"操作系统: {platform.system()} {platform.release()}")
            info.append(f"系统版本: {platform.version()}")
            info.append(f"机器类型: {platform.machine()}")
            info.append(f"处理器: {platform.processor()}")
        except Exception as e:
            info.append(f"系统信息获取失败: {str(e)}")
        info.append("")
        
        # CPU 信息
        info.append("=== CPU 信息 ===")
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            info.append(f"CPU 使用率: {cpu_percent}%")
            info.append(f"CPU 核心数: {cpu_count}")
            if cpu_freq:
                info.append(f"CPU 频率: {cpu_freq.current:.1f} MHz")
        except Exception as e:
            info.append(f"CPU信息获取失败: {str(e)}")
        info.append("")
        
        # 内存信息
        info.append("=== 内存信息 ===")
        try:
            memory = psutil.virtual_memory()
            info.append(f"总内存: {memory.total / (1024**3):.2f} GB")
            info.append(f"可用内存: {memory.available / (1024**3):.2f} GB")
            info.append(f"已用内存: {memory.used / (1024**3):.2f} GB")
            info.append(f"内存使用率: {memory.percent}%")
        except Exception as e:
            info.append(f"内存信息获取失败: {str(e)}")
        info.append("")
        
        # 磁盘信息
        info.append("=== 存储信息 ===")
        try:
            # 根据操作系统选择磁盘路径
            if platform.system() == 'Windows':
                disk_path = 'C:'
            elif platform.system() == 'Android':
                # Android设备通常使用内部存储
                disk_path = '/data'
            else:
                disk_path = '/'
                
            disk = psutil.disk_usage(disk_path)
            info.append(f"总存储空间: {disk.total / (1024**3):.2f} GB")
            info.append(f"可用存储空间: {disk.free / (1024**3):.2f} GB")
            info.append(f"已用存储空间: {disk.used / (1024**3):.2f} GB")
            info.append(f"存储使用率: {disk.percent}%")
        except Exception as e:
            info.append(f"存储信息获取失败: {str(e)}")
        info.append("")
        
        # 网络信息
        info.append("=== 网络信息 ===")
        try:
            network = psutil.net_io_counters()
            info.append(f"发送字节: {network.bytes_sent / (1024**2):.2f} MB")
            info.append(f"接收字节: {network.bytes_recv / (1024**2):.2f} MB")
        except Exception as e:
            info.append(f"网络信息获取失败: {str(e)}")
        info.append("")
        
        # 电池信息 (移动设备更重要)
        try:
            battery = psutil.sensors_battery()
            if battery:
                info.append("=== 电池信息 ===")
                info.append(f"电池电量: {battery.percent}%")
                info.append(f"是否充电: {'是' if battery.power_plugged else '否'}")
                if battery.secsleft != -1 and battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    hours = battery.secsleft // 3600
                    minutes = (battery.secsleft % 3600) // 60
                    info.append(f"剩余时间: {hours}小时{minutes}分钟")
                info.append("")
        except Exception as e:
            # 电池信息在某些设备上可能不可用
            pass
        
        return '\n'.join(info)
    
    def refresh_info(self, instance=None):
        """刷新系统信息"""
        if self.info_label:
            info_text = self.get_system_info()
            self.info_label.text = info_text
            # 动态计算需要的高度
            self.info_label.texture_update()
            self.info_label.height = self.info_label.texture_size[1] + 20  # 添加一些padding
    
    def auto_refresh(self, dt):
        """自动刷新"""
        self.refresh_info()

if __name__ == '__main__':
    SystemInfoApp().run() 