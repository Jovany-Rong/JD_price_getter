# coding: utf-8

import config

import requests
import csv
import json
from datetime import datetime
import os

class JdGetter(object):
    
    def __init__(self):
        
        self.session = requests.Session() # 初始化一个 requests Session 方便后续使用
        self.skuIds = config.SKUIDS # 读取配置文件
        
        # 创建 headers ，填写 UA ，模拟真实用户
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.47'
        }
    
    
    def get_sku_info(self, skuId): # 传入 skuId 作为参数
        
        # 生成商品主页 url
        skuUrl = 'https://item.jd.com/%s.html' % skuId
        
        # 请求商品主页，获取响应文本，并找到 class="sku-name" 这个div的文本 
        r = self.session.get(skuUrl, headers=self.headers)
        
        # 这里用最简单的字符串切分的方式处理，当然使用正则、xpath解析等方式均可
        skuName = r.text.split('<div class="sku-name">')[1].split('</div>')[0].strip()
        # 测试发现部分商品名称左侧可能有图片，如果有图片，把它去掉
        if "<img" in skuName:
            skuName = skuName.split('/>')[1].strip()
                
        # 生成商品价格查询 url
        skuPriceUrl = 'https://p.3.cn/prices/mgets?skuIds=J_%s' % skuId
        
        # 请求商品价格，获取响应文本，并使用 json 解析为 dict ，获取 p 字段，转为 float 类型即为商品价格
        r = self.session.get(skuPriceUrl, headers=self.headers)
        skuPrice = float(json.loads(r.text)[0]["p"])
        
        return {"skuId": skuId, "skuName": skuName, "skuPrice": skuPrice}
    
    
    def get_all_sku_info(self):
        
        # 获取当前日期时间及时间戳
        now = datetime.now()
        dateTime = now.strftime('%Y-%m-%d %H:%M:%S')
        timeStamp = now.timestamp()
        
        # 创建list来保存结果
        result = list()
        
        # 遍历 skuIds
        for skuId in self.skuIds:
            d = self.get_sku_info(skuId)
            
            # 添加日期时间及时间戳
            d["datetime"] = dateTime
            d["timestamp"] = timeStamp
            
            # 添加到结果中
            result.append(d)
            
        return result
            
            
    def write_to_csv(self, result, path='result.csv', overwrite=False): # path: csv文件路径；overwrite: 是否覆盖原文件内容
        
        # 根据 overwrite 参数决定文件打开模式
        if overwrite:
            mode = 'w+' # 覆盖写入
        else:
            mode = 'a+' # 追加写入
            
        # 编写 csv 文件头
        csvHeaders = ['skuId', 'skuName', 'skuPrice', 'datetime', 'timestamp']
        
        # 从 result 中获取csv数据行
        rows = [] # 保存数据行结果
        for row in result: # 遍历 result
            rows.append([row[x] for x in csvHeaders]) # 这边用列表推导式写，比较方便；追加到 rows 中
            
        # 如果文件已存在、且 overwrite 为False，则无需写入csv头
        if (overwrite == False) and (os.path.isfile(path)):
            writeHeader = False
        else:
            writeHeader = True
        
        # 打开csv文件并写入头和数据行
        with open(path, mode, encoding='utf-8') as f:
            f_csv = csv.writer(f) # 初始化 csv writer
            if writeHeader:
                f_csv.writerow(csvHeaders) # 写入头
            f_csv.writerows(rows) # 写入数据行


if __name__ == "__main__":
    # 实例化 JdGetter
    getter = JdGetter()
    
    # 获取并输出csv文件
    getter.write_to_csv(getter.get_all_sku_info())