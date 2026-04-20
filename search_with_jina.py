import os
import requests
from tavily import TavilyClient

# 1. 初始化客户端
tavily_api_key = os.getenv("TAVILY_API_KEY")
jina_api_key = os.getenv("JINA_API_KEY")

tavily = TavilyClient(api_key=tavily_api_key)

def get_jina_content(url):
    """使用 Jina Reader 获取网页纯净内容"""
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "Authorization": f"Bearer {jina_api_key}",
        "X-Return-Format": "text" # 只要纯文本，不要HTML
    }
    try:
        response = requests.get(jina_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text[:3000] # 截取前3000字，防止太长
        else:
            return f"Jina读取失败: {response.status_code}"
    except Exception as e:
        return f"Jina读取错误: {str(e)}"

def search_and_read(query):
    print(f"🔍 正在搜索: {query} ...")
    
    # 2. 使用 Tavily 搜索 (找链接)
    # search_depth="advanced" 是 Tavily 的深度搜索模式
    response = tavily.search(query=query, search_depth="advanced", max_results=3)
    
    results = []
    
    # 3. 遍历结果，使用 Jina 读取全文
    for result in response['results']:
        url = result['url']
        print(f"📖 正在通过 Jina 深度阅读: {url} ...")
        
        full_content = get_jina_content(url)
        
        results.append({
            "title": result['title'],
            "url": url,
            "snippet": result['content'], # Tavily 提供的摘要
            "full_content": full_content  # Jina 提供的全文
        })
        
    return results

# --- 主程序 ---
if __name__ == "__main__":
    # 这里可以替换成你的新闻关键词
    topic = os.getenv("SEARCH_TOPIC") or "Artificial Intelligence News"
    
    news_data = search_and_read(topic)
    
    # 打印结果，方便你调试
    for item in news_data:
        print("-" * 50)
        print(f"标题: {item['title']}")
        print(f"链接: {item['url']}")
        print(f"正文预览: {item['full_content'][:200]}...") # 只打印前200字看效果
