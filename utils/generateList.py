import time

class GenerateList:
    def __init__(self,data_list,threshold):
        '''
        迭代器处理多key
        Args:
            List:列表
            int:阈值
        Returns:
            string
        '''
        self.data_list = data_list
        self.threshold = threshold
    
    @property
    def generate_list(self):
        last_executed_time = time.time()  # 记录上次执行时间
        count = 0  # 记录当前1分钟内执行次数
        list_len=len(self.data_list) #记录列表长度
        list_num=0 #当前列表位置
        while True:
            # 列表列数重置
            if list_num>=list_len:
                list_num=0
                count = 0
            #超阈处理
            current_time = time.time()
            if current_time - last_executed_time >= 60:
                last_executed_time = current_time
                count = 0
                list_num+=1

            if count < self.threshold:
                yield self.data_list[list_num]
                count += 1
                list_num+=1
            else:
                count=0
                yield None
            

def main():         
    generator = GenerateList([1,2,3,4,5],3).generate_list
    while True:
        data = next(generator)
        if data is not None:
            print("获取下一条列表的内容...",data)
            time.sleep(2)
        else:
            print("处理数据:", data)
            time.sleep(2)
if __name__ == "__main__":
    main()