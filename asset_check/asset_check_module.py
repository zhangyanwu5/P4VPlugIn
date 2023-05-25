import threading
import queue

from base_module import BaseModule
from asset_check import asset_check_ui
from asset_check.asset_check_thread import AssetCheckThread, MonitorLogThread

from PyQt5.QtCore import QTimer

UNREAL_PROCESS_NAME = "UE4Editor.exe"
ASSET_CHECK_PIPE_NAME = "\\\\.\\pipe\\ACMAssetCheckPipe"


# 资产检查模块
class AssetCheckModule(BaseModule):
    submit_list_path = ''  # 提交资产列表存储路径
    check_asset_thread = None  # 资产检查线程
    monitor_log_thread = None  # 监测日志线程
    quit_event = None  # 退出线程事件
    application = None  # 应用程序
    dialog = None  # 对话框UI
    process_log_timer = None  # tick触发器
    message_queue = None  # 消息队列

    # 初始化
    def __init__(self):
        super(AssetCheckModule, self).__init__()
        self.application = asset_check_ui.create_application()

    # 启动
    def startup_module(self, args=[]) -> bool:
        if len(args) == 0 or type(args[0]) != str:
            return False

        self.submit_list_path = args[0]

        # UI相关
        self.dialog = asset_check_ui.create_dialog()

        # 多线程相关
        self.quit_event = threading.Event()
        self.message_queue = queue.Queue()
        self.check_asset_thread = AssetCheckThread(queue=self.message_queue, quit_event=self.quit_event)
        # self.check_asset_thread.start()
        self.monitor_log_thread = MonitorLogThread(queue=self.message_queue, quit_event=self.quit_event)
        self.monitor_log_thread.start()

        # 设置定时Tick
        self.process_log_timer = QTimer()
        self.process_log_timer.timeout.connect(self.tick_process_log)
        self.process_log_timer.start(50)  # 每50毫秒执行一次

        return True

    # 关闭
    def shutdown_module(self):
        print("ShutdownModule")
        if self.process_log_timer:
            self.process_log_timer.stop()

        if self.quit_event:
            self.quit_event.set()

    # 执行函数
    def run(self, args=[]) -> bool:
        if not super(AssetCheckModule, self).run(args):
            return False

        # 初始化
        if not self.startup_module(args):
            return False

        # 显示UI
        self.dialog.show()
        self.application.exec_()

        # 关闭
        self.shutdown_module()

    # 处理日志
    def tick_process_log(self) -> None:
        try:
            log = self.message_queue.get_nowait()
            if log:
                print(log)
                self.dialog.output_log(log)
        except queue.Empty:
            pass
