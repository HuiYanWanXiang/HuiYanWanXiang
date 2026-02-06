class HuiyanError(Exception):
    """项目基础异常类"""
    pass

class LLMConnectionError(HuiyanError):
    """LLM 连接失败"""
    pass

class PromptEmptyError(HuiyanError):
    """提示词为空"""
    pass