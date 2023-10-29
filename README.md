# Envist

<p align="center">

<img src="https://github.com/Almas-Ali/envist/blob/master/logo.png?raw=true" alt="Envist Logo" width="200"/>

[![PyPI version](https://badge.fury.io/py/envist.svg)](https://pypi.org/project/envist/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/envist)](https://pypi.org/project/envist/)
[![PyPI - License](https://img.shields.io/pypi/l/envist)](https://pypi.org/project/envist/)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FAlmas-Ali%2Fenvist&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=Total+hits&edge_flat=false)](https://hits.seeyoufarm.com)

A simple, lightweight, and easy to use environment variable manager for Python

Created by [**Md. Almas Ali**](https://github.com/Almas-Ali "Md. Almas Ali")

</p>

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Functions](#functions)
- [Data Types](#data-types)
- [Examples](#examples)
- [License](#license)
- [Contributing](#contributing)

## Features

Envist a simple, lightweight, and easy to use environment variable manager for Python. It can be used to get, set, unset, and save environment variables to a file. It also supports casting environment variables to a specific types as you need. It not only supports the casting from language spacific types but also supports casting from `.env` file spacific types. For example, if you have a `.env` file like this:

```env
# .env
name = John Doe
age = 20
is_admin = True
```

Then you can get the `name` variable as `str`, `age` variable as `int`, and `is_admin` variable as `bool` like this:

```python
import envist

env = envist.Envist()

name = env.get('name', cast=str) # Output: 'John Doe'
age = env.get('age', cast=int) # Output: 20
is_admin = env.get('is_admin', cast=bool) # Output: True
```

It has a spacial feature like never before. Now, with `envist` you can typecast your environment variables inside your `.env` file. For example, if you have a `.env` file like this:

```env
# .env
name <str> = John Doe
age <int> = 20
is_admin <bool> = True
```

Then you can get the `name` variable as `str`, `age` variable as `int`, and `is_admin` variable as `bool` like this:

```python
import envist

env = envist.Envist()

name = env.get('name') # Output: 'John Doe'
print(type(name)) # Output: <class 'str'>

age = env.get('age') # Output: 20
print(type(age)) # Output: <class 'int'>

is_admin = env.get('is_admin') # Output: True
print(type(is_admin)) # Output: <class 'bool'>
```

Here you don't need to specify the `cast` parameter. It will automatically cast the environment variables to the types you specified in your `.env` file. This is like a constant typecasting. You can also override the typecasting by specifying the `cast` parameter.

Envist also supports variable expansion. For example, if you have a `.env` file like this:

```env
# .env
server <str> = 127.0.0.1
port <int> = 8080
url <str> = http://${server}:${port}
```

Then you can get the `url` variable like this:

```python
import envist

env = envist.Envist()

url = env.get('url') # Output: 'http://127.0.0.1:8080'
```

## Installation

Install `envist` using `pip`:

```bash
pip install envist
```

## Functions

Envist class has the following functions:

| Function    | Description                        | Parameters                                  | Return Type |
| ----------- | ---------------------------------- | ------------------------------------------- | ----------- |
| `get`       | Get a specific env variable        | `key` (str), `default` (any), `cast` (type) | any         |
| `get_all`   | Get all env variables              | None                                        | dict        |
| `set`       | Set a specific env variable        | `key` (str), `value` (any)                  | None        |
| `set_all`   | Set multiple env variables         | `variables` (dict)                          | None        |
| `unset`     | Unset a specific env variable      | `key` (str)                                 | None        |
| `unset_all` | Unset multiple env variables       | `keys` (list)                               | None        |
| `save`      | Save updated env variables to file | `pretty` (bool), `sort_keys` (bool)         | None        |

# Data Types

Envist supports the following data types:

| Data Type        | Description | Status      |
| ---------------- | ----------- | ----------- |
| `str`            | String      | Supported   |
| `float`          | Float       | Supported   |
| `bool`           | Boolean     | Supported   |
| `list`, `List`   | Array       | Supported   |
| `dict`, `Dict`   | Object      | Development |
| `tuple`, `Tuple` | Tuple       | Development |
| `set`, `Set`     | Set         | Development |
| `CSV`            | CSV         | Development |
| `JSON`           | JSON        | Development |

**Note:** Multi-line expressions are not supported yet. It will be supported in the next version.

## Examples

```python
from envist import Envist

env = Envist()

# Print env object as string
print(env)
# <Envist path=".env">

# Get default env file path
print(env.path)
# .env

# Custom env file path or file name
env = Envist(path='my/path/.env')

# Get a specific env variable
env.get('name')

# Get a specific env variable with default value
env.get('name', default='John Doe')

# Get a specific env variable with default value and cast
env.get('name', default='John Doe', cast=int)

# Get all env variables
env.get_all()

# Set a specific env variable
env.set('name', 'John Doe')
env.set('age', 20)
env.set('is_admin', True)

# Set multiple env variables
env.set_all({
    'name': 'John Doe',
    'age': 20,
    'is_admin': True
})

# Unset a specific env variable
env.unset('name')

# Unset multiple env variables
env.unset_all(['name', 'age'])

# Unset all env variables
env.unset_all()

# Save updated env variables to file
# Save to default file, i.e. .env. You can also specify a custom file path in Emvist constructor object.
env.save(
    pretty=True, # Pretty print
    sort_keys=True # Sort keys
)

# Get a list from env variable
# list_elements <list> = 1, 2, 3, 4, 5
env.get('list_elements', cast=list)

# Working with variables
# server <str> = 127.0.0.1
# port <int> = 8080
# url <str> = http://${server}:${port}
env.get('url') # Output: 'http://127.0.0.1:8080'

```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork it.
2. Create your feature branch (`git checkout -b feature/feature-name`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/feature-name`).
5. Create a new Pull Request.
