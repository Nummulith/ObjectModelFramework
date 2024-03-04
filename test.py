class MyClass:
    SomeField = "42"

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        return int(value) if isinstance(value, str) and value.isdigit() else int(value) if isinstance(value, (int, float)) else value

# Создаем экземпляр класса
obj = MyClass()

result = obj.SomeField
print(f"{result}, {type(result)}")

result = getattr(obj, "SomeField", None)
print(f"{result}, {type(result)}")
