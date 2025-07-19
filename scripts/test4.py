from typing import cast
from torch.jit import isinstance
import ast
from layer0.utils.logging_config import get_logger

logger = get_logger(__name__)

FORBIDDEN_MODULES = {"os", "sys", "random", "time", "socket", "subprocess"}
FORBIDDEN_FUNCTIONS = {"eval", "exec", "open", "input", "__import__"}

def check_contract_safety(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    issues = []

    for node in ast.walk(tree):

        # Cấm import
        if isinstance(node, ast.Import):
            node = cast(ast.Import, node)
            for alias in node.names:
                mod = alias.name.split('.')[0]
                if mod in FORBIDDEN_MODULES:
                    issues.append(f"❌ Cấm import: {mod}")

        # Cấm from x import y
        elif isinstance(node, ast.ImportFrom):
            node = cast(ast.ImportFrom, node)
            if node.module:
                mod = node.module.split('.')[0]
                if mod in FORBIDDEN_MODULES:
                    issues.append(f"❌ Cấm from-import: {mod}")

        # Cấm gọi hàm
        elif isinstance(node, ast.Call):
            node = cast(ast.Call, node)
            # Trường hợp gọi trực tiếp: open(), eval()
            if isinstance(node.func, ast.Name):
                node.func = cast(ast.Name, node.func)
                func_name = node.func.id
                if func_name in FORBIDDEN_FUNCTIONS:
                    issues.append(f"❌ Cấm gọi hàm: {func_name}")
            # Trường hợp gọi như os.system
            elif isinstance(node.func, ast.Attribute):
                node.func = cast(ast.Attribute, node.func)
                obj = node.func.value
                if isinstance(obj, ast.Name):
                    obj = cast(ast.Name, obj)
                    mod = obj.id
                    if mod in FORBIDDEN_MODULES:
                        issues.append(f"❌ Cấm gọi: {mod}.{node.func.attr}")
         
        if isinstance(node, ast.ClassDef):
            node = cast(ast.ClassDef, node)
            logger.info("Class: %s", node.name)
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    item = cast(ast.FunctionDef, item)
                    logger.info("  Method: %s", item.name)

    return issues

check_contract_safety("syntax_test.py")