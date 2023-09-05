import time

class GenerateList:
    def __init__(self, data_list, threshold):
        self.data_list = data_list
        self.threshold = threshold
        self.count = 0  # 记录当前阈值内执行次数
        self.list_len = len(self.data_list)  # 记录列表长度
        self.list_num = 0  # 当前列表位置
    
    @property
    def next_item(self):
        while True:
            if self.count < self.threshold:
                yield self.data_list[self.list_num]
                self.count += 1
            else:
                self.count = 0
                self.list_num = (self.list_num + 1) % self.list_len

def main():
    generator = GenerateList([1, 2, 3, 4, 5], 3).next_item
    while True:
        data = next(generator)
        time.sleep(2)
        print("获取下一条列表的内容...", data)

if __name__ == "__main__":
    main()