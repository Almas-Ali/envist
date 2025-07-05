import os

from envist import Envist


env = Envist(
    path=".env.example",
    accept_empty=True,
    # auto_cast=False
)

parsed_values = env.get_all()

print(parsed_values)

# os_data = os.getenv("JSON_DATA")
# print(os_data, type(os_data))

# envist_data = env.get("JSON_DATA")
# print(envist_data, type(envist_data))
# for key, value in envist_data.items():
#     print(f"{key} = {value} ({type(value)})")