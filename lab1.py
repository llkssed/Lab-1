import json
import xml.etree.ElementTree as ET

# Исключения
class InvalidShapeError(Exception):
    def __init__(self, message="Недопустимая форма"):
        self.message = message
        super().__init__(self.message)

class FileReadError(Exception):
    def __init__(self, message="Ошибка при чтении файла"):
        self.message = message
        super().__init__(self.message)

class FileWriteError(Exception):
    def __init__(self, message="Ошибка при записи файла"):
        self.message = message
        super().__init__(self.message)

# Базовые классы
class Shape:
    def __init__(self, color):
        if not color:
            raise ValueError("Цвет не может быть пустым")
        self.color = color

    def draw(self):
        raise NotImplementedError("Метод draw() должен быть реализован в дочернем классе")

class Circle(Shape):
    def __init__(self, color, radius):
        super().__init__(color)
        if radius <= 0:
            raise ValueError("Радиус должен быть положительным числом")
        self.radius = radius

    def draw(self):
        return f"Рисую круг с радиусом {self.radius} и цветом {self.color}"

class Rectangle(Shape):
    def __init__(self, color, width, height):
        super().__init__(color)
        if width <= 0 or height <= 0:
            raise ValueError("Ширина и высота должны быть положительными числами")
        self.width = width
        self.height = height

    def draw(self):
        return f"Рисую прямоугольник {self.width}x{self.height} с цветом {self.color}"

class Line(Shape):
    def __init__(self, color, length):
        super().__init__(color)
        if length <= 0:
            raise ValueError("Длина линии должна быть положительным числом")
        self.length = length

    def draw(self):
        return f"Рисую линию длиной {self.length} и цветом {self.color}"

class Polygon(Shape):
    def __init__(self, color, sides):
        super().__init__(color)
        if sides < 3:
            raise ValueError("Многоугольник должен иметь минимум 3 стороны")
        self.sides = sides

    def draw(self):
        return f"Рисую многоугольник с {self.sides} сторонами и цветом {self.color}"

class Text:
    def __init__(self, content, font_size):
        if not content:
            raise ValueError("Текст не может быть пустым")
        if font_size <= 0:
            raise ValueError("Размер шрифта должен быть положительным")
        self.content = content
        self.font_size = font_size

    def draw(self):
        return f"Рисую текст '{self.content}' с размером шрифта {self.font_size}"

class Group:
    def __init__(self):
        self.items = []

    def add(self, item):
        if not isinstance(item, (Shape, Text)):
            raise InvalidShapeError("Можно добавить только объекты Shape или Text")
        self.items.append(item)

    def draw(self):
        return "\n".join(item.draw() for item in self.items)

class Canvas:
    def __init__(self, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("Ширина и высота холста должны быть положительными")
        self.width = width
        self.height = height
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def draw(self):
        return f"Размер холста: {self.width}x{self.height}\n" + "\n".join(el.draw() for el in self.elements)

class Project:
    def __init__(self, name):
        if not name:
            raise ValueError("Название проекта не может быть пустым")
        self.name = name
        self.canvas = None

    def set_canvas(self, canvas):
        if not isinstance(canvas, Canvas):
            raise TypeError("Требуется объект Canvas")
        self.canvas = canvas

    def draw(self):
        if not self.canvas:
            return "Холст не задан"
        return f"Проект: {self.name}\n" + self.canvas.draw()

class FileHandler:
    @staticmethod
    def save_to_json(filename, project):
        try:
            data = {
                "name": project.name,
                "canvas": {
                    "width": project.canvas.width,
                    "height": project.canvas.height,
                    "elements": [
                        {
                            "type": el.__class__.__name__,
                            "properties": el.__dict__
                        } for el in project.canvas.elements
                    ]
                }
            }
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            raise FileWriteError(f"Ошибка при записи в JSON: {e}")

    @staticmethod
    def load_from_json(filename):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except Exception as e:
            raise FileReadError(f"Ошибка при чтении JSON: {e}")

    @staticmethod
    def save_to_xml(filename, project):
        try:
            root = ET.Element("project", name=project.name)
            canvas_elem = ET.SubElement(root, "canvas", width=str(project.canvas.width), height=str(project.canvas.height))
            for el in project.canvas.elements:
                el_elem = ET.SubElement(canvas_elem, "element", type=el.__class__.__name__)
                for k, v in el.__dict__.items():
                    ET.SubElement(el_elem, k).text = str(v)
            tree = ET.ElementTree(root)
            tree.write(filename)
        except Exception as e:
            raise FileWriteError(f"Ошибка при записи в XML: {e}")

    @staticmethod
    def load_from_xml(filename):
        try:
            tree = ET.parse(filename)
            return tree.getroot()
        except Exception as e:
            raise FileReadError(f"Ошибка при чтении XML: {e}")

# Пример использования
if __name__ == "__main__":
    try:
        canvas = Canvas(800, 600)
        canvas.add_element(Circle("red", 50))
        canvas.add_element(Rectangle("blue", 100, 200))
        canvas.add_element(Text("Hello, World!", 24))

        project = Project("My Design")
        project.set_canvas(canvas)

        print(project.draw())

        FileHandler.save_to_json("project.json", project)
        FileHandler.save_to_xml("project.xml", project)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
