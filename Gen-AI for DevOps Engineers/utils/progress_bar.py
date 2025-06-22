import time
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn


def custom_progress_bar(task_description="Generating Dockerfile..."):
    """Progress bar with custom columns and styling"""
    # print(f"\n{title}")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        expand=True
    ) as progress:
        
        task = progress.add_task(f"{task_description}", total=50)
        
        for i in range(50):
            time.sleep(0.05)  # Simulate work
            progress.update(task, advance=1)


def styled_progress_bar(task_description="Generating Dockerfile..."):
    """Progress bar with custom colors and styling"""    
    with Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[bold green]{task.percentage:>3.0f}%"),
        expand=True
    ) as progress:
        
        task = progress.add_task(f"{task_description}", total=75)
        
        for i in range(75):
            time.sleep(0.03)
            progress.update(task, advance=1)