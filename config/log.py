import logging

def setup_logging(log_file):
    # 创建日志器
    logger = logging.getLogger()
    # 设置日志级别
    logger.setLevel(logging.INFO)

    # 防止重复写日志，这里进行判断，若logger.handlers列表为空则添加
    if not logger.handlers:
         # 创建控制台处理器
         sh = logging.StreamHandler()
         # 将控制台处理器放到日志器中
         logger.addHandler(sh)

         # 创建文件处理器
         fh = logging.FileHandler(log_file, encoding='utf-8')
         # 将文件处理器放到日志器中
         logger.addHandler(fh)

         # 根据格式，创建格式器
         fmt1 = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
         formatter1 = logging.Formatter(fmt1)
         fmt2 = "%(asctime)s - %(filename)s - %(levelname)s: %(message)s"
         formatter2 = logging.Formatter(fmt2)

         # 给控制台处理器设置格式
         sh.setFormatter(formatter1)
         # 给文件处理器设置格式
         fh.setFormatter(formatter2)

    return logger


if __name__ == "__main__":
    # 测试示例：创建名为app.log的日志文件并输出日志信息
    logger = setup_logging("logs/app.log")
    logger.debug("this is a debug msg")
    logger.info("this is a info msg")
    logger.warning("this is a warning msg")
    logger.error("this is a error msg")
    logger.critical("this is a critical msg")
