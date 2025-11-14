import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential


# 设置页面配置
st.set_page_config(
    page_title="比特币价格监控",
    page_icon="₿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .price-container {
        text-align: center;
        margin: 2rem 0;
    }
    .price {
        font-size: 4rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .price-change {
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    .positive {
        color: #2ECC71;
    }
    .negative {
        color: #E74C3C;
    }
    .refresh-button {
        background-color: #3498DB;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 0.25rem;
        cursor: pointer;
        font-size: 1rem;
        transition: background-color 0.3s;
    }
    .refresh-button:hover {
        background-color: #2980B9;
    }
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
        margin-right: 10px;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# API端点
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
BITCOGECKO_ID = "bitcoin"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_bitcoin_data():
    """获取比特币价格数据"""
    params = {
        'ids': BITCOGECKO_ID,
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
        'include_24hr_vol': 'true',
        'include_last_updated_at': 'true'
    }
    
    try:
        response = requests.get(COINGECKO_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 解析数据
        bitcoin_data = data[BITCOGECKO_ID]
        current_price = bitcoin_data['usd']
        price_change_24h = bitcoin_data['usd_24h_change']
        last_updated = bitcoin_data['last_updated_at']
        
        return {
            'current_price': current_price,
            'price_change_24h': price_change_24h,
            'last_updated': last_updated,
            'status': 'success'
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f"网络请求错误: {str(e)}"
        }
    except KeyError as e:
        return {
            'status': 'error',
            'message': f"数据解析错误: {str(e)}"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"未知错误: {str(e)}"
        }

def format_price(price):
    """格式化价格显示"""
    return f"${price:,.2f}"

def format_change(change):
    """格式化价格变化显示"""
    change_abs = abs(change)
    sign = "+" if change >= 0 else "-"
    return f"{sign}{change_abs:.2f}% ({sign}${change_abs:,.2f})"

def display_bitcoin_price():
    """显示比特币价格信息"""
    # 获取数据
    data = fetch_bitcoin_data()
    
    # 显示加载状态
    if data['status'] == 'success':
        current_price = data['current_price']
        price_change_24h = data['price_change_24h']
        last_updated = datetime.fromtimestamp(data['last_updated'])
        
        # 价格容器
        st.markdown("""
        <div class="price-container">
            <h1>比特币价格 (BTC/USD)</h1>
            <div class="price">{}</div>
            <div class="price-change {}">{}</div>
            <p>最后更新: {}</p>
        </div>
        """.format(
            format_price(current_price),
            "positive" if price_change_24h >= 0 else "negative",
            format_change(price_change_24h),
            last_updated.strftime("%Y-%m-%d %H:%M:%S")
        ), unsafe_allow_html=True)
    else:
        # 显示错误信息
        st.error(f"获取比特币价格失败: {data['message']}")
    
    # 刷新按钮
    if st.button("刷新价格", key="refresh_button"):
        # 强制刷新数据
        st.experimental_rerun()

# 主应用界面
def main():
    # 标题
    st.title("比特币价格监控")
    st.markdown("---")
    
    # 显示比特币价格
    display_bitcoin_price()
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: grey;'>数据来源: CoinGecko API</p>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()