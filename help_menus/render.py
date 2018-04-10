import json
import shutil
import os
import sys
import click
import jinja2

PATH = os.path.dirname(__file__)

if __name__ == "__main__":
    try:
        with open(os.path.join(PATH, 'recipes.json')) as recipe_file:
            recipes = json.load(recipe_file)
    except FileNotFoundError:
        print("Error: coudn't find recipes.json", file=sys.stderr)
        sys.exit(1)
    template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(PATH)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

    template = template_env.get_template(os.path.join(PATH, 'help_template.html'))
    rendered_html = template.render(recipes)
    with open(os.path.join(PATH, 'help.html'), 'w') as help_file:
        help_file.write(rendered_html)
