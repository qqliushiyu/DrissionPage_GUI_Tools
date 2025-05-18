#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
元素选择器生成器模块，用于自动生成和评估元素选择器。
支持多种定位策略，如XPath、CSS、ID等，并提供定位策略的健壮性评估。
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import re


class SelectorEvaluator:
    """
    选择器评估器，用于评估选择器的健壮性和准确性。
    """
    
    # 选择器类型权重，数值越高表示健壮性越好
    SELECTOR_WEIGHTS = {
        "id": 10,       # ID选择器最可靠
        "name": 8,      # name属性选择器较可靠
        "css": 7,       # CSS选择器可靠性中等
        "xpath": 6,     # XPath选择器可靠性中等
        "link_text": 5, # 链接文本选择器可靠性一般
        "tag": 3,       # 标签选择器可靠性较低
        "class": 3,     # 类选择器可靠性较低
        "text": 2       # 文本选择器可靠性低
    }
    
    @classmethod
    def evaluate_selector(cls, selector_type: str, selector_value: str) -> Tuple[int, str]:
        """
        评估选择器的健壮性
        
        Args:
            selector_type: 选择器类型（如id, xpath, css等）
            selector_value: 选择器值
            
        Returns:
            (分数, 评估意见)
        """
        base_score = cls.SELECTOR_WEIGHTS.get(selector_type.lower(), 1)
        
        # 根据选择器类型和值进行具体评估
        if selector_type.lower() == "id":
            # ID选择器评估
            if re.search(r'\d+$', selector_value):
                # 以数字结尾的ID可能是动态生成的，健壮性降低
                return base_score - 2, "ID以数字结尾，可能是动态生成的，不太稳定"
            return base_score, "ID选择器通常是最可靠的选择"
            
        elif selector_type.lower() == "xpath":
            # XPath选择器评估
            if "//" in selector_value:
                # 包含//的XPath可能会受到DOM结构变化的影响
                base_score -= 1
            
            if "contains" in selector_value:
                # 使用contains函数增加了灵活性
                base_score += 1
            
            if selector_value.count("/") > 5:
                # 路径过长，可能受DOM结构变化影响
                return base_score - 2, "XPath路径过长，易受DOM结构变化影响"
                
            if "@id" in selector_value or "@name" in selector_value:
                # 使用ID或name属性可以提高稳定性
                base_score += 2
                return base_score, "基于ID或name属性的XPath选择器相对稳定"
            
            return base_score, "XPath选择器在DOM结构稳定的情况下可靠"
            
        elif selector_type.lower() == "css":
            # CSS选择器评估
            if "#" in selector_value:
                # 使用ID选择器
                base_score += 2
                return base_score, "基于ID的CSS选择器非常可靠"
                
            if selector_value.count(" > ") > 3:
                # 选择器链过长
                base_score -= 2
                return base_score, "CSS选择器链过长，易受DOM结构变化影响"
                
            if "[" in selector_value and "]" in selector_value:
                # 使用属性选择器
                base_score += 1
                return base_score, "使用属性选择器增加了健壮性"
            
            return base_score, "CSS选择器在DOM结构稳定的情况下可靠"
            
        elif selector_type.lower() == "class":
            # 类选择器评估
            classes = selector_value.split()
            if len(classes) > 2:
                # 使用多个类可以提高特异性
                base_score += 1
                return base_score, "多类选择器提高了特异性，但仍可能受样式变更影响"
            
            return base_score, "类选择器容易受样式变更影响，建议配合其他选择器使用"
            
        else:
            # 其他选择器类型
            return base_score, f"此类型选择器的健壮性为 {base_score}/10"


class SelectorGenerator:
    """
    选择器生成器，根据元素特征自动生成多种定位策略。
    """
    
    def __init__(self, drission_engine=None):
        """
        初始化选择器生成器
        
        Args:
            drission_engine: DrissionPage引擎实例，用于页面交互
        """
        self._engine = drission_engine
    
    def generate_selectors(self, element_or_info: Any) -> Dict[str, Dict[str, Any]]:
        """
        为元素生成多种选择器
        
        Args:
            element_or_info: 元素对象或元素信息字典
            
        Returns:
            选择器字典，格式为 {选择器类型: {value: 选择器值, score: 健壮性分数, comment: 评价}}
        """
        # 这里的实现依赖于具体使用的DrissionPage版本
        # 以下是一个示例实现
        
        if self._engine is None:
            return {"error": {"value": "", "score": 0, "comment": "未配置DrissionPage引擎"}}
        
        selectors = {}
        
        # 获取元素信息
        element_info = self._get_element_info(element_or_info)
        
        # 生成ID选择器（如果有ID）
        if element_info.get("id"):
            selector_type = "id"
            selector_value = element_info["id"]
            score, comment = SelectorEvaluator.evaluate_selector(selector_type, selector_value)
            selectors[selector_type] = {
                "value": selector_value,
                "score": score,
                "comment": comment
            }
        
        # 生成name选择器（如果有name属性）
        if element_info.get("name"):
            selector_type = "name"
            selector_value = element_info["name"]
            score, comment = SelectorEvaluator.evaluate_selector(selector_type, selector_value)
            selectors[selector_type] = {
                "value": selector_value,
                "score": score,
                "comment": comment
            }
        
        # 生成CSS选择器
        css_selector = self._generate_css_selector(element_info)
        if css_selector:
            score, comment = SelectorEvaluator.evaluate_selector("css", css_selector)
            selectors["css"] = {
                "value": css_selector,
                "score": score,
                "comment": comment
            }
        
        # 生成XPath选择器
        xpath_selector = self._generate_xpath_selector(element_info)
        if xpath_selector:
            score, comment = SelectorEvaluator.evaluate_selector("xpath", xpath_selector)
            selectors["xpath"] = {
                "value": xpath_selector,
                "score": score,
                "comment": comment
            }
        
        # 对于链接，生成链接文本选择器
        if element_info.get("tag") == "a" and element_info.get("text"):
            selector_type = "link_text"
            selector_value = element_info["text"]
            score, comment = SelectorEvaluator.evaluate_selector(selector_type, selector_value)
            selectors[selector_type] = {
                "value": selector_value,
                "score": score,
                "comment": comment
            }
        
        return selectors
    
    def recommend_selector(self, selectors: Dict[str, Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
        """
        根据健壮性评分推荐最佳选择器
        
        Args:
            selectors: 选择器字典
            
        Returns:
            (选择器类型, 选择器信息)
        """
        if not selectors:
            return "none", {"value": "", "score": 0, "comment": "没有可用的选择器"}
        
        # 根据分数排序
        sorted_selectors = sorted(
            selectors.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # 返回得分最高的选择器
        return sorted_selectors[0]
    
    def _get_element_info(self, element_or_info: Any) -> Dict[str, Any]:
        """
        获取元素信息
        
        Args:
            element_or_info: 元素对象或元素信息字典
            
        Returns:
            元素信息字典
        """
        # 根据DrissionPage API调整实现
        if isinstance(element_or_info, dict):
            return element_or_info
        
        try:
            # 尝试从元素对象获取信息
            return self._engine.get_element_info(element_or_info)
        except Exception:
            # 如果失败则返回空字典
            return {}
    
    def _generate_css_selector(self, element_info: Dict[str, Any]) -> str:
        """
        生成CSS选择器
        
        Args:
            element_info: 元素信息字典
            
        Returns:
            CSS选择器
        """
        if not element_info:
            return ""
        
        tag = element_info.get("tag", "")
        if not tag:
            return ""
        
        # 优先使用ID
        if element_info.get("id"):
            return f"#{element_info['id']}"
        
        # 使用name属性
        if element_info.get("name"):
            return f"{tag}[name='{element_info['name']}']"
        
        # 使用class属性
        if element_info.get("class"):
            class_names = element_info["class"].split()
            if class_names:
                # 使用第一个类名，如果有多个
                return f"{tag}.{class_names[0]}"
        
        # 基于其他属性
        for attr in ["type", "role", "aria-label"]:
            if element_info.get(attr):
                return f"{tag}[{attr}='{element_info[attr]}']"
        
        # 如果都没有特殊属性，尝试使用文本内容
        if element_info.get("text") and len(element_info["text"]) < 30:
            text = element_info["text"].strip()
            return f"{tag}:contains('{text}')"
        
        # 最后可能不得不返回一个较弱的选择器
        return tag
    
    def _generate_xpath_selector(self, element_info: Dict[str, Any]) -> str:
        """
        生成XPath选择器
        
        Args:
            element_info: 元素信息字典
            
        Returns:
            XPath选择器
        """
        if not element_info:
            return ""
        
        tag = element_info.get("tag", "")
        if not tag:
            return ""
        
        # 优先使用ID
        if element_info.get("id"):
            return f"//{tag}[@id='{element_info['id']}']"
        
        # 使用name属性
        if element_info.get("name"):
            return f"//{tag}[@name='{element_info['name']}']"
        
        # 使用class属性
        if element_info.get("class"):
            class_names = element_info["class"].split()
            if class_names:
                # 使用contains和第一个类名
                return f"//{tag}[contains(@class, '{class_names[0]}')]"
        
        # 基于其他属性
        for attr in ["type", "role", "aria-label"]:
            if element_info.get(attr):
                return f"//{tag}[@{attr}='{element_info[attr]}']"
        
        # 使用文本内容
        if element_info.get("text") and len(element_info["text"]) < 30:
            text = element_info["text"].strip()
            return f"//{tag}[contains(text(), '{text}')]"
        
        # 最后可能不得不返回一个较弱的选择器
        return f"//{tag}"


class BrowserPluginConnector:
    """
    浏览器插件连接器，用于与浏览器插件进行通信，
    获取用户在网页上选择的元素，并生成选择器。
    """
    
    def __init__(self, selector_generator: SelectorGenerator):
        """
        初始化浏览器插件连接器
        
        Args:
            selector_generator: 选择器生成器实例
        """
        self._selector_generator = selector_generator
        self._connection = None
        self._is_connected = False
    
    def connect(self, port: int = 8888) -> bool:
        """
        连接到浏览器插件
        
        Args:
            port: 连接端口
            
        Returns:
            是否成功连接
        """
        # 这里实现与浏览器插件的WebSocket连接
        # 实际实现需要根据具体的插件协议来定
        try:
            # 模拟连接过程
            self._is_connected = True
            return True
        except Exception:
            self._is_connected = False
            return False
    
    def disconnect(self) -> None:
        """断开与浏览器插件的连接"""
        if self._is_connected:
            # 关闭连接
            self._is_connected = False
    
    def is_connected(self) -> bool:
        """
        检查是否已连接到浏览器插件
        
        Returns:
            是否已连接
        """
        return self._is_connected
    
    def get_selected_element(self) -> Dict[str, Any]:
        """
        获取用户在浏览器中选择的元素
        
        Returns:
            元素信息字典
        """
        if not self._is_connected:
            return {"error": "未连接到浏览器插件"}
        
        # 这里模拟从插件获取选中元素的过程
        # 实际实现需要处理插件的消息
        
        # 示例返回数据
        return {
            "tag": "button",
            "id": "submitBtn",
            "class": "btn btn-primary",
            "text": "提交",
            "attributes": {
                "type": "submit",
                "aria-label": "Submit form"
            }
        }
    
    def generate_selectors_for_selected(self) -> Dict[str, Dict[str, Any]]:
        """
        为用户选择的元素生成选择器
        
        Returns:
            选择器字典
        """
        element_info = self.get_selected_element()
        if "error" in element_info:
            return {"error": {"value": element_info["error"], "score": 0, "comment": "获取元素失败"}}
        
        return self._selector_generator.generate_selectors(element_info) 