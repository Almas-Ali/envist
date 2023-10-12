# Envist

A simple, lightweight, and easy to use environment variable manager for Python

Created by [**Md. Almas Ali**](https://github.com/Almas-Ali "Md. Almas Ali")


[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FAlmas-Ali%2Fenvist&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=Total+hits&edge_flat=false)](https://hits.seeyoufarm.com)


## Installation

```bash
pip install envist
```

## Usage

```python
from envist import Envist

env = Envist()

# Print env object as string
print(env)
# <Envist path=".env">

# Get default env file path
print(env.path)
# .env

# Custom env file path
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
env.save()

```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork it.
2. Create your feature branch (`git checkout -b feature/feature-name`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/feature-name`).
5. Create a new Pull Request.
