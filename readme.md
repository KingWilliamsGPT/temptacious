![cover](./temptacious/repo_photos/Temptacious%20Logo.PNG)


# Temptacious

Temptacious is a lightweight template engine inspired by the Django template engine. It's designed to be easy to use, flexible, and fast. Although it's still in its early stages, it's already quite powerful and can be used to generate dynamic HTML, XML, and other types of documents.

## Features

Some of the key features of Temptacious include:

- A simple and intuitive syntax that's easy to learn and use.
- Support for variables, loops, conditionals, and other common programming constructs.
- Easy integration with existing Python projects.
- Flexible and customizable, will support custom filters, tags, and extensions, eventualy.

## Getting Started

To get started with Temptacious, simply install it using pip:

```bash
pip install temptacious
```

Once you've installed Temptacious, you can start using it in your Python projects or downloaded it [here](https://pypi.org/project/temptacious/1.0/) at pypi. Here's a quick example:

```python
from temptacious import Template

template = Template("Hello, {{name}}!")
context = {'name':'World'}
result = template.render(context)
print(result)  # Output: Hello, World!
```

### Cheet :)
```python
from temptacious.base import main

# try it out yourself!!
main()
```

<!-- For more information on how to use Temptacious, check out the [documentation](https://temptacious.readthedocs.io/en/latest/). -->

## Contributing

Temptacious is an open-source project built by Williams Samuel. Contributions are welcome and encouraged!

## License

Temptacious is released under the [MIT License](LICENSE). Feel free to use it in your own projects or modify it as needed. 🤗
