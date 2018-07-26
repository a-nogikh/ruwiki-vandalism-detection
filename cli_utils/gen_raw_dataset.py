import click

def get_command():
    @click.command()
    def gen_raw_dataset():
        pass
    
    return gen_raw_dataset
