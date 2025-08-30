#!/usr/bin/env python3

import click
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.generators.text_generator import TextGenerator
from src.core.generators.password_generator import PasswordGenerator
from src.core.generators.apikey_generator import APIKeyGenerator


@click.group()
@click.version_option(version="1.0.0", prog_name="random-toolbox")
def cli():
    """Random Toolbox - A versatile toolkit for developers."""
    pass


@cli.command()
@click.option('--type', 'content_type', 
              type=click.Choice(['word', 'sentence', 'paragraph']),
              default='paragraph',
              help='Type of text to generate')
@click.option('--count', type=int, default=1, 
              help='Number of items to generate')
def text(content_type, count):
    """Generate random text (words, sentences, or paragraphs)."""
    try:
        generator = TextGenerator()
        result = generator.generate(content_type, count)
        
        if isinstance(result, list):
            for item in result:
                click.echo(item)
        else:
            click.echo(result)
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--length', type=int, default=16,
              help='Password length (8-128)')
@click.option('--uppercase/--no-uppercase', default=True,
              help='Include uppercase letters')
@click.option('--lowercase/--no-lowercase', default=True,
              help='Include lowercase letters')
@click.option('--numbers/--no-numbers', default=True,
              help='Include numbers')
@click.option('--symbols/--no-symbols', default=False,
              help='Include symbols')
@click.option('--exclude-ambiguous', is_flag=True,
              help='Exclude ambiguous characters (0, O, l, 1, etc.)')
@click.option('--show-entropy', is_flag=True,
              help='Show entropy and strength information')
def password(length, uppercase, lowercase, numbers, symbols, exclude_ambiguous, show_entropy):
    """Generate secure random passwords."""
    try:
        generator = PasswordGenerator()
        result = generator.generate_password(
            length=length,
            uppercase=uppercase,
            lowercase=lowercase,
            numbers=numbers,
            symbols=symbols,
            exclude_ambiguous=exclude_ambiguous
        )
        
        click.echo(result["password"])
        
        if show_entropy:
            click.echo(f"Length: {result['length']} characters", err=True)
            click.echo(f"Entropy: {result['entropy_bits']} bits", err=True)
            click.echo(f"Strength: {result['strength']}", err=True)
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--format', 'key_format',
              type=click.Choice(['hex', 'base64', 'base58', 'custom']),
              default='hex',
              help='Output format for the API key')
@click.option('--length', type=int, default=32,
              help='Key length in bytes')
@click.option('--prefix', type=str, default='',
              help='Optional prefix for the key')
@click.option('--charset', type=str, default=None,
              help='Custom character set (only for custom format)')
@click.option('--show-entropy', is_flag=True,
              help='Show entropy and security information')
def apikey(key_format, length, prefix, charset, show_entropy):
    """Generate secure API keys."""
    try:
        generator = APIKeyGenerator()
        result = generator.generate(
            key_format=key_format,
            length=length,
            prefix=prefix,
            charset=charset
        )
        
        click.echo(result["api_key"])
        
        if show_entropy:
            click.echo(f"Format: {result['format']}", err=True)
            click.echo(f"Length: {result['total_length']} characters", err=True)
            click.echo(f"Entropy: {result['entropy_bits']} bits", err=True)
            click.echo(f"Security: {result['security_level']}", err=True)
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()