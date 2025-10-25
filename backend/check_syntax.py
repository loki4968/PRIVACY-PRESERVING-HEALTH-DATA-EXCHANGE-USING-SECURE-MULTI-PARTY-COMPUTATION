import ast

def check_syntax(file_path):
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            source = file.read()
        ast.parse(source)
        print(f"✅ Syntax check passed for {file_path}")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path} at line {e.lineno}, column {e.offset}")
        print(f"   {e.text.strip()}")
        print(f"   {' ' * (e.offset - 1)}^")
        print(f"   {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error checking syntax: {str(e)}")
        return False

if __name__ == "__main__":
    check_syntax("main.py")