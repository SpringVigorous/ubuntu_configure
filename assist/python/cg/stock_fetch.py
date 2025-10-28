import akshare as ak
import pandas as pd
from base import df_empty,exception_decorator,logger_helper,UpdateTimeType

# 设置pandas显示选项，以便完整查看数据
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def get_stock_hist_data(symbol, start_date, end_date)->pd.DataFrame:
    """
    获取A股股票历史行情数据
    """
    try:
        # 调用接口获取数据
        df = ak.stock_zh_a_hist(
            symbol=symbol,        # 股票代码，无需市场后缀
            period="daily",       # 周期：        print(f"获取股票 {symbol} 数据失败: {str(e)}")
            start_date=start_date, # 开始日期，格式：YYYYMMDD
            end_date=end_date,    # 结束日期，格式：YYYYMMDD
            adjust="qfq"          # 复权类型：""(不复权), "qfq"(前复权), "hfq"(后复权)
        )
        
        # 基本数据处理
        df['日期'] = pd.to_datetime(df['日期'])  # 转换日期格式
        df.set_index('日期', inplace=True)      # 将日期设为索引
        
        # 重命名列名为英文，便于后续处理
        column_name_mapping = {
            '开盘': 'open',
            '收盘': 'close', 
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '振幅': 'amplitude',
            '涨跌幅': 'pct_chg',
            '涨跌额': 'change',
            '换手率': 'turnover'
        }
        df.rename(columns=column_name_mapping, inplace=True)
        
        return df.sort_index()  # 按日期顺序排列
    
    except Exception as e:
        print(f"获取股票 {symbol} 数据失败: {str(e)}")
        return None
def get_realtime_data(specific_stock_code=None)->pd.DataFrame:
    """
    获取实时行情数据。不指定代码则获取全市场数据。
    """
    try:
        # 获取全市场实时数据(A股)
        realtime_df:pd.DataFrame = ak.stock_zh_a_spot_em()
        
        if specific_stock_code:
            # 筛选特定股票
            filtered_df = realtime_df[realtime_df['代码'] == specific_stock_code]
            if not df_empty(filtered_df):
                return filtered_df
            else:
                print(f"未找到股票代码 {specific_stock_code} 的实时数据")
                return None
        else:
            return realtime_df
            
    except Exception as e:
        print(f"获取实时数据失败: {str(e)}")
        return None
    
def main():
    
    
        
    all_realtime_data = get_realtime_data()
    all_realtime_data.to_excel("all_realtime_data.xlsx", index=False)
    
    
    
    
    # 使用示例：获取贵州茅台2025年第一季度的数据
    stock_data = get_stock_hist_data("603101", "20250101", "20250331")

    if stock_data is not None:
       
        print("数据获取成功！示例数据前5行：")
        print(stock_data.head())
        
        print("\n基础统计信息：")
        print(stock_data[['close', 'volume', 'pct_chg']].describe())
        pass

if __name__ == "__main__":
    main()    
    
