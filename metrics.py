import os
import ast


def analyze_code(directory):
    total_lines = 0
    empty_lines = 0
    comment_lines = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    for line in f:
                        total_lines += 1
                        stripped_line = line.strip()
                        if not stripped_line:
                            empty_lines += 1
                        elif stripped_line.startswith("#"):
                            comment_lines += 1
    return total_lines, empty_lines, comment_lines


def analyze_functions(directory):
    function_lines = []
    class_lines = []
    file_lines = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    file_lines.append(len(lines))

                    tree = ast.parse("".join(lines))
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            function_lines.append(len(node.body))
                        elif isinstance(node, ast.ClassDef):
                            class_lines.append(len(node.body))

    avg_function_lines = sum(function_lines) / len(function_lines) if function_lines else 0
    avg_class_lines = sum(class_lines) / len(class_lines) if class_lines else 0
    avg_file_lines = sum(file_lines) / len(file_lines) if file_lines else 0

    return avg_function_lines, avg_class_lines, avg_file_lines

def analyze_classes(directory):
    namespaces = 0
    types = 0
    methods = 0
    fields = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            namespaces += 1
                            types += 1  # каждый класс как тип
                            for body_item in node.body:
                                if isinstance(body_item, ast.FunctionDef):
                                    methods += 1
                                elif isinstance(body_item, ast.Assign):
                                    fields += 1

    return namespaces, types, methods, fields


directory = 'C:\\Users\\1\\Desktop\\Work\\concreteDecor\\api'
total, empty, comments = analyze_code(directory)
comment_percentage = (comments / total) * 100 if total else 0

print(f"Total lines: {total}")
print(f"Empty lines: {empty}")
print(f"Comment lines: {comments}")
print(f"Comment percentage: {comment_percentage:.2f}%")



avg_func, avg_class, avg_file = analyze_functions(directory)

print(f"Average function lines: {avg_func:.2f}")
print(f"Average class lines: {avg_class:.2f}")
print(f"Average file lines: {avg_file:.2f}")

namespaces, types, methods, fields = analyze_classes(directory)

print(f"Namespaces: {namespaces}")
print(f"Types: {types}")
print(f"Methods: {methods}")
print(f"Fields: {fields}")