import importlib.util
import os
from datetime import datetime

import click
import dotenv


class CustomCLI(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_custom_commands()

    def _load_custom_commands(self):
        """Load custom commands from file specified in ENV or default location."""
        dotenv.load_dotenv()
        custom_commands_file = os.environ.get('DMP_AF_CLI_COMMANDS_FILE', None)

        if custom_commands_file:
            click.echo(message=f"📁 Found custom cli commands file path: {custom_commands_file}.", err=True)
        else:
            return

        file_path = os.path.join(os.getcwd(), custom_commands_file)

        if os.path.exists(file_path):
            try:
                spec = importlib.util.spec_from_file_location("custom_commands", file_path)
                if spec is None:
                    click.echo(f"❌ Can't create spec for file: {file_path}", err=True)
                    return

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                click.echo(f"✅ Custom command module loaded: {file_path}", err=True)
            except SyntaxError as e:
                click.echo(f"❌ Syntax error in file {file_path}: {str(e)}", err=True)
                return
            except ImportError as e:
                click.echo(f"❌ Import error in file {file_path}: {str(e)}", err=True)
                return
            except PermissionError as e:
                click.echo(f"❌ Permission denied for file {file_path}: {str(e)}", err=True)
                return
            except Exception as e:
                click.echo(f"❌ Unexpected error for file {file_path}: {str(e)}", err=True)
                return

            commands_loaded_cnt = 0
            loaded_commands = set()
            for attr_name in dir(module):
                try:
                    if attr_name.startswith('_'):
                        continue

                    attr = getattr(module, attr_name)

                    if isinstance(attr, click.Command):
                        if not attr.name:
                            click.echo(message=f"⚠️ Skipped command without name: {attr_name}", err=True)
                            continue

                        if attr.name in loaded_commands:
                            click.echo(message=f"⚠️ Skipped command with duplicate name: {attr_name}", err=True)
                            continue

                        self.add_command(attr)
                        commands_loaded_cnt += 1
                        loaded_commands.add(attr_name)

                except Exception as e:
                    click.echo(f"⚠️ Exception while processing command {attr_name}: {e}", err=True)
                    continue

            if commands_loaded_cnt == 0:
                click.echo(message=f"💡 There are no commands found in file {file_path}.", err=True)
            else:
                click.echo(f"✅ Loaded {commands_loaded_cnt} custom commands: {', '.join(loaded_commands)}", err=True)


@click.group(cls=CustomCLI)
@click.version_option()
@click.pass_context
def cli(ctx):
    """Main CLI entrypoint with standard context."""
    ctx.ensure_object(dict)
    ctx.obj['start_time'] = datetime.now()


@cli.command(name="hello")
@click.pass_context
def hello(ctx):
    """Common command for CLI."""
    _ = ctx
    click.echo("Hello! I'm working.")


if __name__ == '__main__':
    cli()
