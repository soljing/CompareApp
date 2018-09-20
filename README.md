程序功能
=========
从 WatchGuard 网站获取 Firebox T/M series 的性能数据并存入 csv 文件，并按Firewall Throughput小到大排序

解决方案
---------
使用requests模块来获取指定网站url的HTML内容，使用BeautifulSoup模块来抽取HTML中需要的数据

模块设计
---------
> __get_all_product__           ：查询T/M系列产品信息<br>
> __create_compare_url__        ：根据比较产品构造比较网站地址<br>
> __get_url_content__           ：读取指定URL的网页内容<br>
> __query_compare_result__      : 查询比较结果<br>
> __sort_result_by_throughput__ : 按Firewall Throughput小到大排序<br>
> __output_csv__                : 保存结果到CSV<br>
> get_csv_result                : 获取结果<br>


项目结构
---------
分为2个文件：
>main.py是程序实现文件<br>
>unit_test.py是单元测试文件<br>
>result_xxx.csv 是输出的CSV结果文件<br>
>requirements.txt 程序依赖库说明<br>

脚本使用方法
---------
>传入2个比较设备参数<br>
```
app = CompareApp('WatchGuard Firebox® M440','WatchGuard Firebox® M5600')
csv = app.get_csv_result()
```
>传入3个比较设备参数<br>
```
app = CompareApp('WatchGuard Firebox® M440','WatchGuard Firebox® M5600','WatchGuard® Firebox T70')
csv = app.get_csv_result()
```