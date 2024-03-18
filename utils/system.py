import psutil


# 获取系统CPU占用率，范围为0-1
def get_cpu_usage():
    return psutil.cpu_percent(interval=None) / 100
