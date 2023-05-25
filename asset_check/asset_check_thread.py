# 资产检查线程
import subprocess
import threading
import time

import psutil
import win32file

UNREAL_PROCESS_NAME = "UE4Editor.exe"
ASSET_CHECK_PIPE_NAME = "\\\\.\\pipe\\ACMAssetCheckPipe"


# 资产检查线程
class AssetCheckThread(threading.Thread):
    message_queue = None
    quit_event = None

    def __init__(self, queue, quit_event):
        super(AssetCheckThread, self).__init__()
        self.message_queue = queue
        self.quit_event = quit_event

    def run(self) -> None:
        super(AssetCheckThread, self).run()

        # 区分直接用UE还是启动Commandlet
        if self.have_unreal_progress():
            if not self.check_asset_by_named_pipe():
                self.check_asset_by_command_let()
        else:
            self.check_asset_by_command_let()

    # 输出日志（传输给主线程）
    def transfer_log(self, log: str):
        self.message_queue.put(log)

    # 检测unreal进程是否存在
    @staticmethod
    def have_unreal_progress() -> bool:
        for proc in psutil.process_iter():
            if proc.name() == UNREAL_PROCESS_NAME:
                return True

        return False

    # 通过命名管道与unreal进行通信来进行asset check
    @staticmethod
    def check_asset_by_named_pipe() -> None:
        file_handle = win32file.CreateFile(ASSET_CHECK_PIPE_NAME,
                                           win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                           win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
                                           None,
                                           win32file.OPEN_EXISTING,
                                           win32file.FILE_ATTRIBUTE_NORMAL,
                                           None)

        data = "C:\\Users\\yanwuzhang\\Desktop\\test_path.txt"
        data_size = len(data)
        win32file.WriteFile(file_handle, struct.pack('i', data_size))
        win32file.WriteFile(file_handle, data.encode())

        # 接收数据
        result = win32file.ReadFile(file_handle, 4096)
        decode_result = result[1].decode('utf-16')
        print(decode_result)

    # 通过command let来进行asset check
    def check_asset_by_command_let(self) -> None:
        editor_path = "C:\\Work\\Git\\TOPXACProj\\ACMEngine\\Engine\\Binaries\\Win64\\UE4Editor.exe"
        project_path = "C:\\Work\\Perforce\\ACMobileClient\\ACMobileClient.uproject"
        startupinfo = subprocess.STARTUPINFO()
        # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # startupinfo.wShowWindow = subprocess.SW_HIDE
        commandlet_process = subprocess.Popen(
            [editor_path, project_path, "-run=AssetCheck",
             "filelist=C:\\Users\\yanwuzhang\\Desktop\\test_path.txt"],
            startupinfo=startupinfo)

        self.transfer_log("开始准备进行资产检查...")
        self.transfer_log("检查器启动时间可能较久，请耐心等待哦♥")

        # 判断主进程是否通知结束
        while not self.quit_event.is_set():
            time.sleep(0.1)

        # 主进程通知结束时，如果commandlet_process还未执行完，则强制关闭
        if commandlet_process.poll() is None:
            commandlet_process.terminate()


# 监测日志线程
class MonitorLogThread(threading.Thread):
    message_queue = None
    quit_event = None

    def __init__(self, queue, quit_event):
        super(MonitorLogThread, self).__init__()
        self.message_queue = queue
        self.quit_event = quit_event

    def run(self) -> None:
        super(MonitorLogThread, self).run()

        with open("C:\\Work\\Perforce\\ACMobileClient\\log.log", "r+") as logfile:
            while not self.quit_event.is_set():
                line = logfile.readline()
                if not line:
                    time.sleep(0.2)
                    continue

                logfile.seek(0, 2)
                print(line.strip())
