#encoding: utf-8
import os
import datetime
import requests
from bs4 import BeautifulSoup

class CompareApp:
    '''
    从 WatchGuard 网站获取 Firebox T/M series 的性能数据并存入 csv 文件
    app = CompareApp('WatchGuard Firebox® M440','WatchGuard Firebox® M5600')
    app.get_csv_result()

    app = CompareApp('WatchGuard Firebox® M440','WatchGuard Firebox® M5600','WatchGuard® Firebox T70')
    app.get_csv_result()
    '''
    #后台网站地址
    url = 'https://www.watchguard.com/wgrd-products/appliances-compare'

    #需要关注的产品类
    product_series = ['WatchGuard® Firebox M Series','WatchGuard Firebox T Series']
    
    #查询页面取数据标记
    qry_flag1 =  'WatchGuard® Model'
    qry_flag2 = 'Performance'

    #比较值
    compare_item = 'Firewall Throughput'

    def __init__(self,product1,product2,product3=None):
        '''
        输入参数，至少2个，最多3个
        '''
        self.compare_products = [product1,product2]
        if product3:
            self.compare_products.append(product3)
        

    def get_csv_result(self):
        '''
        输出csv文件路径与当前的脚本文件同路径
        '''
        compare_result_list = self.__query_compare_result__()
        sort_list = self.__sort_result_by_throughput__(compare_result_list)
        #保存到当前脚本的目录下
        pwd = os.path.split(os.path.realpath(__file__))[0]
        now = datetime.datetime.now()
        file_name = 'result_' + datetime.datetime.strftime(now,'%Y_%m_%d %H_%M_%S') + '.csv'
        save_path = os.path.join(pwd,file_name)
        #print(save_path)
        return self.__output_csv__(sort_list,save_path)

    def __output_csv__(self,result,save_path):
        '''
        写csv文件，参数是列表，列表元素是tuple (product_name,performance_dic)
        '''
        try:
            with open(save_path,mode='w+',encoding='utf-8') as f:
                header = ['Model']
                performance_names = list(result[0][1].keys())
                header.extend(performance_names)
                header_str = "".join(['"%s",' % i for i in header])
                
                #写表头
                f.write(header_str+"\n")
                #写表数据
                for (product,performance) in result:
                    data_str = product.split()[-1]
                    for item in performance_names:
                        data_str += (',"%s"' %  performance[item])
                    f.write(data_str+"\n")
                print("结果文件路径:",save_path)
                return save_path
        except Exception as e:
            print('写文件失败')
            print('异常信息:',e)
        return None

    def __query_compare_result__(self):
        '''
        查询比较产品的性能数据，返回是列表，列表元素是tuple （product_name,performance_dic）
        '''
        compare_url = self.__create_compare_url__()
        #print(compare_url)
        content = self.__get_url_content__(compare_url)
        soup = BeautifulSoup(content,"html.parser")
        table = soup.find('table')
        table_rows = table.find_all('tr')


        #产品比较信息
        compare_info = []   
        #先根据标志位1读取产品信息
        for row in table_rows:
            find_product = False
            table_cells = row.find_all('th')
            for cell in table_cells:
                if cell.string.strip() == CompareApp.qry_flag1:
                    find_product = True
                    continue
                if find_product:
                    product_name = cell.string.strip()
                    compare_info.append((product_name,{}))
        #print(compare_info)
        #再根据标志2读取性能数据
        #1.找出性能的开始和结束行
        find_performance = False
        performance_start_row = -1
        performance_end_row = -1
        for row_index in range(0,len(table_rows)):
            table_cells = table_rows[row_index].find_all('th')
            for cell in table_cells:
                if cell.string.strip() == CompareApp.qry_flag2:
                     find_performance = True
                     performance_start_row = row_index + 1
                     break
                if find_performance and (cell.string.strip() != CompareApp.qry_flag2):
                    performance_end_row = row_index
                    break
            if performance_end_row > 0:
                break
        # 2.读取性能数据
        for row_index in range(performance_start_row,performance_end_row):
            table_cells = table_rows[row_index].find_all('td')
            performance_row = []
            for cell in table_cells:
                performance_row.append(cell.string.strip())
            
            for index in range(0,len(compare_info)):
                performance_name = performance_row[0]
                compare_info[index][1][performance_name] = performance_row[index + 1]
        #print(compare_info)
        return compare_info

    def __sort_result_by_throughput__(self,result_list):
        '''
        对查询性能结果按吞吐量进行从小到大排序，返回值排序后的列表
        '''
        length = len(result_list) 
        for i in range(0,length):
            for j in range(i+1,length):
                throughput_i = result_list[i][1][CompareApp.compare_item].strip(' Gbps')
                throughput_j = result_list[j][1][CompareApp.compare_item].strip(' Gbps')
                if throughput_i > throughput_j:
                    result_list[i],result_list[j] = result_list[j],result_list[i]
        return result_list

    def __get_url_content__(self,url):
        '''
        读取指定URL的网页内容
        '''
        content = None
        try:
            content = requests.get(url).content
        except Exception as e:
            print("访问URL:%s失败" % CompareApp.url)
            print("异常信息：", e)
        return content

    def __get_all_product__(self):
        '''
        获取所有的T/M系列产品查询id信息
        '''
        content = self.__get_url_content__(CompareApp.url)
        #加载网页
        soup = BeautifulSoup(content,"html.parser")
        
        #读取下拉菜单中的T/M系列产品名称和对应的查询ID
        product_list = {}

        #找到网页中的下拉菜单(p1,p2,p3都是一样的，随便取一个)
        p1_groups = soup.find(id='p1').find_all('optgroup')
        for opt_group in p1_groups:
            label = opt_group['label']
            if label in CompareApp.product_series:
                options = opt_group.find_all('option')
                for option in options:
                    #获取选项里产品名称
                    product_fullname = option.string
                    #获取选项里产品ID
                    product_id = option['value']
                    #保存到产品列表里
                    product_list[product_fullname] = product_id
        return product_list

    def __create_compare_url__(self):
        '''
        根据比较产品构造网站地址
        '''
        compare_url = CompareApp.url
        product_list = self.__get_all_product__()
        for product in self.compare_products:
            if product in product_list:
                compare_url += '/%s' % product_list[product]
            else:
                raise(Exception('产品:%s 输入错误，请输入T/M 相关产品'))
        return compare_url

if __name__ == '__main__':
    app = CompareApp('WatchGuard Firebox® M440','WatchGuard Firebox® M5600')
    app.get_csv_result()